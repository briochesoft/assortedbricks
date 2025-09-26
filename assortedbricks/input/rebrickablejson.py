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

import json
from pandas import json_normalize
from .inputinterface import InputInterface


class RebrickableJSON(InputInterface):
    magic = '{"count":'

    def load(self, _, file_path):
        """
        This function loads a Rebrickable JSON from a from the given file_path.

        Parameters
        ----------
        input : str
            The set number to load.

        Returns
        -------
        None
        """
        # Check if the file is a Rebrickable JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.read(len(RebrickableJSON.magic))
            if not first_line.startswith(RebrickableJSON.magic):
                raise ValueError('Invalid Rebrickable JSON file, '
                                 f'first line should be "{RebrickableJSON.magic}"')

        with open(file_path, 'r', encoding='utf-8') as f:
            # Read the JSON file
            data = json.load(f)

        self.df = json_normalize(data, 'results')

    def clean(self):
        """
        This function handles a Rebrickable JSON file before being used for clustering.

        The output is a pandas DataFrame with two columns: "DesignID" and "Quantity".
        The "DesignID" column contains the part number without any non-numerical characters.
        The "Quantity" column contains the sum of the quantities of each part regardless of color.

        Returns
        -------
        None
        """
        # Select only the "Part" and "Quantity" columns
        self.df = self.df[['part.part_num', 'quantity']]
        # Rename Part to DesignID
        self.df = self.df.rename(columns={'part.part_num': 'DesignID'})
        self.df = self.df.rename(columns={'quantity': 'Quantity'})
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
        Returns the file extension for a Rebrickable JSON file.

        Returns
        -------
        str
            The file extension for a Rebrickable file, which is ".json".
        """
        return ".json"
