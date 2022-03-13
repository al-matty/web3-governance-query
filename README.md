# Snapshot Voter


A script to query snapshot.page with multiple Ethereum wallets. It returns a 'to_vote.json'
file with all active proposal ids for each of your wallets that the respective wallet hasn't
yet voted on.
A more easily readable csv file 'to_vote.csv' is also returned that shows the names of
the snapshot spaces with active proposals instead of the proposal ids per wallet.
The json file is meant to be used as input for other scripts, the csv is meant to be
more of an easily verifiable sanity check of the script's general functionality.
The script is intended to be used daily or on a regular basis.


## Usage

Create a wallets.txt with one ETH wallet address per line.
If you haven't joined any spaces with these wallets on snapshot.page yet,
with each wallet, join each snapshot space that you want updates on manually.
This needs to be done one time only.
Run the script.
A json and csv file will be created in your project folder.

csv example:
![Preview](https://github.com/al-matty/TelegramMerchBot/blob/main/currentMerch.png)

json example:
![Preview](https://github.com/al-matty/TelegramMerchBot/blob/main/currentMerch.png)

## License

This project is licensed under the [MIT license](https://github.com/al-matty/telegram-merch-bot/blob/main/LICENSE) - see the [LICENSE](https://github.com/al-matty/snapshot-voter/blob/main/LICENSE) file for details.
