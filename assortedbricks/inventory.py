# Copyright (c) 2025, BriocheSoft
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# SPDX-License-Identifier: MIT

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import re
from pandas import merge, concat, DataFrame
from numpy import where
from .input.input import Input
from .cluster import kmeans_clusters
from .data.database import Database
from .data.brickarchitect import get_image, fetch_part_info


class Inventory():
    def __init__(self):
        """
        Initializes a new Inventory object.

        Returns
        -------
        None
        """
        self.df = None
        self.db = None
        self.clusters = None
        self.input = Input()

    def load(self, input, file):
        """
        Load a file ready to be clustered.

        Parameters
        ----------
        input_file : str
            The path to the input file containing the inventory list.

        Returns
        -------
        None
        """
        # Try to load the input file through all supported formats
        if not self.input.load(input, file):
            raise ValueError("Failed to load input file")

        # Transform the input file to a standard format
        print(f"{str(datetime.now())}: Cleaning inventory...")
        self.input.clean()

        # Open the local database
        self.db = Database()
        self.df = None

        # Use the database to get already existing parts
        print(f"{str(datetime.now())}: Merging with local database...")
        self.merge_with_database(self.input.dataframe())

        # Fetch missing parts
        print(f"{str(datetime.now())}: Fetching missing parts and images...")
        self.fetch_missing_parts()

        # Update missing images (once a day)
        print(f"{str(datetime.now())}: Updating missing images...")
        self.update_images()

        # No need for the database anymore
        self.db.close()

        # Prepare data for clustering using the labels hirarchy
        print(f"{str(datetime.now())}: Creating labels hirarchy...")
        self.create_labels_hirarchy()

        # Clustering has not been performed yet
        self.clusters = None

    def cluster(self, num_clusters, seed=None):
        """
        Clusters the inventory.

        Parameters
        ----------
        num_clusters : int
            The number of clusters to form.
        seed : int, optional
            The random seed for the clustering algorithm.

        Returns
        -------
        None
        """
        print(f"{str(datetime.now())}: Clustering...")
        self.clusters = kmeans_clusters(self.df, num_clusters, seed)

    def as_html(self):
        """
        Generates HTML from the clusters.

        Returns
        -------
        str
            The HTML from the clusters.
        """
        assert self.clusters is not None, "Call cluster() first!"
        print(f"{str(datetime.now())}: Generating HTML...")

        clusters = self.clusters.to_dict('records')

        # Open the output HTML file
        no_category = re.compile(r'^\d+\. ')
        html_string = ''

        self.db = Database()
        # Loop through each cluster
        with ThreadPoolExecutor() as executor:
            for result in executor.map(lambda cluster:
                                       self.__single_cluster_html(cluster, no_category), clusters):
                html_string += ''.join(result)
        self.db.close()

        print(f"{str(datetime.now())}: done")
        return html_string

    def __single_cluster_html(self, cluster, regex):
        """
        Generates HTML for a single cluster.

        Parameters
        ----------
        cluster : dict
            A single cluster with its label and quantity.
        regex : re.Pattern
            A compiled regular expression to remove the category index from the label.

        Returns
        -------
        html : list
            A list of strings representing the HTML for a single cluster.
        """
        html = []
        html.append('<div>\n')
        label = cluster['label']
        # Remove category index
        label = regex.sub('', label)

        quantity = int(cluster['Quantity'])

        # Draw the cluster label and quantity
        html.append('<p style="margin: 10px; font-size: 32px;">'
                    f'{label} ({quantity})</p>\n')

        rows = self.db.get_images_for_cluster(cluster)

        part_images_html = []
        for row in rows:
            image, = row
            if image is not None:
                part_images_html.append(
                    f'<img src="data:image/png;base64,{image}" style="margin: 10px;">\n')
        html = html + part_images_html

        html.append('</div>\n')
        # Add a line break between clusters
        html.append('<br>')
        return html

    def merge_with_database(self, input_df):
        # Read the database
        """
        Reads the database and merges it with the given input DataFrame
        based on DesignID.

        Parameters
        ----------
        input_df : pandas.DataFrame
            The input DataFrame to be merged with the database DataFrame.

        Returns
        -------
        None
        """
        design_ids = ','.join(map(str, input_df['DesignID'].tolist()))
        database_df = self.db.get_labels_dataframe(design_ids)

        # Merge the input and database dataframes based on DesignID
        self.df = merge(input_df, database_df, on='DesignID', how='left')

    def fetch_missing_parts(self):
        # Get a list of DesignID without Labels
        """
        Fetches a list of DesignID without Labels and adds them to the database.

        This function fetches the part information from the BrickArchitect website
        for all the parts in the dataframe without labels. It then adds the
        fetched part information to the database.

        Returns
        -------
        None
        """
        unknown_parts = self.df[self.df['Labels'].isna()]['DesignID'].tolist()
        if len(unknown_parts) > 0:
            print(f"    Fetching {len(unknown_parts)} parts...")
            # Create a new dataframe for the unknown parts
            new_parts_df = DataFrame(columns=['DesignID', 'Labels', 'Image'])
            with ThreadPoolExecutor(max_workers=10) as executor:
                today = datetime.now().strftime('%Y-%m-%d')
                futures = [executor.submit(fetch_part_info, part)
                           for part in unknown_parts]
                for future in futures:
                    part, new_labels, new_image = future.result()
                    # add part to database
                    new_parts_df = concat([new_parts_df,
                                           DataFrame(data={'DesignID': part,
                                                           'Labels': new_labels,
                                                           'Image': new_image, 'Updated': today}, index=[0])])
                    # add new_labels our dataframe
                    self.df.loc[self.df['DesignID'] == part, 'Labels'] = new_labels

            # Save to database
            self.db.append_parts_dataframe(new_parts_df)

    def update_images(self):
        """
        Updates the images for the given parts in the database.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Notes
        -----
        This function will only try to update the image once a day. If the updated date
        is older than today, it will not try to update the image. This is to prevent
        the function from fetching the same image multiple times in a row.
        """
        design_ids = ','.join(map(str, self.df['DesignID'].tolist()))
        rows = self.db.get_missing_images(design_ids)
        for row in rows:
            (part, updated) = row
            fetch_date = datetime.strptime(updated, '%Y-%m-%d').date()
            # We only try to update the image once a day
            if fetch_date < datetime.now().date():
                print(f"Updating image for part {part}")
                new_image = get_image(part)
                self.db.update_image(part, new_image)

    def create_labels_hirarchy(self):
        # Get all unique labels from the "Labels" column in the database
        """
        Creates a new dataframe with columns for each unique label in the "Labels" column.

        The new dataframe will have the same index as the original dataframe and
        will contain the same columns as the original dataframe, plus one column for
        each unique label in the "Labels" column. The value of each label column will
        be 1 if the label is present in the database and 0 otherwise.

        The resulting dataframe will be stored in the `self.df` attribute.
        """

        labels_array = self.df['Labels'].str.split(',')

        labels_len = 0
        all_labels = []
        for subarray in labels_array:
            if labels_len < len(subarray):
                labels_len = len(subarray)
        for i in range(labels_len):
            for subarray in labels_array:
                if i < len(subarray):
                    all_labels.append(subarray[i])
        # Remove duplicates from all_labels
        all_labels = list(dict.fromkeys(all_labels))

        # Create columns for each label keeping the order
        label_df = concat([self.df,
                           DataFrame({label: [0] * len(self.df) for label in all_labels if label})],
                          axis=1)

        # Set the value of each label column to 1 if the label is present in the database
        for label in all_labels:
            if label:
                label_df[label] = where(label_df['Labels'].str.contains(label), 1, 0)

        # Drop the unnecessary Labels column from the output dataframe
        self.df = label_df.drop('Labels', axis=1)

    def get_extensions(self):
        """
        Returns the file extensions supported as input file format.

        Returns
        -------
        str
            The file extensions as a comma-separated string.
        """
        return self.input.extension()
