#import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            
            # 创建唯一订单ID
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            # 遍历每本书，处理库存和订单详情
            for book_id, count in id_and_count:
                # cursor = self.conn.execute(
                #     "SELECT book_id, stock_level, book_info FROM store "
                #     "WHERE store_id = ? AND book_id = ?;",
                #     (store_id, book_id),
                # )
                # row = cursor.fetchone()
                # if row is None:
                #     return error.error_non_exist_book_id(book_id) + (order_id,)

                # stock_level = row[1]
                # book_info = row[2]
                # book_info_json = json.loads(book_info)
                # price = book_info_json.get("price")

                book = self.stores_collection.find_one(
                    {"store_id": store_id, "inventory.book_id": book_id},
                    {"inventory.$": 1}
                )
                if book is None:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = book['inventory'][0]['stock_level']
                book_info_json = json.loads(book['inventory'][0]['book_info'])
                price = book_info_json.get("price")

                # 检查库存是否足够
                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

            #     cursor = self.conn.execute(
            #         "UPDATE store set stock_level = stock_level - ? "
            #         "WHERE store_id = ? and book_id = ? and stock_level >= ?; ",
            #         (count, store_id, book_id, count),
            #     )

                # 更新库存
                self.stores_collection.update_one(
                    {"store_id": store_id, "inventory.book_id": book_id},
                    {"$set": {"inventory.$.stock_level": stock_level - count}}  # 减少库存
                )

            #     if cursor.rowcount == 0:
            #         return error.error_stock_level_low(book_id) + (order_id,)

            #     self.conn.execute(
            #         "INSERT INTO new_order_detail(order_id, book_id, count, price) "
            #         "VALUES(?, ?, ?, ?);",
            #         (uid, book_id, count, price),
            #     )

            # self.conn.execute(
            #     "INSERT INTO new_order(order_id, store_id, user_id) "
            #     "VALUES(?, ?, ?);",
            #     (uid, store_id, user_id),
            # )
            # self.conn.commit()

                # 插入订单详情
                self.order_details_collection.insert_one({
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                })
            order_id = uid

        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        try:
            # cursor = conn.execute(
            #     "SELECT order_id, user_id, store_id FROM new_order WHERE order_id = ?",
            #     (order_id,),
            # )
            # row = cursor.fetchone()
            # if row is None:
            #     return error.error_invalid_order_id(order_id)

            # order_id = row[0]
            # buyer_id = row[1]
            # store_id = row[2]

            # 查找订单
            order = self.orders_collection.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            buyer_id = order['user_id']
            store_id = order['store_id']

            # 检查用户身份
            if buyer_id != user_id:
                return error.error_authorization_fail()

            # cursor = conn.execute(
            #     "SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,)
            # )
            # row = cursor.fetchone()
            # if row is None:
            #     return error.error_non_exist_user_id(buyer_id)
            # balance = row[0]
            # if password != row[1]:
            #     return error.error_authorization_fail()

            # 获取用户信息以检查余额和密码
            user = self.users_collection.find_one({"user_id": buyer_id}, {"balance": 1, "password": 1})
            if user is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = user['balance']
            if password != user['password']:
                return error.error_authorization_fail()

            # cursor = conn.execute(
            #     "SELECT store_id, user_id FROM user_store WHERE store_id = ?;",
            #     (store_id,),
            # )
            # row = cursor.fetchone()
            # if row is None:
            #     return error.error_non_exist_store_id(store_id)

            # seller_id = row[1]

            # 查找商店
            store = self.stores_collection.find_one({"store_id": store_id})
            if store is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = store['user_id']  # 获取卖家ID

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            # cursor = conn.execute(
            #     "SELECT book_id, count, price FROM new_order_detail WHERE order_id = ?;",
            #     (order_id,),
            # )
            # total_price = 0
            # for row in cursor:
            #     count = row[1]
            #     price = row[2]
            #     total_price = total_price + price * count

             # 计算订单总价
            order_details = self.order_details_collection.find({"order_id": order_id})
            total_price = sum(detail['count'] * detail['price'] for detail in order_details)

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            # cursor = conn.execute(
            #     "UPDATE user set balance = balance - ?"
            #     "WHERE user_id = ? AND balance >= ?",
            #     (total_price, buyer_id, total_price),
            # )
            # if cursor.rowcount == 0:
            #     return error.error_not_sufficient_funds(order_id)

            # cursor = conn.execute(
            #     "UPDATE user set balance = balance + ?" "WHERE user_id = ?",
            #     (total_price, seller_id),
            # )

            # if cursor.rowcount == 0:
            #     return error.error_non_exist_user_id(seller_id)

            # cursor = conn.execute(
            #     "DELETE FROM new_order WHERE order_id = ?", (order_id,)
            # )
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)

            # cursor = conn.execute(
            #     "DELETE FROM new_order_detail where order_id = ?", (order_id,)
            # )
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)

            # conn.commit()

            # 更新买家余额
            self.users_collection.update_one(
                {"user_id": buyer_id},
                {"$set": {"balance": balance - total_price}}  # 扣除余额
            )

            # 更新卖家余额
            seller = self.users_collection.find_one({"user_id": seller_id})
            if seller is None:
                return error.error_non_exist_user_id(seller_id)

            self.users_collection.update_one(
                {"user_id": seller_id},
                {"$set": {"balance": seller['balance'] + total_price}}  # 增加余额
            )

            # 删除订单和订单详情
            self.orders_collection.delete_one({"order_id": order_id})
            self.order_details_collection.delete_many({"order_id": order_id})

        # except sqlite.Error as e:
        #     return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
        #     cursor = self.conn.execute(
        #         "SELECT password  from user where user_id=?", (user_id,)
        #     )
        #     row = cursor.fetchone()
        #     if row is None:
        #         return error.error_authorization_fail()

        #     if row[0] != password:
        #         return error.error_authorization_fail()

        #     cursor = self.conn.execute(
        #         "UPDATE user SET balance = balance + ? WHERE user_id = ?",
        #         (add_value, user_id),
        #     )
        #     if cursor.rowcount == 0:
        #         return error.error_non_exist_user_id(user_id)

        #     self.conn.commit()
        # except sqlite.Error as e:
        #     return 528, "{}".format(str(e))

        # 查找用户信息
            user = self.users_collection.find_one({"user_id": user_id}, {"password": 1})
            if user is None:
                return error.error_authorization_fail()

            # 验证密码
            if user['password'] != password:
                return error.error_authorization_fail()

            # 增加用户余额
            self.users_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"balance": add_value}}  # 增加指定金额
            )

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
