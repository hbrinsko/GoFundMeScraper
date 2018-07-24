import sys
import pymongo
import scraping
import config

if __name__ == "__main__":
    
    uri ="mongodb://" + config.user + ":" + config.password + "@ds243441.mlab.com:43441/gofundme"

    client = pymongo.MongoClient(uri)
    db = client.get_default_database()
    campaigns = db['campaigns']
    scraped_data = scraping.scrape()
    campaigns.insert_many(scraped_data)

    client.close()