# Telegram Merch Bot


A Telegram bot that produces merchandise for the cryptocurrency 'YLD' on demand.
You can add this bot on Telegram by searching for its handle `@YLDMerchBot`.
Send it `/merch` and it sends back infographics with always up-to-date token
metrics like circulating supply and market capitalization.

It does so in three steps:

1. Scrape and store up-to-date token metrics from coingecko.com.
2. Draw scraped data onto the template image.
3. Send image to user via Telegram.

Here is an example of one of the infograpics the bot delivers. Keep in mind
that the 'golden' metrics are up-to-date as of the time requested via Telegram.

![Preview](https://github.com/al-matty/TelegramMerchBot/blob/main/currentMerch.png)

## Requirements & Installation

The script runs on `python 3` and uses the packages listed in `requirements.txt`. 

The best practice would be to install a virtual environment and install the
requirements afterwards using `pip`:
```
pip3 install -r requirements.txt
```
If you're using `conda`, you can create a virtual environment and install the
requirements using this code:

```
conda create -n merchbot python=3.6
conda activate merchbot
pip3 install -r requirements.txt
```

## License

This project is licensed under the [MIT license](https://github.com/al-matty/telegram-merch-bot/blob/main/LICENSE) - see the [LICENSE](https://github.com/al-matty/telegram-merch-bot/blob/main/LICENSE) file for details.
