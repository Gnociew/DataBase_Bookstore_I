import pytest
import time
from be.model import db_conn
from datetime import datetime, timedelta
from fe.access import auth
from fe import conf

class TestConfirmReceipt:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.auth = auth.Auth(conf.URL)
        self.db_conn = db_conn.DBConn()  # 创建 DBConn 实例
        self.user_id = "test_credit_{}".format(time.time())
        self.order_id_shipped = "order_shipped_{}".format(time.time())
        self.order_id_unshipped = "order_unshipped_{}".format(time.time())

        # 创建已发货订单数据
        self.db_conn.unfinished_orders_collection.insert_one({
            "order_id": self.order_id_shipped,
            "user_id": self.user_id,
            "store_id": "test_store",
            "create_time": datetime.now() - timedelta(days=20),
            "pay_time": datetime.now() - timedelta(days=18),
            "shipping_time": datetime.now() - timedelta(days=8),
            "status": "已发货",
            "order_details": [{"item_id": "item1", "quantity": 1}]
        })

        # 创建未发货订单数据
        self.db_conn.unfinished_orders_collection.insert_one({
            "order_id": self.order_id_unshipped,
            "user_id": self.user_id,
            "store_id": "test_store",
            "create_time": datetime.now() - timedelta(days=2),
            "pay_time": datetime.now() - timedelta(days=3),
            "status": "未发货",
            "order_details": [{"item_id": "item2", "quantity": 2}]
        })

        yield

        # 清理测试数据
        self.db_conn.unfinished_orders_collection.delete_many({"user_id": self.user_id})
        self.db_conn.finished_orders_collection.delete_many({"user_id": self.user_id})

    # 测试自动确认收货成功 - 符合条件的订单已发货超过14天
    def test_auto_confirm_receipt_success(self):
        # 首先将已发货订单的发货时间更新到14天以后，确保符合自动确认条件
        self.db_conn.unfinished_orders_collection.update_one(
            {"order_id": self.order_id_shipped},
            {"$set": {"shipping_time": datetime.now() - timedelta(days=15)}}
        )
        code = self.auth.auto_confirm_receipt()
        assert code == 200
        # 验证符合条件的订单是否被移动到历史订单集合
        finished_order = self.db_conn.finished_orders_collection.find_one({"order_id": self.order_id_shipped})
        assert finished_order is not None
        assert finished_order["status"] == "确认收货"

    # 测试确认收货成功
    def test_confirm_receipt_success(self):
        code = self.auth.confirm_receipt(self.user_id, self.order_id_shipped)
        assert code == 200
        # 验证订单是否移动到历史订单集合
        finished_order = self.db_conn.finished_orders_collection.find_one({"order_id": self.order_id_shipped})
        assert finished_order is not None
        assert finished_order["status"] == "确认收货"

    # 测试确认收货失败 - 订单状态不是已发货
    def test_confirm_receipt_failure(self):
        code = self.auth.confirm_receipt(self.user_id, self.order_id_unshipped)
        assert code != 200




