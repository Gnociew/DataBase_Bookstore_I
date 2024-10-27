#import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from datetime import datetime, timedelta


class Buyer(db_conn.DBConn):    # 定义Buyer类，继承自DBConn类
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
            order_id = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            # 创建订单详情列表
            order_details = []

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

                # 从数据库获取书籍信息
                book = self.stores_collection.find_one(
                    {"store_id": store_id, "inventory.book_id": book_id},
                    {"inventory.$": 1}  # 仅获取匹配的库存信息
                )
                if book is None or not book.get('inventory'):
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                # 获取库存和价格信息
                # 确保inventory不为空，然后安全地访问元素
                stock_level = book['inventory'][0]['stock_level'] # 库存数量
                price = book['inventory'][0]['price']

                # 检查库存是否足够
                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

            #     cursor = self.conn.execute(
            #         "UPDATE store set stock_level = stock_level - ? "
            #         "WHERE store_id = ? and book_id = ? and stock_level >= ?; ",
            #         (count, store_id, book_id, count),
            #     )
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

                # 添加订单详情到列表中
                order_details.append({
                    "book_id": book_id,
                    "count": count,
                    "price": price
                })

            # 更新库存并插入订单
            for detail in order_details:
                book_id = detail['book_id']
                count = detail['count']

                # 更新库存
                self.stores_collection.update_one(
                    {"store_id": store_id, "inventory.book_id": book_id},
                    {"$set": {"inventory.$.stock_level": stock_level - count}}  # 减少库存
                )

            # 插入订单到 orders 集合中
            self.unfinished_orders_collection.insert_one({
                "order_id": order_id,  # 订单ID
                "user_id": user_id,  # 用户ID
                "store_id": store_id,  # 商店ID
                "create_time": datetime.now(),
                "status":"未支付",
                "order_details": order_details  # 订单详情
            })

        except Exception as e:
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

            order = self.unfinished_orders_collection.find_one({"order_id": order_id})
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
                logging.error(f"用户不存在：用户ID={buyer_id}")
                return error.error_non_exist_user_id(buyer_id)

            balance = user['balance']
            logging.info(f"用户余额：{balance}")

            if password != user['password']:
                logging.error(f"密码验证失败：用户ID={buyer_id}")
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

            # 查找拥有该商店的用户（卖家）
            seller = self.users_collection.find_one({"stores.store_id": store_id})
            if seller is None:
                return error.error_non_exist_store_id(store_id)
            seller_id = seller['user_id']

            if not self.user_id_exist(seller_id):
                logging.error(f"商店不存在：商店ID={store_id}")
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
            order = self.unfinished_orders_collection.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id)

            order_details = order.get('order_details', [])
            total_price = sum(detail['count'] * detail['price'] for detail in order_details)

            logging.info(f"订单总价：{total_price}")

            # 检查用户余额是否足够支付订单
            if balance < total_price:
                logging.error(f"余额不足：用户ID={buyer_id}, 订单总价={total_price}, 余额={balance}")
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
            logging.info(f"买家余额更新成功：扣除金额={total_price}")

            # 更新卖家余额
            seller = self.users_collection.find_one({"user_id": seller_id})
            if seller is None:
                logging.error(f"卖家不存在：卖家ID={seller_id}")
                return error.error_non_exist_user_id(seller_id)

            self.users_collection.update_one(
                {"user_id": seller_id},
                {"$set": {"balance": seller['balance'] + total_price}}  # 增加余额
            )
            logging.info(f"卖家余额更新成功：增加金额={total_price}")

            # 更新订单状态为已支付未发货，设置支付时间
            self.unfinished_orders_collection.update_one(
                {"order_id": order_id},
                {
                    "$set": {
                        "status": "已支付未发货",  # 更新状态
                        "pay_time": datetime.now()  # 设置支付时间
                    }
                }
            )

        # except sqlite.Error as e:
        #     return 528, "{}".format(str(e))

        except Exception as e:
            logging.error(f"支付过程中出现异常：{str(e)}")
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
        #  return 528, "{}".format(str(e))

            # 查找用户信息
            user = self.users_collection.find_one({"user_id": user_id}, {"password": 1})
            if user is None:
                return error.error_authorization_fail()

            # 密码验证
            if user['password'] != password:
                return error.error_authorization_fail()

            # 增加用户余额
            result = self.users_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"balance": add_value}}  # 增加指定金额
            )

            # 检查更新是否成功
            if result.modified_count == 0:
               return error.error_non_exist_user_id(user_id)

        except Exception as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
    
    def search_books(self,key_words):
        # print("bemodel",key_words)
        # key_words = key_words.encode('unicode_escape').decode('utf-8')
        query = {"$text": {"$search": key_words}}
        book_info = self.books_collection.find(query)

        # 将光标转换为列表
        book_info_list = list(book_info)
        # print("be",book_info_list)
        # print("be", book_info_list)

        not_found = { 'message': "No books found."}
        if not book_info_list:
            return 404, not_found

        return 200,book_info_list
