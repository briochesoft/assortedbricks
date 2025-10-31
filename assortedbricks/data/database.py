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
from datetime import datetime
from pandas import read_sql_query
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import select, update

DATABASE_PATH = "./datastore/brickarchitect.sqlite"
engine = create_engine(f"sqlite+pysqlite:///{DATABASE_PATH}")
metadata_obj = MetaData()
parts = Table(
    "parts",
    metadata_obj,
    Column("index", Integer, primary_key=True),
    Column("DesignID", Integer, unique=True, nullable=False),
    Column("Labels", String, nullable=False),
    Column("Image", String, nullable=True),
    Column("Updated", String, nullable=False),
)


class Database:

    def __init__(self):
        """
        Initializes a new Database object.

        Creates a connection to the database file at "data/brickarchitect.sqlite" and
        creates a table named "parts" if it doesn't exist. The table has five columns: "index",
        "DesignID", "Labels", "Image", and "Updated". The "index" column is the primary
        key and is used to uniquely identify each row in the table. The "DesignID" column
        is a unique identifier for each part. The "Labels" column contains the labels for
        each part. The "Image" column contains the image data for each part. The "Updated"
        column contains the date and time when the part was last updated in the database.

        :return: None
        """
        # create the directory if it doesn't exist
        if not os.path.exists(os.path.dirname(DATABASE_PATH)):
            os.makedirs(os.path.dirname(DATABASE_PATH))
        metadata_obj.create_all(engine)

    def __del__(self):
        """
        Commits all pending transactions and closes the database connection.

        This should be called when the database is no longer needed to prevent
        memory leaks.
        """
        with engine.connect() as conn:
            conn.commit()

    def commit(self):
        """
        Commits all pending transactions.
        """
        with engine.connect() as conn:
            conn.commit()

    def fetch_part_image(self, design_id):
        """
        Fetches the image for the given design ID from the database.

        Parameters
        ----------
        design_id : int
            The design ID to fetch the image for.

        Returns
        -------
        str
            The base64 encoded image data.
        """
        with engine.connect() as conn:
            return conn.execute(select(parts.c.Image).filter(parts.c.DesignID == design_id)).first()

    def get_labels_dataframe(self, design_ids):
        """
        Extracts the design IDs and their corresponding labels from the database for
        the given design IDs.

        Parameters
        ----------
        design_ids : str
            A comma-separated string of design IDs to fetch the labels for.

        Returns
        -------
        pandas.DataFrame
            A DataFrame containing the design IDs and their corresponding labels.
        """
        stmt = select(parts.c.DesignID, parts.c.Labels).filter(parts.c.DesignID.in_(design_ids.split(',')))
        with engine.connect() as conn:
            return read_sql_query(stmt, conn)

    def append_parts_dataframe(self, parts_df):
        """
        Appends the given parts DataFrame to the "parts" table in the database.

        Parameters
        ----------
        parts_df : pandas.DataFrame
            The DataFrame containing the parts to be appended to the database.

        Returns
        -------
        None
        """
        with engine.begin() as conn:
            parts_df.to_sql("parts", conn, if_exists="append", index=False)

    def get_missing_images(self, design_ids):
        """
        Fetches all the missing images for the given design IDs.

        Parameters
        ----------
        design_ids : str
            A comma-separated string of design IDs to fetch the missing images for.

        Returns
        -------
        list
            A list of tuples containing the design ID and the last updated date
            for each part that is missing an image.
        """

        with engine.connect() as conn:
            return conn.execute(select(parts.c.DesignID, parts.c.Updated)
                    .filter(parts.c.DesignID.in_(design_ids.split(',')), parts.c.Image.is_(None))).all()

    def update_image(self, design_id, image):
        """
        Updates the image for the given design ID.

        Parameters
        ----------
        design_id : int
            The design ID to update the image for.
        image : str
            The base64 encoded image data.

        Returns
        -------
        None
        """
        today = datetime.now().strftime('%Y-%m-%d')
        with engine.connect() as conn:
            conn.execute(update(parts).where(parts.c.DesignID == design_id).values(Image=image, Updated=today))

    def get_images_for_cluster(self, cluster):
        """
        Fetches all the images for the given cluster.

        Parameters
        ----------
        cluster : dict
            A dictionary containing the cluster information with the following keys:
            - DesignIDs: A list of design IDs in the cluster

        Returns
        -------
        list
            A list of tuples containing the image data for each part in the cluster.
        """
        with engine.connect() as conn:
            return conn.execute(select(parts.c.Image).filter(parts.c.DesignID.in_(cluster['DesignIDs'].split(", ")))
                    .order_by(parts.c.DesignID)).fetchall()
