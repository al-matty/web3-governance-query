#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Image Manipulation Module for MerchBot
"""
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from scrapeData import get_comp_metrics, get_moon_metrics
from math import floor


def updateMoon():
    '''
    Calls scrapeData.get_moon_metrics() and prints token data on template image.
    Returns unix time stamp.
    '''

    moon_metrics = get_moon_metrics()

    outfile = 'YLD_Moon.jpg'
    img = Image.open('TemplateYLD4.JPG')

    d1 = ImageDraw.Draw(img)
    myFont = ImageFont.truetype('GothamBook.ttf', size=26)

    draw_order = ['yield', 'cream', 'anchor-protocol', 'alpha-finance', 'compound', 'aave']
    yield_mc = moon_metrics['yield']['marketCap']
    yield_price = moon_metrics['yield']['priceUSD']

    def parse_str(float_, roundTo=1):
        '''
        Parses float to str.
        Conditionally appends nothing, 'k', 'm' or 'b'
        '''
        def round_or_not(float_, roundTo=roundTo):
            if roundTo:
                return round(float_, roundTo)
            else:
                return float_

        if float_ >= 1000000000:
            return str(round_or_not(float_/1000000000)) + 'bn'
        if float_ >= 1000000:
            return str(round(float_/1000000)) + 'm'
        else:
            return str(round(float_))

    def draw_row(moon_metric, pos_y):
        #gold = (237, 187, 130)
        white = (255, 255, 255)

        # Draw mc twice
        mc = '$' + parse_str(moon_metric['marketCap'])
        pos_x = 525 - (len(mc) / 2)
        d1.text((pos_x, pos_y), mc, font=myFont, fill=white)
        d1.text((pos_x + 280, pos_y), mc, font=myFont, fill=white)

        # Draw ROI
        roi = str(round(moon_metric['marketCap'] / yield_mc, 1)) + 'x'
        pos_x = 150 - (len(roi)/ 2)
        d1.text((pos_x, pos_y), roi, font=myFont, fill=white)

        # Draw YLD extrapolated price
        multiplier = moon_metric['marketCap'] / yield_mc
        yld_price = '$' + parse_str(round(multiplier * yield_price))
        pos_x = 335 - (len(yld_price)/ 2)
        d1.text((pos_x, pos_y), yld_price, font=myFont, fill=white)


    pos_y = 348

    for token_str in draw_order:
        metrics = moon_metrics[token_str]

        draw_row(metrics, pos_y)

        pos_y += 107


    # Draw time last updated
    pos = (665,970)
    gold = (237, 187, 130)

    timeStamp = int(time.time())
    parsedTs = datetime.utcfromtimestamp(timeStamp).strftime('%d %b %Y')
    drawTime = 'Figures as at ' + str(parsedTs)
    dateFont = ImageFont.truetype('GothamBook.ttf', size=20)

    d1.text(pos, drawTime, font=dateFont, fill =gold)

    # Save outfile
    img.save(outfile)

    # Get current time in unix format
    timeStamp = int(time.time())

    return timeStamp


def updateComparison():
    '''
    Calls scrapeData.get_comp_metrics() and prints token data on comparison template.
    Returns unix time stamp.
    '''

    dictOfDicts = get_comp_metrics()
    template = 'YLD_Comp_Template.png'
    outfile = 'YLD_Comp.png'

    img = Image.open(template)

    def getMcStr(dict_, int_=False):
        '''return market cap string'''
        if dict_['marketCap'] < 1000000000:
            if int_:
                return str(round(dict_['marketCap'] / 1000000)) + 'm'
            else:
                return str(round(dict_['marketCap'] / 1000000, 1)) + 'm'
        else:
            if int_:
                return str(round(dict_['marketCap'] / 1000000000)) + 'b'
            else:
                return str(round(dict_['marketCap'] / 1000000000, 1)) + 'b'


    def getSupplStr(dict_, int_=False):
        '''Returns circulating supply string'''
        if dict_['circSupply'] < 1000000:
            if int_:
                return str(round(dict_['circSupply'] / 1000)) + 'k'
            else:
                return str(round(dict_['circSupply'] / 1000, 1)) + 'k'
        else:
            if int_:
                return str(round(dict_['circSupply'] / 1000000)) + 'm'
            else:
                return str(round(dict_['circSupply'] / 1000000, 1)) + 'm'


    def drawTokenData(img, position, dict_):
        '''
        Assumes image, position and token metrics dict.
        Prints data on image and returns it.
        '''
        # Draw token metrics
        d1 = ImageDraw.Draw(img)
        myFont = ImageFont.truetype('GothamBook.ttf', 18)

        posMc = position
        posSup = (position[0] + 148, position[1])
        strMc = getMcStr(dict_)
        strSup = getSupplStr(dict_)

        d1.text(posMc, strMc, font=myFont, fill =(237, 187, 130))
        d1.text(posSup, strSup, font=myFont, fill =(237, 187, 130))

        # Draw current time
        timeStamp = int(time.time())    # Get current time in unix format
        parsedTs = datetime.utcfromtimestamp(timeStamp).strftime('%d %b %Y')
        drawTime = 'Figures as at ' + str(parsedTs)

        dateFont = ImageFont.truetype('GothamBook.ttf', 14)
        d1.text((1018, 462), drawTime, font=dateFont, fill =(237, 187, 130))

        return img


    # Cycle through keys and draw values under 'marketCap' and 'circSupply'
    # depending on 'pos' tuple (position).
    for key in dictOfDicts.keys():
        # Some position adjustment to factor in the changed font
        pos = (dictOfDicts[key]['pos'][0], dictOfDicts[key]['pos'][1] + 2)
        # Draw token metrics on image
        updatedPic = drawTokenData(img, pos, dictOfDicts[key])

    # Save updated pic
    updatedPic.save(outfile)

    # Get current time in unix format
    timeStamp = int(time.time())

    return timeStamp
