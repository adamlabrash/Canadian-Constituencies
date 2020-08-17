# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ConstituencyItem(scrapy.Item):
    postal_code = scrapy.Field()
    province = scrapy.Field()
    county = scrapy.Field()
    place = scrapy.Field()
     
    MP = scrapy.Field()
    MP_email = scrapy.Field()

    constituency = scrapy.Field()
    constituency_population = scrapy.Field()
    constituency_registered_voters = scrapy.Field()
    constituency_polling_divisions = scrapy.Field()
