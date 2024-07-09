import adata
import os
import pymongo


def update_stock_list():
    res_df = adata.stock.info.all_code()
    stock_list = open(os.path.join(os.path.dirname(__file__), "caches")+os.sep + "stock_list.txt", "w")
    for index, row in res_df.iterrows():
        stock_list.write(row["stock_code"] + ',' + row["short_name"] + '\n')
    stock_list.close()


# update_stock_list()

stock_db = pymongo.MongoClient(host='127.0.0.1', port=27017)
stock_lists_collection = stock_db['stock_list']['cn']
stock_lists = []


def save_to_mongo():
    stock_lists_collection.delete_many({})
    with open('caches/stock_list.txt', 'r') as file:
        for item in file.readlines():
            stock_lists_collection.insert_one({"number": item.split(',')[0], "name": item.split(',')[1]})


def get_stock_list():
    documents = stock_lists_collection.find()
    for document in documents:
        stock_lists.append(document.items())

            
save_to_mongo()
stock_db.close()

