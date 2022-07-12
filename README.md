# Snapshot Query


A script to query snapshot.page with multiple Ethereum wallets. It returns a 'to_vote.json'
file with all active proposal ids for each of your wallets that the respective wallet hasn't
yet voted on.
A more human-readable csv file 'to_vote.csv' is also returned that shows the names of
the snapshot spaces with active proposals instead of the proposal ids per wallet.
The json file is meant to be used as input for other scripts taking automated actions
based on the active proposals within the output json file. 
The csv is meant to be more of an easily verifiable sanity check of the script's
general functionality. 

The script is intended to be run as an automated task on a regular basis.
Proposals are automatically removed if:
- a customizable trigger word is detected in the title
- less than 30% of the average voters have participated (average calculated from the last 2 proposals)


## Usage

The script queries snapshot.page for new proposals for each wallet that is
specified in wallets.txt.

For each ETH address you want to check snapshot.page with:
Add it to wallets.txt (one address per line).
If you haven't joined any spaces with these wallets on snapshot.page yet,
with each wallet, join each snapshot space that you want updates on manually.
This needs to be done one time only.
Run the script.

A json and a csv file will be created in your project folder. Also, using the choices.json
file, you can vote with the repo [snapshot-vote](https://github.com/al-matty/snapshot-vote).

### csv example:


![Preview](https://github.com/al-matty/snapshot-voter/blob/main/csv_example.png)


### json example:


![Preview](https://github.com/al-matty/snapshot-voter/blob/main/json_example.png)


## License

This project is licensed under the [MIT license](https://github.com/al-matty/telegram-merch-bot/blob/main/LICENSE) - see the [LICENSE](https://github.com/al-matty/snapshot-voter/blob/main/LICENSE) file for details.
