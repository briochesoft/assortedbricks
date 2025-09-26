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

import os
import json
import requests
from .inputinterface import InputInterface
from ..data.config import get_rebrickable_key


class RebrickableSet(InputInterface):
    magic = '{'

    def load(self, input, file):
        """
        This function loads a Rebrickable JSON from a set number.

        Parameters
        ----------
        input : str
            The set number to load.

        Returns
        -------
        None
        """
        key = get_rebrickable_key()
        if key is None:
            raise ValueError('No Rebrickable key not found')

        if input is None or len(input) < 4:
            raise ValueError('Not a valid set number')

        if '-' not in str(input):
            input = f"{input}-1"

        data = ""
        try:
            headers = {
                'Authorization': f'key {key}',
                'Content-Type': 'application/json'
            }
            url = f"https://rebrickable.com/api/v3/lego/sets/{input}/parts/"
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise ValueError('Not a valid set number')
            data = json.loads(response.content.decode('utf-8'))
        except requests.exceptions.HTTPError:
            raise ValueError('HTTP Error')

        # Create directroy if it doesn't exist
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))
        with open(file, 'w') as f:
            json.dump(data, f)

        # We raise ValueError so RebrickableJSON can load the file afterwards
        raise ValueError('File loaded, use RebrickableJSON')
