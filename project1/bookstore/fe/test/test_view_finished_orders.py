import pytest

from fe import conf
from fe.access.new_seller import register_new_seller
from fe.access import book
import uuid
from fe.access.new_buyer import register_new_buyer
from be.model import store
import random
from datetime import datetime



class TestViewFinishedOrders:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # do before test
        order_id1 = "test_view_finished_orders1_id_{}".format(str(uuid.uuid1()))
        order_id2 = "test_view_finished_orders2_id_{}".format(str(uuid.uuid1()))
        order_id3 = "test_view_finished_orders3_id_{}".format(str(uuid.uuid1()))
        store_id = "test_view_finished_orders_store_id_{}".format(str(uuid.uuid1()))
        self.user_id = "test_view_finished_orders_user_id_{}".format(str(uuid.uuid1()))
        status = "确认收货"

        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, 3)
        order_details = []
        for b in self.books:
            order_details.append({
                "book_id": b.id,  # 替换为实际的图书ID
                "count": random.randint(1, 5),  # 随机购买数量
                "price": b.price  # 替换为实际的图书单价
            })
            
        self.conn = store.get_db_conn()
        self.finished_orders_collection = self.conn['finished_orders']

        order_data1 = {
            "order_id": order_id1,  
            "user_id": self.user_id,
            "store_id": store_id,
            "create_time": datetime.now(),
            "pay_time": datetime.now(),  # 假设付款时间与创建时间相同
            "shipping_time": None,  # 如果还未发货，则设为 None
            "received_time": None,  # 如果还未确认收货，则设为 None
            "status": status,
            "order_details": order_details[0]
        }
        order_data2 = {
            "order_id": order_id2,
            "user_id": self.user_id,
            "store_id": store_id,
            "create_time": datetime.now(),
            "pay_time": datetime.now(),  # 假设付款时间与创建时间相同
            "shipping_time": None,  # 如果还未发货，则设为 None
            "received_time": None,  # 如果还未确认收货，则设为 None
            "status": status,
            "order_details": order_details[1]
        }
        order_data3 = {
            "order_id": order_id3,
            "user_id": self.user_id,
            "store_id": store_id,
            "create_time": datetime.now(),
            "pay_time": datetime.now(),  # 假设付款时间与创建时间相同
            "shipping_time": None,  # 如果还未发货，则设为 None
            "received_time": None,  # 如果还未确认收货，则设为 None
            "status": status,
            "order_details": order_details[2]
        }

        self.finished_orders_collection.insert_one(order_data1)
        self.finished_orders_collection.insert_one(order_data2)
        self.finished_orders_collection.insert_one(order_data3)

        self.buyer = register_new_buyer(self.user_id, self.user_id)


        yield
        # do after test

    # 测试查询存在的历史订单
    def test_view_finished_orders(self):
            code,order = self.buyer.view_finished_orders(self.user_id)
            # print(book)
            result_file_path = "fe/finished_orders.html"  # 前一级目录的文件路径

            with open(result_file_path, 'w', encoding='utf-8') as file:
                file.write(str(order))

            assert code == 200

    # 测试查询存在的历史订单
    def test_view_non_finished_orders(self):
        code,order = self.buyer.view_finished_orders("999")
        assert code != 200

    
