#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
All functions are stored here
"""

import os, json, requests, keyring, csv
#from web3.auto.infura import w3

#eth = w3.eth


logging = True        # toggles verbosity (False = no messages at all)



def load_wallets(wallet_path):
    '''
    Returns a set of wallets read from a text file.
    '''
    with open(wallet_path, 'r') as f:
        wallets = {l.strip() for l in f.readlines()}
    return wallets


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


def set_already_voted_dict(already_voted_path, wallet_path):
    '''
    Reads json containing voting history and returns a dict (past votes
    per wallet). Creates dict with wallets as keys if no json file found.
    '''
    wallets = load_wallets(wallet_path)
    d = read_from_json(wallets, already_voted_path)
    return d


def write_to_json(_dict, path):
    '''
    Writes dict of shape {wallet1: {prop_id_1, prop_id_2,...}, wallet2: ...}
    to json file located in path variable.
    '''
    with open(path, 'w') as jfile:
        json_object = json.dump(_dict, jfile, indent=4)
        cond_log(f'\nFound that these proposals are up for voting:\n {_dict}')


def dict_to_csv(_dict, outpath):
    '''
    Writes a dictionary to a csv file.
    '''
    with open(outpath, 'w') as f:
        w = csv.writer(f)
        for k, v in _dict.items():
            w.writerow([k, v])


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
    cond_log(f'\nFound {len(active_props)} active proposal(s) for: {active_spaces}.')

    return active_props


def remove_voted_on(wallet, proposals, already_voted_dict):
    '''
    Takes a set of proposals. Returns subset of those proposals that
    the wallet has not yet voted on.
    '''

    already_voted = set(already_voted_dict[wallet])
    removed = set(proposals) - already_voted

    return removed


def get_not_yet_voted(wallet, spaces, already_voted_dict):
    '''
    Takes a set of snapshot spaces and returns the set of active proposals
    that this wallet has not yet voted on.
    '''
    # gets active proposals per wallet and removes those already voted on
    to_vote = remove_voted_on(wallet,
                              get_active_proposals(spaces),
                              already_voted_dict
                              )
    cond_log(f'Found the following proposals for {wallet}:\n {to_vote}')
    return to_vote


def get_pk(encr_pk_path, keyr_service_name, keyr_account):

    decr_pw = keyring.get_password(keyr_service_name, keyr_account)

    with open(encr_pk_path) as keyfile:
        enc_k = keyfile.read()
        pk = eth.account.decrypt(enc_k, decr_pw)

    decr_pw = None
    return pk


def connect_web3(url, pk):
    pass


def get_choices(proposal_id):
    '''
    Returns list of choices up for vote for a specific proposal.
    '''
    query_proposal = '''query Proposal {
        proposal(id:"'''+proposal_id+'''") {
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
    d = json_from_query(query_proposal)
    return d['data']['proposal']['choices']



def export_to_vote(wallet_path, already_voted_path, export_path):
    '''
    Wrapper for core functionality. Queries graphql.
    Saves a json file containing all active proposals per wallet that
    the wallet has not yet voted on.
    '''
    
    wallets = load_wallets(wallet_path)
    already_voted_dict = set_already_voted_dict(
            already_voted_path, wallet_path
            )
    
    d = {}

    # query graphql for active proposals per wallet
    for wallet in wallets:
        spaces = get_joined_spaces(wallet)
        d[wallet] = list(get_not_yet_voted(wallet, spaces, already_voted_dict))

    write_to_json(d, export_path)
    cond_log(f'\n...updated {export_path.strip("./")}')



def get_spaces_from_proposals(proposals_list, id_memo={}):
    '''
    Takes list of proposal ids, returns list of unique ids of their respective spaces.
    A dictionary of shape {proposal_str: id_str, ... } can be provided for
    memoization, to avoid querying for the same proposal twice (i.e. with multiple wallets).
    '''
    # helper function, queries graphql to get space id from prop id
    def id_from_prop(proposal_id):
        query_proposal = '''query Proposal {
            proposal(id:"'''+proposal_id+'''") {
                space {
                  name
                }
              }
            }'''
        d = json_from_query(query_proposal)
        return d['data']['proposal']['space']['name']

    ids = set()

    for prop in proposals_list:
        if prop in id_memo:
            ids.add(id_memo[prop])
        else:
            space_id = id_from_prop(prop)
            ids.add(space_id)
            id_memo[prop] = space_id

    # returns tuple (spaces list, updated memo dictionary)
    return list(ids), id_memo


def export_readable_csv(json_path, outpath='./to_vote.csv'):
    '''
    Takes the wallet: proposals dictionary, replaces all proposals
    with the name of their respective spaces and saves as csv file
    '''
    cond_log('...resolving space names for csv file...')

    # read dict from json
    with open(json_path, 'r') as jfile:
        in_dict = json.load(jfile)
    out_dict = {}
    memo_dict = {}

    # query spaces ids from graphql
    for wallet, prop_list in in_dict.items():

        spaces, memo_dict = get_spaces_from_proposals(prop_list, memo_dict)
        out_dict[wallet] = spaces

    # save as csv
    dict_to_csv(out_dict, outpath)
    cond_log(f'...updated {outpath.strip("./")}.')
    
    # print list of spaces with active proposals
    print('\nFound active proposals for these spaces in total:\n')
    unique_spaces = set(memo_dict.values())
    [print(x) for x in unique_spaces]







def vote_yes(wallet, space):
    '''
    Logs into a snapshot space with wallet,
    votes for whichever button contains a "Yes".
    '''
    # connect wallet with snapshot.page

    # return set of joined spaces with active proposals to vote on
    active = get_not_yet_voted(wallet)

    # for each active space: vote yes

    # disconnect wallet from snapshot.page
    pass


def vote_all_with_wallet(wallet):
    '''
    Iterates through spaces this wallet has joined,
    checks which have active proposals,
    votes for whichever button contains a "Yes" on those.
    '''
    active = get_active_spaces(wallet)

    # Pass if no proposals currently for this wallet's joined spaces
    if active == {}:
        cond_log(f'No active proposals atm for wallet {wallet}!')
        return None

    else:
        for space in active:
            vote_yes(wallet, space)




# at the end: Write updated json file back to disk!
