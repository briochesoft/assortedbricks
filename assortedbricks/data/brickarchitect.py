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

from base64 import b64encode
import requests
from bs4 import BeautifulSoup


# Function to get labels from html page
def get_labels(partid):
    """
    Fetches labels from the provided part ID.

    Parameters
    ----------
    partid : str
        The part ID to fetch labels for.

    Returns
    -------
    tuple
        A tuple containing the new part ID and the labels.
    """

    new_part = partid
    labels = 'Lego'
    try:
        url = f"https://brickarchitect.com/parts/{partid}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        labels_div = soup.find('div', class_='chapternav')
        labels_a = [a.text for a in labels_div.find_all('a')]
        if len(labels_a) > 0:
            if labels_a[0] == 'The LEGO Parts Guide':
                labels_a[0] = 'Lego'
            labels = ','.join(labels_a)
            new_part = response.url.split('/')[-1]
    except requests.exceptions.HTTPError:
        print(f"Failed to fetch labels for part ID {partid}")
    except AttributeError as e:
        print(e)
        print(f"Failed to read labels for part ID {partid}")
    return (new_part, labels)


def get_image(partid):
    """
    Fetches the part image from the provided URL.

    Parameters
    ----------
    partid : str
        The part ID to fetch the image for.

    Returns
    -------
    str
        The image data encoded in base64.
    """
    image = None
    try:
        # Fetch the part image from the provided URL
        url = f"https://brickarchitect.com/content/parts/{partid}.png"
        response = requests.get(url)
        response.raise_for_status()
        image = b64encode(response.content).decode('utf-8')
    except requests.exceptions.HTTPError:
        print(f"Failed to fetch part image for part ID {partid}")

    # Get the image data
    return image


def fetch_part_info(partid):
    """
    Fetches part information from the BrickArchitect website.

    Parameters
    ----------
    partid : str
        The part ID to fetch information for.

    Returns
    -------
    tuple
        A tuple containing the original part ID, the new labels, and the new image data.
    """

    (new_partid, new_labels) = get_labels(partid)
    new_image = get_image(new_partid)
    return partid, new_labels, new_image
