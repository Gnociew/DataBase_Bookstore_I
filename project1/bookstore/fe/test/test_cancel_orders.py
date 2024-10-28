# fe/test/test_cancel_order.py

import pytest
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
from fe.access import book
from fe import conf
import uuid

class TestCancelOrder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # 初始化买家
        self.buyer_id = f"test_cancel_order_buyer_id_{uuid.uuid4()}"
        self.password = "password123"
        self.seller_id = f"test_cancel_order_seller_id_{uuid.uuid4()}"
        self.store_id=f"test_store_{uuid.uuid4()}"
        self.buyer = register_new_buyer(self.buyer_id, self.password)
        code = self.buyer.add_funds(100000)
        assert code == 200, "充值失败"

        self.seller = register_new_seller(self.seller_id, "seller_password")

        # 创建商店
        code = self.seller.create_store(self.store_id)
        assert code == 200, "创建商店失败"

        # 添加书籍
        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, 6)
        self.buy_book_id_list = []

        for bk in self.books:
            code = self.seller.add_book(self.store_id, 2, bk)
            assert code == 200
            self.buy_book_id_list.append(bk.id)

        # 创建不同状态的订单
        # 1. 未支付的订单
        test_book_id_list = []
        for i in range(0, 2):
            tmp_tuple = (self.buy_book_id_list[i], 1)
            test_book_id_list.append(tmp_tuple)
        code, order_id = self.buyer.new_order(self.store_id, test_book_id_list)
        assert code == 200, f"创建订单失败"
        self.unpaid_order_id = order_id

        # 2. 已支付的订单
        test_book_id_list = []
        for i in range(2, 4):
            tmp_tuple = (self.buy_book_id_list[i], 1)
            test_book_id_list.append(tmp_tuple)
        code, order_id = self.buyer.new_order(self.store_id, test_book_id_list)
        assert code == 200, f"创建订单失败"

        code = self.buyer.payment(order_id)
        assert code == 200, f"支付失败"
        self.paid_order_id = order_id

        # 3. 已发货的订单
        test_book_id_list = []
        for i in range(4, 6):
            tmp_tuple = (self.buy_book_id_list[i], 1)
            test_book_id_list.append(tmp_tuple)
        code, order_id = self.buyer.new_order(self.store_id, test_book_id_list)
        assert code == 200, f"创建订单失败"

        code = self.buyer.payment(order_id)
        assert code == 200, f"支付失败"

        code = self.seller.mark_order_shipped(order_id)
        assert code == 200, "标记订单为已发货失败"
        self.already_order_id=order_id

        yield


    def test_cancel_unpaid_order_within_30_minutes(self):
        """测试在下单未支付且30分钟内取消订单"""
        order_id = self.unpaid_order_id

        code, msg = self.buyer.cancel_order(order_id)
        assert code == 200
        assert msg == "订单取消成功"


    def test_cancel_paid_order_before_shipment(self):
        """测试在下单已支付但未发货时取消订单"""
        order_id = self.paid_order_id

        code, msg = self.buyer.cancel_order(order_id)
        assert code == 200
        assert msg == "订单取消成功"
    def test_cancel_shipped_order(self):
        """测试在订单已发货时取消订单"""
        order_id = self.already_order_id

        code, msg = self.buyer.cancel_order(self.already_order_id)
        assert code == 200
        assert msg == "订单取消成功"
    def test_cancel_non_existing_order(self):
        """测试取消不存在的订单"""
        code, msg = self.buyer.cancel_order("non_existing_order_id")
        assert code != 200
        assert msg != "订单取消成功"


