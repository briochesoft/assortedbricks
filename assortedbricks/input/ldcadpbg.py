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

import re
from pandas import DataFrame, concat
from .inputinterface import InputInterface


class LDCadPBG(InputInterface):
    magic = "[options]"

    def load(self, _, file_path):
        """
        This function loads a LDCad file from the given file_path.

        Parameters
        ----------
        file_path : str
            The path to the pbg file to be read.

        Returns
        -------
        None
        """
        # Check if the file is a Rebrickable CSV file
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.read(len(LDCadPBG.magic))
            if not first_line.startswith(LDCadPBG.magic):
                raise ValueError('Invalid LDCad file, '
                                 f'first line should be "{LDCadPBG.magic}"')

        # Read the CSV file
        with open(file_path, 'r', encoding='utf-8') as f:
            # Inventory start after the line "<items>"
            line = f.readline()
            while not line.startswith("<items>"):
                line = f.readline()

            # Extract part and quantity for each line
            line_regex = re.compile(r'^([^\.]*)\.dat.*\[color=(\d+)\] \[count=(\d+)\]$')
            for line in f.readlines():
                match = line_regex.match(line)
                if match:
                    part = match.group(1)
                    color = match.group(2)
                    quantity = match.group(3)
                    if self.df is None:
                        self.df = DataFrame(data={'DesignID': part, 'Color': color, 'Quantity': quantity},
                                            index=[0])
                    else:
                        self.df = concat([self.df,
                                          DataFrame(data={'DesignID': part, 'Color': color, 'Quantity': quantity},
                                                    index=[0])])

    def clean(self):
        """
        This function handles a LDCad file before being used for clustering.

        The output is a pandas DataFrame with two columns: "DesignID" and "Quantity".
        The "DesignID" column contains the part number without any non-numerical characters.
        The "Quantity" column contains the sum of the quantities of each part regardless of color.

        Returns
        -------
        None
        """
        # Select only the "Part" and "Quantity" columns
        self.df = self.df[['DesignID', 'Quantity']]
        self.df.Quantity = self.df.Quantity.astype(int)

        # Only keep the first digits from the DesignID
        self.df['DesignID'] = self.df['DesignID'].str.extract(r'^(\d+)')[0]

        # Group by "DesignID" and sum the "Quantity"
        self.df = self.df.groupby('DesignID')['Quantity'].sum().reset_index()

        # Sort the dataframe by "DesignID" in ascending numerical order
        self.df.DesignID = self.df.DesignID.astype(int)
        self.df = self.df.sort_values(by='DesignID', ascending=True)

    def extension(self):
        """
        Returns the file extension for a LDCad file.

        Returns
        -------
        str
            The file extension for a LDCad file, which is ".pbg".
        """
        return ".pbg"
