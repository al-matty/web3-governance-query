#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Written by Al Matty <almatty@gmail.com>
"""

from functions import *


logging = True    # toggles verbosity (False = no messages at all)

# file paths
wallet_path = './wallets.txt'                # text file, 1 wallet per row
already_voted_path = './already_voted.json'  # path to voting history (not strictly necessary)
export_json_path = './to_vote.json'
encr_pk_path = '../encrPK.json'



# load set of wallets used for voting
wallets = load_wallets(wallet_path)    # creates set of wallets

# load dictionary of proposals to ignore from disk if it exists
ALREADY_VOTED_DICT = read_from_json(wallets, already_voted_path)





export_to_vote(wallets, export_json_path)
cond_log(f'All went well! No errors whatsoever.')







# At the very end: Save updated dictionary of proposals to ignore to disk
#write_to_json(ALREADY_VOTED_DICT, already_voted_path)
