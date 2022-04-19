#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Global variables are defined here
"""

import os, json

logging = True
already_voted_path = './already_voted_on.json'
wallet_path = './wallets.txt'


def cond_log(msg):
    '''Prints a message only if logging is switched on.'''
    if logging:
        print(msg)


def read_from_json(wallets, filepath):
    '''
    Returns dict of shape {wallet1: [prop_id_1, prop_id_2,...], wallet2: ...}
    to avoid trying to vote twice for the same proposal with the same wallet.
    Returns dictionary of shape {w1: [], w2: [], ...} if no file detected.
    '''
    if os.path.isfile(filepath):
        with open(filepath, 'r') as jfile:
            data = json.load(jfile)
            return data
    else:
        d = {w: [] for w in wallets}
        cond_log(f'No local wallet history found. Created this instead:\n {d}')
        return d


def load_wallets(wallet_path):
    '''
    Returns a set of wallets read from a text file.
    '''
    with open(wallet_path, 'r') as f:
        wallets = {l.strip() for l in f.readlines()}
    return wallets


wallets = load_wallets(wallet_path)

# load dictionary of proposals to ignore from disk if it exists
ALREADY_VOTED_DICT = read_from_json(wallets, already_voted_path)


