import jwt
import time
import logging
from be.model import error
from be.model import db_conn
from datetime import datetime, timedelta

from be.model.store import init_database


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded

def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self) 

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            initial_credit = 100  # 设置初始信用分
            self.users_collection.insert_one({
                "user_id": user_id,
                "password": password,
                "balance": 0,
                "token": token,
                "terminal": terminal,
                "credit": initial_credit,
                "stores": []
            })
        
        except Exception as e:
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        # cursor = self.conn.execute("SELECT token from user where user_id=?", (user_id,))
        # row = cursor.fetchone()
        # if row is None:
        #     return error.error_authorization_fail()
        # db_token = row[0]
        user = self.users_collection.find_one({"user_id": user_id})
        if user is None:
            return error.error_authorization_fail()
        db_token = user.get("token")
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        user = self.users_collection.find_one({"user_id": user_id})
        if user is None:
            return error.error_authorization_fail()

        if password != user.get("password"):
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"token": token, "terminal": terminal}}
            )
        except Exception as e:
            return 530, "{}".format(str(e)), ""
        return 200, "ok", token


    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)
            self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"token": dummy_token, "terminal": terminal}}
            )
        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message
            result = self.users_collection.delete_one({"user_id": user_id})
            if result.deleted_count == 1:
                return 200, "ok"
            else:
                return error.error_authorization_fail()
        except Exception as e:
            return 530, "{}".format(str(e))


    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"password": new_password, "token": token, "terminal": terminal}}
            )
        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    # 检查信用分是否足够
    def check_credit(self, user_id: str) -> (int, str):
        user = self.users_collection.find_one({"user_id": user_id})
        if user is None:
            return error.error_authorization_fail()

        if user.get("credit") < 3:
            return 400, "Insufficient credit to cancel the order."

        return 200, "Credit is sufficient."

    # 更新用户的信用分
    def update_credit(self, user_id: str, points: int) -> (int, str):
        # 先检查信用分是否足够
        code, message = self.check_credit(user_id)
        if code != 200:
            return code, message  # 若信用分不足，则返回检查结果

        try:
            result = self.users_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"credit_score": -points}}  # 扣除信用分
            )
            if result.modified_count == 0:
                return error.error_authorization_fail()  # 用户未找到
        except Exception as e:
            return 530, "{}".format(str(e))
        return 200, "Credit score update successfully."

    # 设置信用分
    def set_credit_score(self, user_id: str, score: int):
        try:
            self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"credit": score}}
            )
            return 200, "Credit score updated successfully."
        except Exception as e:
            return 530, str(e)

    # 用户确认收货
    def confirm_receipt(self, user_id: str, order_id: str) -> (int, str):
        try:
            # 查找未发货的订单，确保订单属于该用户
            unfinished_order = self.unfinished_orders_collection.find_one({
                "order_id": order_id,
                "user_id": user_id,
                "status": "已发货"
            })

            if not unfinished_order:
                return 404, "No valid unfulfilled orders were found or the order was confirmed to be received."

            # 将订单插入到历史订单集合中
            self.finished_orders_collection.insert_one({
                "order_id": unfinished_order["order_id"],
                "user_id": unfinished_order["user_id"],
                "store_id": unfinished_order["store_id"],
                "create_time": unfinished_order["create_time"],
                "pay_time": unfinished_order["pay_time"],
                "shipping_time": unfinished_order["shipping_time"],
                "received_time": datetime.now(),  # 设置确认收货时间
                "status": "确认收货",
                "order_details": unfinished_order["order_details"]
            })

            # 从进行中订单集合中删除该订单
            self.unfinished_orders_collection.delete_one({"order_id": order_id})

        except Exception as e:
            return 530, "Error: {}".format(str(e))

        return 200, "Confirm that the receipt is successful."

    # 平台自动确认收货:检查已发货订单是否超过14天，超过则自动确认收货
    def auto_confirm_receipt(self) -> (int, str):
        try:
            # 当前时间减去14天
            fourteen_days_ago = datetime.now() - timedelta(days=14)

            # 找出发货超过14天且未确认收货的订单
            orders_to_confirm = self.unfinished_orders_collection.find({
                "status": "已发货",
                "shipping_time": {"$lte": fourteen_days_ago}
            })

            # 判断是否有符合条件的订单
            if not orders_to_confirm.count():
                return 404, "No orders eligible for automatic receipt confirmation were found."

            # 遍历符合条件的订单并更新状态
            for order in orders_to_confirm:
                order_id = order['order_id']

                # 将订单移动到历史订单集合
                self.finished_orders_collection.insert_one({
                    "order_id": order["order_id"],
                    "user_id": order["user_id"],
                    "store_id": order["store_id"],
                    "create_time": order["create_time"],
                    "pay_time": order["pay_time"],
                    "shipping_time": order["shipping_time"],
                    "received_time": datetime.now(),
                    "status": "确认收货",
                    "order_details": order["order_details"]
                })

                # 从进行中订单集合中删除该订单
                self.unfinished_orders_collection.delete_one({"order_id": order_id})

            return 200, "Automatic confirmation of receipt was successful for eligible orders."

        except Exception as e:
            return 530, "Error during automatic confirmation of receipt: {}".format(str(e))
