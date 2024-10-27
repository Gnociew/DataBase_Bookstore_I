# import pytest
# from fe.access.buyer import Buyer
# from fe.access.seller import Seller
# from fe.test.gen_book_data import GenBook
# from fe.access.new_buyer import register_new_buyer
# from fe.access.book import Book
# import uuid
# from datetime import datetime, timedelta
#
# class TestConfirmReceipt:
#     seller_id: str
#     store_id: str
#     buyer_id: str
#     password: str
#     buy_book_info_list: [Book]
#     order_id: str
#     buyer: Buyer
#     seller: Seller
#
#     @pytest.fixture(autouse=True)
#     def pre_run_initialization(self):
#         self.seller_id = "test_confirm_receipt_seller_id_{}".format(str(uuid.uuid1()))
#         self.store_id = "test_confirm_receipt_store_id_{}".format(str(uuid.uuid1()))
#         self.buyer_id = "test_confirm_receipt_buyer_id_{}".format(str(uuid.uuid1()))
#         self.password = self.seller_id
#         gen_book = GenBook(self.seller_id, self.store_id)
#         ok, buy_book_id_list = gen_book.gen(
#             non_exist_book_id=False, low_stock_level=False, max_book_count=5
#         )
#         self.buy_book_info_list = gen_book.buy_book_info_list
#         assert ok
#         b = register_new_buyer(self.buyer_id, self.password)
#         self.buyer = b
#         code, self.order_id = b.new_order(self.store_id, buy_book_id_list)
#         assert code == 200
#
#         # 确保将订单状态设为“已发货”以进行测试
#         code = b.shipping_order(self.order_id)  # 假设您有方法将订单状态设置为已发货
#         assert code == 200
#         yield
#
#     def test_confirm_receipt_ok(self):
#         # 测试用户确认收货的正常情况
#         code, message = self.buyer.confirm_receipt(self.order_id)
#         assert code == 200
#
#     def test_confirm_receipt_order_not_found(self):
#         # 测试确认收货时订单不存在的情况
#         code, message = self.buyer.confirm_receipt("invalid_order_id")
#         assert code != 200
#
#     def test_auto_confirm_receipt_ok(self):
#         # 测试平台自动确认收货的正常情况
#         # 先将订单发货时间设置为14天前
#         self.buyer.shipping_time = datetime.now() - timedelta(days=15)
#
#         # 调用自动确认收货的方法
#         code, message = self.buyer.auto_confirm_receipt()
#         assert code == 200
#
#     def test_auto_confirm_receipt_no_orders(self):
#         # 测试没有订单可以自动确认收货的情况
#         code, message = self.buyer.auto_confirm_receipt()
#         assert code != 200