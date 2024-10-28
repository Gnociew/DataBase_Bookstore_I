# fe/test/test_cancel_order.py
from datetime import datetime, timedelta
import pytest
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
from fe.access import book
from fe import conf
import uuid
from fe.access import auth

import time
from be.model import db_conn


class TestCancelOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # 初始化买家
        self.buyer_id = f"test_cancel_order_buyer_id_{uuid.uuid4()}"
        self.db_conn = db_conn.DBConn()
        self.password = "password123"
        self.seller_id = f"test_cancel_order_seller_id_{uuid.uuid4()}"
        self.store_id = f"test_store_{uuid.uuid4()}"
        self.auth = auth.Auth(conf.URL)

        # 注册新买家
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        code = self.buyer.add_funds(100000)
        assert code == 200, "充值失败"

        # 注册新卖家
        self.seller = register_new_seller(self.seller_id, self.password)

        # 创建商店
        code = self.seller.create_store(self.store_id)
        assert code == 200, "创建商店失败"

        # 生成并添加书籍
        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, 5)
        self.buy_book_id_list = []

        for bk in self.books:
            code = self.seller.add_book(self.store_id, 2, bk)
            assert code == 200
            self.buy_book_id_list.append(bk.id)

    def test_auto_cancel_order_10min_ago(self):
        """
        测试未支付订单在30分钟后是否会被自动取消。
        """
        # 创建一个未支付的订单10分钟前
        order_id = "order_id_not_pay1_{}".format(time.time())
        self.db_conn.unfinished_orders_collection.insert_one({
            "order_id": order_id,
            "user_id": self.buyer_id,
            "store_id": self.store_id,
            "create_time": datetime.now() - timedelta(minutes=10),
            "status": "未支付",
            "order_details": [{"book_id": self.buy_book_id_list[0], "count": 1}]
        })

        code, message = self.buyer.auto_cancel_order()
        assert code == 200, f"自动取消订单失败，消息: {message}"

        code, orders = self.buyer.view_finished_orders(self.buyer_id)
        if isinstance(orders, list):
            order_id_list_history = [order["order_id"] for order in orders]
        else:
            order_id_list_history = []
        assert order_id not in order_id_list_history, "10分钟前的的未支付订单不应该在订单历史中"

    def test_auto_cancel_order_40min_ago(self):
        """
        测试未支付订单在30分钟后是否会被自动取消。
        """
        # 创建一个未支付的订单40分钟前
        order_id = "order_id_not_pay2_{}".format(time.time())
        self.db_conn.unfinished_orders_collection.insert_one({
            "order_id": order_id,
            "user_id": self.buyer_id,
            "store_id": self.store_id,
            "create_time": datetime.now() - timedelta(minutes=40),
            "status": "未支付",
            "order_details": [{"book_id": self.buy_book_id_list[1], "count": 1}]
        })

        code, message = self.buyer.auto_cancel_order()
        assert code == 200, f"自动取消订单失败，消息: {message}"

        code, orders = self.buyer.view_finished_orders(self.buyer_id)
        if isinstance(orders, list):
            order_id_list_history = [order["order_id"] for order in orders]
        else:
            order_id_list_history = []
        assert order_id in order_id_list_history, "40分钟前的未支付订单应该在订单历史中"
