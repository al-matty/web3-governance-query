# Snapshot Query

![GitHub](https://img.shields.io/github/license/al-matty/snapshot-query)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/release/python-390/)
![Libraries.io dependency status for GitHub repo](https://img.shields.io/librariesio/github/al-matty/snapshot-query)

A script to query snapshot.page with multiple Ethereum addresses. It returns 3 files:

* `to_vote.json`  for each address: all active proposal ids that the address hasn't yet voted on
* `to_vote.csv`   for each address: all snapshot space names with currently active proposals that the address hasn't yet voted on
* `choices.json`  proposal data for all active proposals, usable as voting recipe for the complementary repo [snapshot-vote](https://github.com/al-matty/snapshot-vote)

The json files are meant to be used as potential input for other scripts taking automated actions based on the queried data, while the csv file is meant to be more of an easily verifiable sanity check of the script's general functionality. The script is intended to run as an automated task on a regular basis.
To filter out some potential noise and avoid blacklisting targeting bots, proposals are ignored if:
- a customizable trigger word is detected in the title
- less than 30% of the average voters have participated (average calculated from the last 2 proposals). This is not a problem if the script is run regularly. As soon as the proposal gains some traction (>30%), it will no longer be filtered out.


## Usage

Specify all the Ethereum addresses you want to get voting information on in './wallets.txt', one address per line.
If you haven't joined any spaces with these wallets on snapshot.page yet, with each wallet, join each snapshot space that you want updates on in the future. This needs to be done one time only. Run [snapshotQuery.py](https://github.com/al-matty/snapshot-query/blob/main/snapshotQuery.py).
The three mentioned output files will be created in your project folder.

Using the 'choices.json' file, you can now automate voting based on customizable conditions using the repo [snapshot-vote](https://github.com/al-matty/snapshot-vote) for voting and [create_choices_json()](https://github.com/al-matty/snapshot-query/blob/main/functions.py#:~:text=function_name)
to freely customize the logic for voting.

### csv example:


![Preview](https://github.com/al-matty/snapshot-voter/blob/main/csv_example.png)


### json example:


![Preview](https://github.com/al-matty/snapshot-voter/blob/main/json_example.png)


## License

This project is licensed under the [MIT license](https://github.com/al-matty/telegram-merch-bot/blob/main/LICENSE) - see the [LICENSE](https://github.com/al-matty/snapshot-voter/blob/main/LICENSE) file for details.
