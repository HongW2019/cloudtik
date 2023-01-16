#!/bin/bash

# download Criteo Terabyte dataset
# the dataset contains 24 zipped files and requires about 1 TB storage for the data and another 2 TB for immediate results

curl -O -C - https://storage.googleapis.com/criteo-cail-datasets/day_{$(seq -s "," 0 23)}.gz
yes n | gunzip day_{0..23}.gz
