import pytest
import uuid
from fe import conf
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
from fe.access import book
class TestSellerOperations:
    @pytest.fixture(autouse=True)
    def setup(self):
        # 生成唯一的 seller_id, store_id, buyer_id
        self.seller_id = f"test_seller_{uuid.uuid4()}"
        self.store_id = f"test_store_{uuid.uuid4()}"
        self.buyer_id = f"test_buyer_{uuid.uuid4()}"
        self.password = "secure_password"

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
        self.already_order_id = []
        yield

        # 清理数据（根据实际情况实现）
        # 例如，删除创建的用户、商店、书籍等

    def test_mark_order_shipped_success(self):
        """
        测试成功标记订单为“已发货”。
        """
        # 创建新订单
        test_mark_order_shipped_success_book_id_list = []
        for i in range(0,3):
            tmp_tuple = (self.buy_book_id_list[i],1)
            test_mark_order_shipped_success_book_id_list.append(tmp_tuple)
        code, order_id =self.buyer.new_order(self.store_id, test_mark_order_shipped_success_book_id_list)
        assert code == 200, f"创建订单失败"

        code = self.buyer.payment(order_id)
        assert code == 200, f"支付失败"

        # 标记订单为已发货
        code = self.seller.mark_order_shipped(order_id)
        assert code == 200, "标记订单为已发货失败"
        self.already_order_id.append(order_id)

    def test_mark_order_shipped_invalid_order(self):
        """
        测试使用不存在的订单ID标记订单为“已发货”。
        """
        invalid_order_id = f"invalid_order_id_{uuid.uuid4()}"
        code = self.seller.mark_order_shipped(invalid_order_id)
        assert code != 200, "应返回错误代码，因为订单ID不存在"

    def test_mark_order_shipped_already_shipped(self):
        """
        测试标记已经发货的订单为“已发货”。
        """
        # 创建新订单
        test_mark_order_shipped_already_shipped = []
        for i in range(3, 5):
            tmp_tuple = (self.buy_book_id_list[i], 1)
            test_mark_order_shipped_already_shipped.append(tmp_tuple)
        code, order_id = self.buyer.new_order(self.store_id, test_mark_order_shipped_already_shipped)
        assert code == 200, f"创建订单失败"

        code = self.buyer.payment(order_id)
        assert code == 200, f"支付失败"

        # 标记订单为已发货
        code = self.seller.mark_order_shipped(order_id)
        assert code == 200, "标记订单为已发货失败"
        self.already_order_id.append(order_id)

        for already_order_id in self.already_order_id:
            # 第二次标记同一订单为已发货，应失败
            code = self.seller.mark_order_shipped(already_order_id)
            assert code != 200, "应返回错误代码，因为订单已标记为已发货"

