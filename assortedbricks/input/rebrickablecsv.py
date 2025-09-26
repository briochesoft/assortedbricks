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

from pandas import read_csv
from .inputinterface import InputInterface


class RebrickableCSV(InputInterface):
    magic = "Part,Color,Quantity"

    def load(self, _, file_path):
        """
        This function loads a Rebrickable file from the given file_path.

        Parameters
        ----------
        file_path : str
            The path to the CSV file to be read.

        Returns
        -------
        None
        """
        # Check if the file is a Rebrickable CSV file
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.read(len(RebrickableCSV.magic))
            if not first_line.startswith(RebrickableCSV.magic):
                raise ValueError('Invalid Rebrickable CSV file, '
                                 f'first line should be "{RebrickableCSV.magic}"')

        # Read the CSV file
        self.df = read_csv(file_path)

    def clean(self):
        """
        This function handles a Rebrickable CSV file before being used for clustering.

        The output is a pandas DataFrame with two columns: "DesignID" and "Quantity".
        The "DesignID" column contains the part number without any non-numerical characters.
        The "Quantity" column contains the sum of the quantities of each part regardless of color.

        Returns
        -------
        None
        """
        # Select only the "Part" and "Quantity" columns
        self.df = self.df[['Part', 'Quantity']]
        # Rename Part to DesignID
        self.df = self.df.rename(columns={'Part': 'DesignID'})
        # Only keep the first digits from the DesignID
        self.df['DesignID'] = self.df['DesignID'].str.extract(r'^(\d+)')[0]

        # Group by "DesignID" and sum the "Quantity"
        self.df = self.df.groupby('DesignID')['Quantity'].sum().reset_index()

        # Sort the dataframe by "DesignID" in ascending numerical order
        self.df.DesignID = self.df.DesignID.astype(int)
        self.df.Quantity = self.df.Quantity.astype(int)
        self.df = self.df.sort_values(by='DesignID', ascending=True)

    def extension(self):
        """
        Returns the file extension for a Rebrickable file.

        Returns
        -------
        str
            The file extension for a Rebrickable file, which is ".csv".
        """
        return ".csv"
