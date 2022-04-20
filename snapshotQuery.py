#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Written by Al Matty <almatty@gmail.com>
"""

from functions import *
from time import sleep

# file paths
wallet_path = './wallets.txt'                # text file, 1 wallet per row
already_voted_path = './already_voted.json'  # path to voting history (not strictly necessary)
export_json_path = './to_vote.json'
export_csv_path = './to_vote.csv'
encr_pk_path = '../encrPK.json'



# run script and export proposals up for voting per wallet
export_to_vote(wallet_path, already_voted_path, export_json_path)

# create csv file with names of snapshot spaces resolved (optional)
sleep(1)
export_readable_csv(export_json_path, export_csv_path)

