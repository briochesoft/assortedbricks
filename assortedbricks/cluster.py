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

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def kmeans_clusters(input_df, num_clusters, seed=None):
    # Create a DataFrame with the features for clustering
    """
    Perform K-Means clustering on a given DataFrame.

    Parameters
    ----------
    input_df : pandas.DataFrame
        The DataFrame to be clustered. The DataFrame should have a "DesignID" column
        and a "Quantity" column.
    num_clusters : int
        The number of clusters to form.
    seed : int, optional
        The random seed for the clustering algorithm.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the clusters and their corresponding labels and quantities.
    """
    features_df = input_df.iloc[:, 2:]

    # Use the 'quantity' column as sample weights
    sample_weights = input_df['Quantity']

    # Perform K-Means clustering with sample weights
    kmeans = KMeans(n_clusters=num_clusters, random_state=seed)
    kmeans.fit(features_df, sample_weight=sample_weights)

    # K statistics
    inertia = kmeans.inertia_
    silhouette = silhouette_score(features_df, kmeans.labels_, metric='euclidean')
    print(f"WSS (lower is better) = {inertia}, "
          f"sil (closer to 1 is better)= {silhouette}")

    # Assign clusters to each piece
    input_df['cluster'] = kmeans.labels_

    # Get quantity per cluster
    clusters = input_df

    # Remove DesignID column
    clusters = clusters.drop('DesignID', axis=1)

    # Group by "cluster" and sum all the other columns
    columns = list(clusters.columns)
    columns.remove('cluster')
    clusters = clusters.groupby('cluster')[columns].sum().reset_index()

    # Create labels
    clusters['label'] = clusters.apply(lambda x: ', '.join(
        [col for col in clusters.columns[2:] if col != 'Lego' and x[col] == x['Lego']]), axis=1)

    # Print statistics for the quantity of pieces in the clusters
    print(clusters['Quantity'].describe())

    # Set default label to Other
    clusters.loc[clusters['label'] == '', 'label'] = 'Other'

    # Add a column containing all the DesignIDs in the cluster
    clusters['DesignIDs'] = clusters.apply(lambda x: ', '.join(
        [str(design_id) for design_id in
            input_df[input_df['cluster'] == x['cluster']]['DesignID']]), axis=1)

    clusters.Quantity = clusters.Quantity.astype(int)
    clusters = clusters.sort_values(by='Quantity', ascending=True)
    return clusters[['label', 'Quantity', 'DesignIDs']]
