import psycopg2
from scrapy.exceptions import NotConfigured


#Pipeline inputs each data item from scrape into a postgres db. Note that the postgres db and tables must already be initialized beforehand
class PostgresPipeline(object):
    def __init__(self, db, user, passwd, host):
        self.db = db
        self.user = user
        self.passwd = passwd
        self.host = host


    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")

        if not db_settings: # if we don't define db config in settings
            raise NotConfigured # then reaise error

        db = db_settings['db']
        user = db_settings['user']
        passwd = db_settings['passwd']
        host = db_settings['host']

        return cls(db, user, passwd, host) # returning pipeline instance
        # crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)


    #Connect to postgres db when spider is started
    def open_spider(self, spider):
        self.conn = psycopg2.connect(dbname=self.db,
                                    user=self.user, password=self.passwd,
                                    host=self.host)
        self.cursor = self.conn.cursor()


    #function will insert each data item into postgres db as it is scraped
    def process_item(self, item, spider):
        sql = """INSERT INTO canadian_constituencies(postal_code, mp_name, mp_email, constituency_name, province, county, place, 
        constituency_population, constituency_registered_voters, constituency_polling_divisions) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        self.cursor.execute(sql,
                            (
                                item.get("postal_code"),
                                item.get("MP"),
                                item.get("MP_email"),
                                item.get("constituency"),
                                item.get("province"),
                                item.get("county"),
                                item.get("place"),
                                item.get("constituency_population"),
                                item.get("constituency_registered_voters"),
                                item.get("constituency_polling_divisions")
                            )
                        )
        self.conn.commit()
        return item


    #Closes db connection when spider is done
    def close_spider(self, spider):
        self.conn.close()
