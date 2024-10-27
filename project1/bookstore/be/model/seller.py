#import sqlite3 as sqlite
from be.model import error
from be.model import db_conn
from datetime import datetime
import json


class Seller(db_conn.DBConn):
    def __init__(self):
        super().__init__()

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_info: str,  # 新增，用于 books 集合
        book_name:str,
        price:int,
        stock_level: int,
    ):
        try:
            # 检查用户、商店是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

        #     self.conn.execute(
        #         "INSERT into store(store_id, book_id, book_info, stock_level)"
        #         "VALUES (?, ?, ?, ?)",
        #         (store_id, book_id, book_json_str, stock_level),
        #     )
        #     self.conn.commit()
        # except sqlite.Error as e:
        #     return 528, "{}".format(str(e))

            # print("!!!!!!!!!!!!!",book_info)


          
            try:
                # 检查是否已存在该 book_id
                existing_book = self.books_collection.find_one({"book_id": book_id})
                
                if existing_book is None:
                    # 如果不存在，则插入新文档
                    self.books_collection.insert_one({
                        "book_id": book_id,
                        "store_id": store_id,
                        "book_info": book_info,
                        "purchase_quantity": 0
                    })
            except Exception as e:
                return 530, str(e)


            # 插入新书籍到指定商店的库存中
            result = self.stores_collection.update_one(
                {"store_id": store_id},
                {"$push": {
                    "inventory": {
                        "book_id": book_id,
                        "book_name":book_name,
                        "price":price,
                        "stock_level": stock_level
                    }
                }}
            )

            # 检查更新是否成功
            if result.modified_count == 0:
                return error.error_non_exist_store_id(store_id)

        except BaseException as e:
            # print(f"Error occurred: {str(e)}")  # 打印错误信息
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

        #     self.conn.execute(
        #         "UPDATE store SET stock_level = stock_level + ? "
        #         "WHERE store_id = ? AND book_id = ?",
        #         (add_stock_level, store_id, book_id),
        #     )
        #     self.conn.commit()
        # except sqlite.Error as e:
        #     return 528, "{}".format(str(e))

            # 更新书籍的库存数量
            result = self.stores_collection.update_one(
                {"store_id": store_id, "inventory.book_id": book_id},
                {"$inc": {"inventory.$.stock_level": add_stock_level}}
            )
            if result.modified_count == 0:
                return error.error_non_exist_store_id(store_id)

        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            
        #     self.conn.execute(
        #         "INSERT into user_store(store_id, user_id)" "VALUES (?, ?)",
        #         (store_id, user_id),
        #     )
        #     self.conn.commit()
        # except sqlite.Error as e:
        #     return 528, "{}".format(str(e))

            # 为用户创建新商店
            self.users_collection.update_one(
                {"user_id": user_id},
                {"$push": {"stores": {"store_id": store_id}}}
            )
            # 在商店集合中添加新商店文档
            self.stores_collection.insert_one({
                "store_id": store_id,
                "inventory": []
            })

        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"
    
    def get_book_rank10(self):
        book_info = self.books_collection.find().sort("purchase_quantity", -1).limit(10)


        # 将光标转换为列表
        book_info_list = list(book_info)
        # print("be",book_info_list)
        # print("be", book_info_list)

        not_found = { 'message': "No books found."}
        if not book_info_list:
            print("be model seller")
            return 404, not_found

        return 200,book_info_list
