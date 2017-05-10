# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# import pymongo
#
# class
#

import pymongo
import datetime
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import DropItem


class MongoDBPipeline(object):
    def __init__(self):
        #filer on dups
        self.horses_seen = set()
        settings = get_project_settings()
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        #DUPLICATES
        if item['horsecode'] in self.horses_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            #get ranks dont think this is possible!!
            # item['scrapymongodb'] = {'ts': datetime.datetime.utcnow()}
            valid = True
            for data in item:
                if not data:
                    valid = False
                    raise DropItem("Missing {0}!".format(data))
            if valid:
                #needs to be collection update!
                # self.collection.insert(dict(item))
                self.collection.update(dict(item), dict(item), upsert=True)
            return item
