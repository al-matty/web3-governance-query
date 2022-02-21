#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
All functions are stored here
"""

import os, json, requests


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



def write_to_json(_dict, path):
    '''
    Writes dict of shape {wallet1: {prop_id_1, prop_id_2,...}, wallet2: ...}
    to json file located in path variable.
    '''
    with open(path, 'w') as jfile:
        json_object = json.dump(_dict, jfile, indent=4)
        cond_log(f'Saved wallet history to file:\n {_dict}')


def cond_log(msg):
    '''Prints a message only if logging is switched on.'''
    if logging:
        print(msg)


def json_from_query(query):
    '''Returns the response of the graphql query as dictionary'''
    url = 'https://hub.snapshot.org/graphql'
    r = requests.post(url, json={'query': query})
    response_str = r.text
    return json.loads(response_str)


def get_joined_spaces(wallet):
    '''Returns the set of snapshot spaces this wallet is following'''

    # query graphql
    query_follows = '''query {
        follows(
            first: 300,
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

    # extract followed spaces from response
    id_set = set()
    d = json_from_query(query_follows)

    for ele in d['data']['follows']:
        id_set.add(ele['space']['id'])

    return id_set


def get_active_proposals(spaces_set):
    '''
    Returns the set of active proposals for each space in given set.
    '''
    # Convert spaces set to graphql-compatible string
    spaces_str = str(list(spaces_set)).replace("'",'"')

    # Get all active proposals for these spaces
    query_active = '''query Proposals {
        proposals (
            first: 50,
            skip: 0,
            where: {
              space_in: '''+spaces_str+''',
              state: "active"
            },
            orderBy: "created",
            orderDirection: desc
        ) {
            id
            title
            body
            choices
            start
            end
            snapshot
            state
            author
            space {
              id
              name
            }
          }
    }'''
    d = json_from_query(query_active)

    # Create set of all active proposal id's of those spaces
    active_props = {x['id'] for x in d['data']['proposals']}
    active_spaces = {x['space']['id'] for x in d['data']['proposals']}
    cond_log(f'Found {len(active_props)} active proposal(s) for: {active_spaces}.')

    return active_props


def remove_voted_on(wallet, proposals):
    '''
    Takes a set of proposals. Returns subset of those proposals that
    the wallet has not yet voted on.
    '''
    global ALREADY_VOTED_DICT

    already_voted = set(ALREADY_VOTED_DICT[wallet])
    removed = set(proposals) - already_voted

    return removed


def get_not_yet_voted(wallet, spaces):
    '''
    Takes a set of snapshot spaces and returns the set of active proposals
    that this wallet has not yet voted on.
    '''
    # gets active proposals per wallet and removes those already voted on
    to_vote = remove_voted_on(wallet, get_active_proposals(spaces))
    cond_log(f'Found the following proposals for {wallet}:\n {to_vote}')
    return to_vote
