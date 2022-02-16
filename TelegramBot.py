#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bot framework taken from Andrés Ignacio Torres <andresitorresm@gmail.com>,
all other files by Al Matty <almatty@gmail.com>.
"""
import time, os
import random
#import logging
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from PIL import Image
from urllib.error import HTTPError
from imageManipulation import *


class MerchBot:

    TELEGRAM_GROUP = 'group'

    """
    A class to encapsulate all relevant methods of the bot.
    """

    def __init__(self):
        """
        Constructor of the class. Initializes certain instance variables
        and checks if everything's O.K. for the bot to work as expected.
        """

        # This environment variable should be set before using the bot
        self.token = os.environ['TELEGRAM_BOT_TOKEN']


        # These will be checked against as substrings within each
        # message, so different variations are not required if their
        # radix is present (e.g. "all" covers "/all" and "ball")
        self.menu_trigger = ['/all', '/merch']
        self.pic_trigger = ['/moonshot', '/comparison']
        self.text_trigger = ['/links']

        # Maps commands to bot messages (text files)
        self.message_map = {
            '/links': 'links.txt'
            }

        # Maps commands to pictures
        self.image_map = {
            '/moonshot': 'YLD_Moon.jpg',
            '/comparison': 'YLD_Comp.png',
            #'YLDMastersOfDefi.JPG',
            #'YLD1.jpg',
            #'YLD2.jpg',
            #'YLD3.jpg',
            #'YLD4.jpg'
            }

        # Creates dict to store a timestamp for whenever a pic got updated
        self.lastFetched = {}
        for cmd in self.pic_trigger:
            img = self.image_map[cmd]
            self.lastFetched[img] = None


        # Stops runtime if the token has not been set
        if self.token is None:
            raise RuntimeError(
                "FATAL: No token was found. " + \
                "You might need to specify one or more environment variables.")

        # Configures logging in debug level to check for errors
#        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                            level=logging.DEBUG)


    def run_bot(self):
        """
        Sets up the required bot handlers and starts the polling
        thread in order to successfully reply to messages.
        """

        # Instantiates the bot updater
        self.updater = Updater(self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Declares and adds handlers for commands that shows help info
        start_handler = CommandHandler('start', self.show_menu)
        help_handler = CommandHandler('help', self.show_menu)
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(help_handler)

        # Declares and adds a handler for text messages that will reply with
        # a pic if the message includes a trigger word
        text_handler = MessageHandler(Filters.text, self.handle_text_messages)
        self.dispatcher.add_handler(text_handler)

        # Fires up the polling thread. We're live!
        self.updater.start_polling()




    def show_menu(self, update, context):
        """
        Shows the menu with current items.
        """

        MENU_MSG = "*Current Merch*\n\n" + \
                    "/comparison with AAVE, COMP, CEL\n" + \
                    "/moonshot price projections based on marketcap\n" + \
                    "/links useful YLD ecosystem links"

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=MENU_MSG,
            parse_mode='MarkdownV2'
            )


    def send_text(self, textfile, update, context):
        """
        Takes a textfile (path) and sends it as mesage to the user.
        """

        with open(textfile, 'r') as file:
            MSG = file.read()

        try:
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=MSG,
                disable_web_page_preview=True,
                parse_mode='MarkdownV2'
                )

        # Try sending again (infinitely) if HTTPError is raised
        except HTTPError as e:
                time.sleep(0.25)
                print('='*30)
                print(f'\nSuccessfully caught HTTPError:\n{e}\n')
                print('='*30)
                send_text(self, textfile, update, context)

    def send_signature(self, update, context):

        # Send signature message after each output
        MSG = "Available /merch:\n" + \
              "/comparison with AAVE, COMP, CEL\n" + \
              "/moonshot price projections based on marketcap\n" + \
              "/links useful YLD ecosystem links"

        context.bot.send_message(chat_id=update.message.chat_id, text=MSG)


    def handle_text_messages(self, update, context):
        """
        Checks if a message comes from a group. If that is not the case,
        or if the message includes a trigger word, replies with merch.
        """
        words = set(update.message.text.lower().split())
#        logging.debug(f'Received message: {update.message.text}')
#        logging.debug(f'Splitted words: {", ".join(words)}')

        # For debugging: Log users that got merch from bot
        chat_user_client = update.message.from_user.username
        if chat_user_client == None:
            chat_user_client = update.message.chat_id
        #        logging.info(f'{chat_user_client} got merch!')

        # Possibility: received command from menu_trigger
        for Trigger in self.menu_trigger:
            for word in words:
                if word.startswith(Trigger):
                    self.show_menu(update, context)
                    return

        # Possibility: received command from text_trigger
        for Trigger in self.text_trigger:
            for word in words:
                if word.startswith(Trigger):
                    file = self.message_map[Trigger]
                    self.send_text(file, update, context)
                    self.send_signature(update, context)
                    print(f'{chat_user_client} got links!')
                    return

        # Possibility: received command from pic_trigger
        for Trigger in self.pic_trigger:
            for word in words:
                if word.startswith(Trigger):
                    self.sendPic(Trigger, update, context)
                    self.send_signature(update, context)
                    print(f'{chat_user_client} got merch!')
                    return





    def update_or_not(self, pic_str):
        """
        Updates the pic if it hasn't been scraped already within last 2 minutes.
        """

        currentTime = int(time.time())

        def update(pic_str):

            if pic_str == 'YLD_Moon.jpg':
                self.lastFetched[pic_str] = updateMoon()

            elif pic_str == 'YLD_Comp.png':
                self.lastFetched[pic_str] = updateComparison()

            else:
                print(pic_str, 'not found. Nothing was updated.')


        # Possibility: First demand for this pic. Update pic
        if self.lastFetched[pic_str] == None:
            update(pic_str)
            return

        # Possibility: First demand since 2 mins for this pic. Update pic
        if currentTime - self.lastFetched[pic_str] > 120:
            update(pic_str)




    # Send out whatever specified in images
    def sendPic(self, cmd_str, update, context, caption=None):
        """
        Sends picture specified in imageMap[cmd_str] to user.
        Scrapes from web if not scraped within last 2 minutes.
        """

        # Send preliminary message
        MSG = 'Preparing your merch... \nGetting fresh numbers...'
#        MSG = "Bot is in maintenance mode right now, being fixed. " + \
#        "Just in case, this is the newest merch (not updated since " + \
#        "Mar 24 1:00 UTC)."
        context.bot.send_message(chat_id=update.message.chat_id, text=MSG)

        # For debugging only
#        chat_user_client = update.message.from_user.username
#        print(f'{chat_user_client} got no merch AAAAAH!')

        # Look up the right image for the command
        image = self.image_map[cmd_str]

        # Update pic if necessary (minimize scraping)
        self.update_or_not(image)

        # Send image specified for this command in self.image_map
        with open(image, 'rb') as img:

            # Sends the picture
            context.bot.send_photo(
                chat_id=update.message.chat_id,
                photo=img,
                caption=caption
                )

        # Some protection against repeatedly calling a bot function
        time.sleep(0.3)




def main():
    """
    Entry point of the script. If run directly, instantiates the
    MerchBot class and fires it up!
    """

    merch_bot = MerchBot()
    merch_bot.run_bot()


# If the script is run directly, fires the main procedure
if __name__ == "__main__":
    main()
