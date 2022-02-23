#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Written by Al Matty <almatty@gmail.com>
"""


# set of wallets which will be used for voting
wallets =         # load from txt file (1 wallet per row)
logging = True    # toggles debug messages (False = no messages at all)


# Load dictionary of proposals to ignore from disk if it exists
already_voted_path = './already_voted.json'
ALREADY_VOTED_DICT = read_from_json(wallets, already_voted_path)







def main(wallets):
    '''
    Wrapper for vote_all_with_wallet which cycles through
    all wallets contained in wallets set.
    '''
    global ALREADY_VOTED_DICT

    for wallet in wallets:
        vote_all_with_wallet(wallet)
        # After each successful vote: Add entry (wallet: prop_id) to dict

    cond_log(f'All went well! No errors whatsoever.')







# At the very end: Save updated dictionary of proposals to ignore to disk
write_to_json(ALREADY_VOTED_DICT, already_voted_path)
