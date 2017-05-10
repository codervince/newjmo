# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RaceItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    racenumber = scrapy.Field()
    racedatetimeutc = scrapy.Field()
    isStarted = scrapy.Field()
    prizemoney= scrapy.Field()
    rating= scrapy.Field()
    raceclass= scrapy.Field()
    distance= scrapy.Field()
    surface= scrapy.Field()
    rail = scrapy.Field()
    going = scrapy.Field()
    hkjc_results_url = scrapy.Field()
    hkjc_race_url= scrapy.Field()
    # class distance

class RunnerItem(scrapy.Item):
    horsenumber = scrapy.Field()
    last6runs = scrapy.Field()
    colour = scrapy.Field()
    seasonstakes = scrapy.Field()
    besttime = scrapy.Field()
    seasonstakesrank = scrapy.Field()
    besttimerank = scrapy.Field()
    horsename = scrapy.Field()
    horsecode = scrapy.Field()
    jockeycode = scrapy.Field()
    draw = scrapy.Field()
    trainercode = scrapy.Field()
    owner = scrapy.Field()
    sire = scrapy.Field()
    result = scrapy.Field()
    importcategory = scrapy.Field()
    therace = scrapy.Field() #nested
    gear = scrapy.Field()
    priority = scrapy.Field()
    scrapymongodb = scrapy.Field()

    # hkjc_results_url= scrapy.Field()

    # racedatetimeutc = scrapy.Field()
    # isStarted = scrapy.Field()
    # runneritems= scrapy.Field()
    # todaysHorses= scrapy.Field()
    # todaysTrainers= scrapy.Field()
    # todaysGears= scrapy.Field()
    # todaysSeasonStakes= scrapy.Field()
    # todaysPriorities= scrapy.Field()
    # todaysDraws= scrapy.Field()
    # todaysImportCategories= scrapy.Field()
    # todaysOwners= scrapy.Field()
    # todaysSires= scrapy.Field()
    # todaysJockeys= scrapy.Field()
