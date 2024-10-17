import logging
import os
#import sqlite3 as sqlite
from pymongo import MongoClient
import threading


class Store:
    database: str  # 数据库名称
    client: MongoClient  # MongoDB 客户端


    def __init__(self):
        # SQL-version ：初始化数据库
        # self.database = os.path.join(db_path, "be.db")
        # self.init_tables()

        # MongoDB-version 
        # 初始化 Store 实例，并设置数据库名称
        self.client = MongoClient('mongodb://localhost:27017/')  # 连接到本地 MongoDB 服务
        self.database = self.client['be']  # 设置数据库的名称
        self.init_collections()  # 调用初始化集合的方法  
        # print("initialize successfully!")

    # SQL-version ：初始化数据表
    # def init_tables(self):
    #     try:
    #         conn = self.get_db_conn()   # 获取数据库连接
    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS user ("
    #             "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
    #             "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
    #         )

    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS user_store("
    #             "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
    #         )

    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS store( "
    #             "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
    #             " PRIMARY KEY(store_id, book_id))"
    #         )

    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS new_order( "
    #             "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
    #         )

    #         conn.execute(
    #             "CREATE TABLE IF NOT EXISTS new_order_detail( "
    #             "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
    #             "PRIMARY KEY(order_id, book_id))"
    #         )

    #         conn.commit()
    #     except sqlite.Error as e:
    #         logging.error(e)
    #         conn.rollback()

    # MongoDB-version ：初始化集合
    def init_collections(self):
        # print("init collections ing")
        # 初始化 MongoDB 集合
        try:
            # 初始集合们并创建索引（创建集合时不需要初始化文档的内容）
            self.users_collection = self.database['users']
            self.users_collection.create_index("user_id", unique=True)

            self.stores_collection = self.database['stores']
            self.stores_collection.create_index("store_id", unique=True)

            self.orders_collection = self.database['orders']
            self.orders_collection.create_index("order_id", unique=True)


        except Exception as e:
            logging.error(e)  # 记录错误信息

    # SQL-version
    # def get_db_conn(self) -> sqlite.Connection:
    #     return sqlite.connect(self.database)

    # MongoDB-version
    def get_db_conn(self):
        return self.database



# 全局变量，用于数据库实例
database_instance: Store = None
# 全局变量，用于数据库同步
init_completed_event = threading.Event()


# 初始化数据库
def init_database():
    # print("store.py init db")
    global database_instance
    database_instance = Store()
    # print("Database instance initialized successfully")

    # 获取数据库连接
    db = database_instance.get_db_conn()
    # 确保 db 是一个有效的 Database 实例
    # print(f"DB type: {type(db)}")  # 输出 db 类型
    



# 获取数据库连接
def get_db_conn():
    # print("arrive at store.py get_db_conn")
    global database_instance
    if database_instance is None:
        print("Database instance is not initialized.")
    else:
        print(f"Database instance type: {type(database_instance)}")  # 打印类型
    return database_instance.get_db_conn() if database_instance else None
