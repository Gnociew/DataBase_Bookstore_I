#import sqlite3 as sqlite
from be.model import error
from be.model import db_conn
from datetime import datetime


class Seller(db_conn.DBConn):
    def __init__(self):
        super().__init__()

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_name: str,  # 从 book_info 改为 book_name
        book_info: str,  # 新增，用于 books 集合
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

            # 插入新书籍到指定商店的库存中
                # 插入新书籍到 books 集合
            self.books_collection.insert_one({
                "book_id": book_id,
                "store_id": store_id,
                "book_info": book_info,
                "purchase_quantity": 0
            })

            # 插入新书籍到指定商店的库存中
            result = self.stores_collection.update_one(
                {"store_id": store_id},
                {"$push": {
                    "inventory": {
                        "book_id": book_id,
                        "book_name": book_name,
                        "price":book_info.book_price,
                        "stock_level": stock_level
                    }
                }}
            )

            # 检查更新是否成功
            if result.modified_count == 0:
                return error.error_non_exist_store_id(store_id)

        except BaseException as e:
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
