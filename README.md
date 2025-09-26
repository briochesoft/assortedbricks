# Assorted Bricks

## Introduction

This project came as a personal need to store away my Lego sets and still be able to easily built them back.

I needed a way to group pieces together by sorts and still manage the number of groups.

I found [brickarchitect](https://brickarchitect.com/), and it provided the perfect hierarchy I was looking for. I also discovered clustering and the KMeans algorithm for grouping elements.

## Installation

```
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

## Usage

```
source .env/bin/activate
./run-assortedbrick
```

Then connect to ```http://localhost:5000``` 

Give a set number or choose an inventory file, the number of clusters to generate and optionnaly a seed for the clustering algorithm.

The set number input is only available is a Rebrickable API key has been configured in the ``config.yaml`` file:

``
rebrickable-key: "KEY"
``

Supported file formats are:
 - Rebrickable CSV
 - Brickstore XML
 - LDCad PBG

## Acknowledgement

Special thanks to [brickarchitect](https://brickarchitect.com/) for the excellent data.