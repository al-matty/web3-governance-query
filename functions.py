#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
All functions are stored here
"""
import json
import requests

def read_from_json(path):
    '''
    Returns dict of shape {wallet1: {prop_id_1, prop_id_2,...}, wallet2: ...}
    to avoid trying to vote twice for the same proposal with the same wallet.
    '''
    with open(path, 'r') as jfile:
        data = json.load(jfile)
        return data


def write_to_json(_dict, path):
    '''
    Writes dict of shape {wallet1: {prop_id_1, prop_id_2,...}, wallet2: ...}
    to json file located in path variable.
    '''
    with open(path, 'w') as jfile:
        json_object = json.dump(_dict, jfile, indent=4)


def cond_log(msg):
    '''Prints a message only if logging is switched on.'''
    if logging:
        print(msg)


def get_joined_spaces(wallet):
    '''Returns the set of snapshot spaces this wallet has joined'''

    # query graphql
    query_follows = '''query {
        follows(
            first: 100,
            where: {
              follower: "'''+str(wallet)+'''"
            }
        ) {
        follower
        space {
          id
        }
        created
        }
    }
    '''
    url = 'https://hub.snapshot.org/graphql'
    r = requests.post(url, json={'query': query_follows})

    # extract followed spaces from response
    id_set = set()
    response_str = r.text
    d = json.loads(response_str)

    for ele in d['data']['follows']:
        id_set.add(ele['space']['id'])

    return id_set
