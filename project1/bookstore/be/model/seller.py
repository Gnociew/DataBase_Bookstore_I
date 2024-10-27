#import sqlite3 as sqlite
from be.model import error
from be.model import db_conn
from datetime import datetime
import logging


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
        #     return 528, "{}".format(str(e))?

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

    def mark_order_shipped(self, order_id: str) -> (int, str):
        """
        根据订单ID标记订单为“已发货”。
        逻辑步骤：
        1. 查找订单，确保订单存在且状态为“未发货”。
        2. 获取订单中的 store_id。
        3. 根据 store_id 找到对应的卖家（用户）。
        4. 更新订单状态为“已发货”并记录发货时间。
        """
        try:
            # 查找未发货的进行中订单
            order = self.unfinished_orders_collection.find_one({
                "order_id": order_id,
                "status": "已支付未发货"
            })

            if not order:
                # 订单不存在或状态不为“未发货”
                return error.error_invalid_order_id(order_id)

            store_id = order.get("store_id")
            if not store_id:
                # 订单缺少 store_id 信息
                return error.error_and_message(528, "订单缺少 store_id 信息。")

            # 找到关联的用户（卖家）
            seller = self.users_collection.find_one({
                "stores.store_id": store_id
            })

            if not seller:
                # 未找到关联 store_id 的卖家
                return error.error_and_message(528, f"未找到关联 store_id '{store_id}' 的卖家。")

            # 更新订单状态为“已发货”并设置发货时间
            result = self.unfinished_orders_collection.update_one(
                {"order_id": order_id},
                {"$set": {
                    "status": "已发货",
                    "shipping_time": datetime.now()
                }}
            )

            if result.modified_count == 0:
                # 无法更新订单状态
                return error.error_and_message(528, "无法更新订单状态。")

            # 记录成功发货的日志
            logging.info(f"Order {order_id} marked as shipped by seller {seller.get('user_id')}.")

        except BaseException as e:
            logging.error(f"Error in mark_order_shipped: {str(e)}")
            return error.error_and_message(528, "未知错误。")
        return 200, "ok"
