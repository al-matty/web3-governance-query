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
choices_json_path = './choices.json'


# run script and export proposals up for voting per wallet
#export_to_vote(wallet_path, already_voted_path, export_json_path)

# if there are proposals to vote on, create a json with its most popular choice
sleep(1)
create_choices_json(export_json_path, choices_json_path)

# filter out proposals with much less engagement than usual
sleep(1)
filter_out_low_engagement_props(choices_json_path)

# filter_out_bot_catcher_proposals(choices_json_path, export_json_path)
sleep(1)
triggers = ['bot', 'sybil', 'human', 'Do not vote', 'Don\'t vote']
filter_out_bot_catcher_proposals(choices_json_path, triggers)

# change choice values to work with weighted votes
sleep(1)
enable_weighted_vote(choices_json_path)

# create csv file with names of snapshot spaces resolved (optional)
sleep(1)
export_readable_csv(export_json_path, export_csv_path)
