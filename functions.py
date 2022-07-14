#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
All functions are stored here
"""

import os, json, requests, keyring, csv, random
from time import sleep
from copy import deepcopy


logging = True        # toggles verbosity (False = no messages at all)
IGNORE_LIST = [       # proposals to forever ignore
        'Qmdpr5nfFdHVsMQskUaEX8TqT54PrAUvFFvuwft7zc9pHU'
        ]


def load_wallets(wallet_path):
    '''
    Returns a set of wallets read from a text file.
    '''
    with open(wallet_path, 'r') as f:
        wallets = {l.strip() for l in f.readlines()}
    return wallets


def create_voted_on_json(wallet_path, already_voted_path):
    '''
    Will be executed if no already_voted.json is found.
    Queries graphql for active proposals. Creates a dict (wallets as keys)
    containing all active proposals that the wallets have voted on already.
    Writes dict to json file, to be used as an ignore list.
    '''
    # get active proposals for all wallets -> dict active_props
    active_props = {}
    wallets = load_wallets(wallet_path)
    dummy_d = {k: [] for k in wallets}
    for wallet in wallets:
        spaces = get_joined_spaces(wallet)
        active_props[wallet] = list(get_not_yet_voted(
                wallet, spaces, dummy_d, silent=True)
                )

    # collect proposals already voted on in already_voted dict
    already_voted_d = {}

    for wallet, props in active_props.items():
        props_per_wallet = []
        for prop in props:
            if already_voted(wallet, prop):
                props_per_wallet.append(prop)
        already_voted_d[wallet] = props_per_wallet

    # export as json file
    write_to_json(already_voted_d, already_voted_path)

    cond_log(f'\nCreated a new {already_voted_path.strip("./")}.')


def read_from_json(json_path):
    '''
    Reads json, returns dict with contents of json file
    '''
    with open(json_path, 'r') as jfile:
        data = json.load(jfile)
        return data


def set_already_voted_dict(already_voted_path, wallet_path):
    '''
    Reads json containing voting history and returns a dict (past votes
    per wallet).
    '''
    wallets = load_wallets(wallet_path)

    # read data from json if it exists
    if os.path.isfile(already_voted_path):
        with open(already_voted_path, 'r') as jfile:
            data = json.load(jfile)
            return data

    # create json if it doesn't exist and repeat
    else:
        print(f'Couldn\'t find {already_voted_path}. Trying to create it...')
        create_voted_on_json(wallet_path, already_voted_path)
        sleep(1)
        data = set_already_voted_dict(already_voted_path, wallet_path)
        return data


def write_to_json(_dict, path):
    '''
    Writes dict of shape {wallet1: {prop_id_1, prop_id_2,...}, wallet2: ...}
    to json file located in path variable.
    '''
    with open(path, 'w') as jfile:
        json_object = json.dump(_dict, jfile, indent=4)


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


def already_voted(wallet, proposal):
    '''
    Queries snapshot, returns True if wallet has voted on proposal already,
    returns False if not.
    '''

    query = '''query Votes {
        votes (
            first: 3000
            skip: 0
            where: {
              proposal: "'''+str(proposal)+'''"
              voter: "'''+str(wallet)+'''"
            }
        orderBy: "created",
        orderDirection: desc
        ) {
        id
        voter
        created
        proposal {
          id
        }
        choice
        space {
          id
        }
        }
    }'''

    # query graphql
    already_voted = json_from_query(query)

    # if graphql response is empty list, wallet is not among past voters
    if already_voted['data']['votes'] != []:
        return True
    else:
        return False


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


def get_active_proposals(spaces_set, silent=False):
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

    return active_props


def remove_voted_on(wallet, proposals, already_voted_dict):
    '''
    Takes a set of proposals. Returns subset of those proposals that
    the wallet has not yet voted on.
    '''

    if already_voted_dict == None:
        removed = proposals
    else:
        already_voted = set(already_voted_dict[wallet])
        removed = set(proposals) - already_voted

    return removed


def add_diversity(prop_dict, probability=0.3):
    '''
    Takes a dict of shape {key1: list, key2: list,..}.
    Removes a random element from each list with a {probability}
    and returns resulting dict and a dict of what's been removed.
    '''
    d = prop_dict
    out_d = d.copy()
    removed = {}

    for k,v in d.items():
        if random.random() <= probability and v != []:
            choice = random.choice(v)
            v.remove(choice)
            out_d[k] = v
            removed[k] = choice

    return out_d, removed


def get_not_yet_voted(wallet, spaces, already_voted_dict, silent=False):
    '''
    Takes a set of snapshot spaces and returns the set of active proposals
    that this wallet has not yet voted on.
    '''
    global IGNORE_LIST

    # gets active proposals per wallet and removes those already voted on
    to_vote = remove_voted_on(wallet,
                              get_active_proposals(spaces, silent=silent),
                              already_voted_dict
                              )
    # subtract proposals from ignore list
    to_vote = to_vote - set(IGNORE_LIST)

    # randomly remove proposals from addresses to add variety between wallets


    if not silent and to_vote != set():
        cond_log(f'\n===> Found new proposals for {wallet}:\n')
        [cond_log(x) for x in to_vote]
        cond_log('')

    return to_vote


def get_pk(encr_pk_path, keyr_service_name, keyr_account):

    decr_pw = keyring.get_password(keyr_service_name, keyr_account)

    with open(encr_pk_path) as keyfile:
        enc_k = keyfile.read()
        pk = eth.account.decrypt(enc_k, decr_pw)

    decr_pw = None
    return pk


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


def export_to_vote(wallet_path, already_voted_path, export_path, export=True):
    '''
    Wrapper for core functionality. Queries graphql.
    Saves a json file containing all active proposals per wallet that
    the wallet has not yet voted on.
    '''
    cond_log('Loading wallets and voting history...')
    wallets = load_wallets(wallet_path)
    already_voted_dict = set_already_voted_dict(
            already_voted_path, wallet_path
            )

    d = {}

    # query graphql for active proposals per wallet
    cond_log('Querying graphql...')
    for wallet in wallets:
        spaces = get_joined_spaces(wallet)
        d[wallet] = list(get_not_yet_voted(wallet, spaces, already_voted_dict))

    #randomly discard some proposals per wallet to add variety btw wallets
    d, removed = add_diversity(d, probability=0.3)
    if removed != {}:
        cond_log('\nRandomly removed these proposals for diversity\n:')
        for wallet, prop in removed.items():
            title = get_prop_data(prop)[prop]['title']
            cond_log(f'{wallet}:')
            cond_log(f'\t{title}\n')
    else:
        cond_log('\nNo random removal of proposals for diversity this time!\n')

    if export:
        write_to_json(d, export_path)
        cond_log(f'\n...updated {export_path.strip("./")}')

    return d


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
    unique_spaces = set(memo_dict.values())
    if unique_spaces == set():
        print('\nNo new proposals to vote on today!\n')
    else:
        print('\nFound active proposals for these spaces in total:\n')
        [print(x) for x in unique_spaces]


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


def quadratic_voting_get_most_popular(single_vote_dict, all_poss_choices):
    '''
    Converts a dict with voting weights in a quadratic vote to a
    single choice integer (the choice voted highest).
    Intended to be an quick approximation of a quadratic vote.
    Returns None  if all possible choices voted equal.
    '''

    votes_d = single_vote_dict   # catch error with some quadratic voting
    votes_set = {v for v in votes_d.values()}

    # return None if equal vote for all choices
    if len(votes_set) == 1 and len(votes_d) == len(all_poss_choices):
        return None

    # else return key of highest value
    else:
        return int(max(votes_d.items(), key=lambda x: x[1])[0])


def get_prop_data(proposal):
    '''
    Queries graphql and returns the most popular choice at this moment
    among other metadata as a nested dict with proposal id as key.
    If proposal has less than 100 votes, popular choice is None.
    '''

    # query graphql for the most recent 1000 votes and their choice
    query_votes = '''query Votes {
        votes (
            first: 1000
            skip: 0
            where: {
              proposal: "'''+str(proposal)+'''"
            }
        orderBy: "created",
        orderDirection: desc
        ) {
        choice
        }
        }'''
    votes_list = json_from_query(query_votes)['data']['votes']

    # query graphql for some proposal metadata
    query_proposal = '''query Proposal {
        proposal(id:"'''+proposal+'''") {
            id
            title
            body
            choices
            start
            end
            snapshot
            state
            author
            type
            space {
              id
              name
            }
          }
        }'''
    meta_data = json_from_query(query_proposal)['data']

    title = meta_data['proposal']['title']
    ts_created = meta_data['proposal']['start']
    vote_count = len(votes_list)
    possible_choices = meta_data['proposal']['choices']
    _type = meta_data['proposal']['type']
    space = meta_data['proposal']['space']['id']
    weighted_vote = False
    _id = meta_data['proposal']['id']

    # set flag for quadratic voting according to data
    if votes_list != [] and type(votes_list[0]['choice']) != int:
        weighted_vote = True


    # transfer choices to int dictionary keys
    choices_d = {}
    for i in range(len(possible_choices)):
        choices_d[i+1] = 0

    # Sum up count of each choice and determine most popular one
    for vote in votes_list:

        # Case: Someone voted for an unavailable choice
        if not weighted_vote:     # catch quadratic voting error
            if vote['choice'] not in choices_d:  # catch outsider vote
                outsider = vote['choice']
                cond_log(f'Oops, caught an outsider. Choice: {outsider}')
                continue

        # case: Quadratic voting
        if type(vote['choice']) == dict:
            highest_v = quadratic_voting_get_most_popular(vote['choice'], choices_d)
            if highest_v == None:
                continue
            else:
                choices_d[highest_v] += 1

        # case: Single choice voting
        else:
            choices_d[vote['choice']] += 1

    # Determine most voted choice so far
    most_popular = max(choices_d.items(), key=lambda x: x[1])[0]

    out_d = {
        proposal: {
            'title': title,
            'pop_choice': most_popular,
            'ts_created': ts_created,
            'total_votes': vote_count,
            'weighted_vote': weighted_vote,
            'type': _type,
            'space': space,
            'id': _id
        }
    }

    return out_d


def create_choices_json(export_json_path, choices_json_path):
    '''
    Takes proposals up for voting from json file and saves another json
    file with the most popular choice so far by other snapshot voters
    for each proposal. Will be inferred from a sample of the last 1000 voters.
    If less than 100 voters so far for a proposal, the choice will be None.
    '''
    to_vote_d = read_from_json(export_json_path)

    # abort if no active proposals to vote on
    if to_vote_d == {}:
        return

    # create empty dict with same structure as to_vote_d
    out_d = {}
    for wallet, prop_list in to_vote_d.items():
        out_d[wallet] = {}
        for prop in prop_list:
            out_d[wallet][prop] = {}

    # populate set of unique proposals
    props = set()
    for wallet, prop_list in to_vote_d.items():
        for prop in prop_list:
            props.add(prop)

    # create dict of proposals and their queried metadata
    prop_data_d = {}
    for prop in props:
        prop_data_d[prop] = get_prop_data(prop)[prop]

    # add metadata for each proposal for each wallet (structure as in to_vote)
    for wallet, props in to_vote_d.items():
        for prop in props:
            out_d[wallet][prop] = prop_data_d[prop]

    # save to json
    write_to_json(out_d, choices_json_path)
    cond_log('\nCreated a choices.json with metadata on active proposals.\n')


def filter_out_bot_catcher_proposals(choices_json_path, triggers):
    '''
    Removes any proposal containing the word bot, human, or sybil in title.
    '''
    choices = read_from_json(choices_json_path)
    props = {}

    # populate dict of unique proposals
    for prop_list in choices.values():
        if prop_list == {}:
            continue
        for _id, data in prop_list.items():
            props[_id] = data

    # remove any proposal containing a word from trigger list
    outfile = deepcopy(choices)
    removed = {}

    for wallet, prop_list in choices.items():
        if prop_list == {}:
            continue
        else:
            for _id, data in prop_list.items():
                title = data['title']
                print(title)
                if any(ele in title for ele in triggers):
                    del outfile[wallet][_id]
                    removed[_id] = data


    # update json file
    write_to_json(outfile, choices_json_path)
    if removed != {}:
        print('\nRemoved these proposals because of a trigger word caught in the proposal title:')
        print_dict = {x['id']: x['title'] for x in removed.values()}
        prettyprint(print_dict, keys_label='Proposal', values_label='Title')
        print('')

def enable_weighted_vote(choices_json_path):
    '''
    Corrects the popular choice to be in a dictionary format.
    '''
    choices = read_from_json(choices_json_path)
    outfile = deepcopy(choices)

    # replace single choice with dictionary
    for wallet, prop_list in choices.items():
        if prop_list == {}:
            continue
        else:
            for _id, data in prop_list.items():
                if data['weighted_vote'] == True:
                    choice_int = data['pop_choice']
                    choice_dict = '{"' + str(choice_int) + '":1}'
                    #choice_dict = {str(choice_int): 1}
                    print('\nChanged a choice to be compatible with the weighted vote...')
                    print('ID:', _id)
                    print('Title:', data['title'])
                    print('Old choice:', choice_int, 'New choice:', choice_dict)
                    print(outfile[wallet][data]['pop_choice'])
                    print(type(outfile[wallet][data]['pop_choice']))
                    outfile[wallet][data]['pop_choice'] = choice_dict

    # update json file
    write_to_json(outfile, choices_json_path)


def filter_out_low_engagement_props(choices_json_path):
    '''
    Reads in choices.json.
    Removes any proposal where less than 30% of usual voters have voted.
    Saves choices.json with those proposals removed.
    '''
    choices = read_from_json(choices_json_path)
    spaces_votes = {}
    props = {}

    # populate dict of unique proposals
    for prop_list in choices.values():
        if prop_list == {}:
            continue
        for _id, data in prop_list.items():
            props[_id] = data

    # read avg past votes from memo dict or alternatively query graphql
    for prop in props.copy():
        space = props[prop]['space']
        if space in spaces_votes:
            props[prop]['avg_votes'] = spaces_votes[space]
        else:
            avg_votes = get_avg_n_votes(space)
            spaces_votes[space] = avg_votes
            props[prop]['avg_votes'] = avg_votes

    # remove any proposal with less than 30% of the usual engagement
    outfile = deepcopy(choices)
    removed = {}

    for wallet, prop_list in choices.items():
        if prop_list == {}:
            continue
        else:
            for _id, data in prop_list.items():
                votes = data['total_votes']
                avg = props[_id]['avg_votes']
                if (votes/avg) < (3/10):
                    del outfile[wallet][_id]
                    removed[_id] = data

    # update json file
    write_to_json(outfile, choices_json_path)
    if removed != {}:
        print('\nRemoved these proposals because less than 30% of the usual voters have voted so far:')
        print_dict = {x['title']: x['total_votes'] for x in removed.values()}
        prettyprint(print_dict, keys_label='Proposal', values_label='Votes so far')
        print('')


def get_avg_n_votes(space_ens, n=2):
    '''
    Queries graphql for the 2 most recent closed votes and returns
    average number of voters out of the 2.
    '''
    # Query graphql: get most recent 2 prop ids
    # for each id: get n_votes
    # calculate average
    # return average
    recent_props = get_recent_closed_proposals(space_ens, n=n)
    vote_counts = [get_n_votes(prop) for prop in recent_props]
    avg = sum(vote_counts)/n
    return avg


def get_n_votes(proposal):
    '''
    Queries snapshot, returns True if wallet has voted on proposal already,
    returns False if not.
    '''

    query = '''query Votes {
        votes (
            first: 5000
            skip: 0
            where: {
              proposal: "'''+str(proposal)+'''"
            }
        orderBy: "created",
        orderDirection: desc
        ) {
        id
        voter
        created
        proposal {
          id
        }
        choice
        space {
          id
        }
        }
    }'''
    votes = json_from_query(query)
    return len(votes['data']['votes'])


def get_recent_closed_proposals(space_ens, n=2):
    '''
    Returns the most recent n closed proposal ids for a given space.
    '''
    n = str(n)
    space_ens = '"'+space_ens+'"'

    # Get all active proposals for these spaces
    query_active = '''query Proposals {
        proposals (
            first: '''+n+''',
            skip: 0,
            where: {
              space_in: '''+space_ens+''',
              state: "closed"
            },
            orderBy: "created",
            orderDirection: desc
        ) {
            id
            space {
              id
              name
            }
          }
    }'''
    result = json_from_query(query_active)

    # Create set of all active proposal id's of those spaces
    props = [x['id'] for x in result['data']['proposals']]
    return props


def prettyprint(dict_, keys_label='keys', values_label='values'):
    print('\n{:^35} | {:^6}'.format(keys_label, values_label))
    print('-'*65)
    for k,v in dict_.items():
        print("{:35} | {:<20}".format(k[:35],v))
