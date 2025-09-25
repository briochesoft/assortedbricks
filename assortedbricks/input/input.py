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

from .rebrickableset import RebrickableSet
from .rebrickablejson import RebrickableJSON
from .rebrickablecsv import RebrickableCSV
from .brickstorexml import BrickStoreXML
from .ldcadpbg import LDCadPBG
from .inputinterface import InputInterface


class Input(InputInterface):

    def __init__(self):
        self.supported_formats = [RebrickableSet(), RebrickableJSON(), RebrickableCSV(), BrickStoreXML(), LDCadPBG()]
        super().__init__()

    def clean(self):
        """
        Cleans the input to get a DataFrame with two columns: "DesignID" and "Quantity".
        The "DesignID" column contains the part number without any non-numerical characters.
        The "Quantity" column contains the sum of the quantities of each part regardless of color.
        """
        self.input.clean()

    def load(self, input, file):
        """
        Loads an input (set number of file path) into the Input object.

        The input is checked against all supported formats. If the input is supported, the
        Input object is updated with the loaded data.

        Parameters
        ----------
        input : str
            Input to be loaded.

        Returns
        -------
        bool
            True if the input was successfully loaded, False otherwise.
        """
        supported = False
        for supported_format in self.supported_formats:
            try:
                supported_format.load(input, file)
                self.input = supported_format
                supported = True
                break
            except ValueError:
                pass
        return supported

    def dataframe(self):
        """Getter for the df attribute."""
        return self.input.dataframe()

    def extension(self):
        """Getter for the extension attribute."""
        return ','.join(map(lambda x: x.extension(), self.supported_formats))
