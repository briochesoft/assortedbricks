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
from flask import Flask, request, render_template_string
from numpy.random import default_rng
from socket import gethostname
from .inventory import Inventory
from .data.config import get_rebrickable_key


class WebPage:
    # Define the HTML template
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Assorted Bricks</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                overflow: hidden;
            }
            #header {
                background-color: #f0f0f0;
                padding: 20px;
                border-bottom: 1px solid #ccc;
                position: fixed;
                top: 0;
                width: 100%;
                z-index: 1;
            }
            #header input[type="file"] {
                margin-right: 10px;
            }
            #header input[type="number"] {
                width: 50px;
            }
            #header button {
                margin-left: 10px;
            }
            #result {
                padding: 20px;
                margin-top: 80px;
                width: calc((100vw - 40px)/0.4);
                height: calc((100vh - 100px)/0.4);
                overflow-y: auto;
                transform: scale(0.4);
                transform-origin: top left;
            }
            .waiting {
                animation: waiting 1s ease-in-out infinite;
            }
            @keyframes waiting {
                0% {
                    transform: rotate(0deg);
                }
                100% {
                    transform: rotate(360deg);
                }
            }
            @media print {
                #header, h2 {
                    display: none;
                }
                #result{
                    display: block;
                    width: auto;
                    height: auto;
                    overflow: visible;
                    transform: scale(1);
                }
            }
            .wrapper {
                display: grid;
                max-width: 960px;
                gap: 6px;
                align-content: space-between;
                align-items: center;
                {% if key %}
                grid-template-areas:
                    "x a b e g h j"
                    "x c d f g i j";
                {% else %}
                grid-template-areas:
                    "x c d e g h j"
                    "x c d f g i j";
                {% endif %}
            }
            .item-title { grid-area: x; justify-self: start;}
            {% if key %}
            .item-l-set { grid-area: a; justify-self: end;}
            .item-i-set { grid-area: b; justify-self: start;}
            {% endif %}
            .item-l-list { grid-area: c; justify-self: end;}
            .item-i-list { grid-area: d; justify-self: start;}
            .item-l-num { grid-area: e; justify-self: center;}
            .item-i-num { grid-area: f; justify-self: center;}
            .item-l-seed { grid-area: g; grid-row: 1 / 3; justify-self: end;}
            .item-i-seed { grid-area: h; justify-self: start;}
            .item-t-seed { grid-area: i; justify-self: start;}
            .item-button { grid-area: j; grid-row: 1 / 3; justify-self: start; width: 240px;}
        </style>
    </head>
    <body>
        <div id="header">
            <form action="" method="post" enctype="multipart/form-data">
                <div class="wrapper">
                    <div class="item-title"><strong>Assorted Bricks</strong></div>
                    {% if key %}
                    <div class="item-l-set"><label for="set-number">Set number:</label></div>
                    <div class="item-i-set"><input type="text" name="set-number" style="width: 80px;"></div>
                    {% endif %}
                    <div class="item-l-list"><label for="part-list">Part List:</label></div>
                    <div class="item-i-list"><input type="file" name="part-list" accept="{{ extensions }}"></div>
                    <div class="item-l-num"><label for="num-clusters">Clusters:</label></div>
                    <div class="item-i-num">
                        <input type="number" name="num-clusters" value="{{ num_clusters }}" style="width: 40px;">
                    </div>
                    <div class="item-l-seed"><label for="seed">Seed:</label></div>
                    <div class="item-i-seed">
                        <input type="number" name="seed" value="" min="0" max="4294967295" style="width: 90px;">
                    </div>
                    <div class="item-t-seed"><label for="current-seed">{{ seed }}</label></div>
                    <div class="item-button"><button
                        type="submit"
                        onclick="document.querySelector('#header button').classList.add('waiting');"
                    >Generate Clusters</button></div>
                </div>
            </form>
        </div>
        {% if result %}
            <div id="result"
                    onload="document.querySelector('#header button').classList.remove('waiting');">
                    <h2>{{ num_clusters }} clusters</h2>
                    {% autoescape false %}
                        {{ result }}
                    {% endautoescape %}
                </div>
            </div>
        {% endif %}
    </body>
    </html>
    """
    num_clusters = 10
    seed = 0
    file_path = './temp/uploaded_file'

    def __init__(self, flask_app):
        self.app = flask_app
        self.register_routes()
        # Remove temporpary file
        if os.path.exists(WebPage.file_path):
            os.remove(WebPage.file_path)

    def register_routes(self):
        """
        Registers the routes for the web server.

        The main route is at '/' and accepts both GET and POST requests.
        """
        @self.app.route('/', methods=['GET', 'POST'])
        def index():
            """
            Handles both GET and POST requests to the main route.

            If the request is a POST, it expects the following form data:

            - 'part-list': a CSV file containing the part list
            - 'num-clusters': the number of clusters to form
            - 'seed': the random seed for the clustering algorithm

            If the request is a GET, it will render the HTML template with the default values for
            num_clusters and seed.

            :return: str
                The rendered HTML template as a string.
            """
            inventory = Inventory()
            extensions = inventory.get_extensions()
            key = get_rebrickable_key() is not None
            if request.method == 'POST':
                file = request.files['part-list']
                try:
                    set = request.form['set-number']
                except KeyError:
                    set = None
                WebPage.num_clusters = int(request.form['num-clusters'])
                try:
                    WebPage.seed = int(request.form['seed'])
                    print(f"seed {WebPage.seed}")
                except ValueError:
                    rng = default_rng()
                    WebPage.seed = rng.integers(low=0, high=2**32-1, size=1)[0]
                if file:
                    # create the directory if it doesn't exist
                    if not os.path.exists(os.path.dirname(WebPage.file_path)):
                        os.makedirs(os.path.dirname(WebPage.file_path))
                    file.save(WebPage.file_path)
                try:
                    inventory.load(set, WebPage.file_path)
                    inventory.cluster(WebPage.num_clusters, seed=WebPage.seed)
                    result = inventory.as_html()
                    return render_template_string(WebPage.template,
                                                  result=result,
                                                  num_clusters=WebPage.num_clusters,
                                                  seed=WebPage.seed,
                                                  extensions=extensions,
                                                  key=key)
                except ValueError as e:
                    print(e)
                    pass
            return render_template_string(WebPage.template,
                                          result=None,
                                          num_clusters=WebPage.num_clusters,
                                          seed=WebPage.seed,
                                          extensions=extensions,
                                          key=key)

    def run(self):
        """
        Starts the Flask web server.

        :return: None
        """
        if 'liveconsole' not in gethostname():
            self.app.run(host="0.0.0.0", debug=False)


def main():
    """
    Start up the Flask web server. And run the web page.

    :return: None
    """
    app = Flask(__name__)
    web_page = WebPage(app)
    web_page.run()


if __name__ == '__main__':
    main()
