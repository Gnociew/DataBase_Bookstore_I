import pytest

from fe import conf
from fe.access.new_seller import register_new_seller
from fe.access import book
import uuid


class TestAddBook:
    # 使用 pytest.fixture 定义一个准备函数，在每个测试前执行
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # do before test
        self.seller_id = "test_add_books_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_add_books_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id

        self.seller = register_new_seller(self.seller_id, self.password)

        code = self.seller.create_store(self.store_id)
        # print("错误检查：")
        # print(code)
        assert code == 200
        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, 2)

        yield
        # do after test

    def test_ok(self):
        for b in self.books:
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200

    # 尝试向不存在的商店添加书籍，确保返回错误
    def test_error_non_exist_store_id(self):
        for b in self.books:
            # non exist store id
            code = self.seller.add_book(self.store_id + "x", 0, b)
            assert code != 200

    # 重复添加相同书籍的情况，确保第二次添加返回错误
    def test_error_exist_book_id(self):
        for b in self.books:
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200
        for b in self.books:
            # exist book id
            code = self.seller.add_book(self.store_id, 0, b)
            assert code != 200

    # 尝试使用不存在的卖家 ID 添加书籍，确保返回错误
    def test_error_non_exist_user_id(self):
        for b in self.books:
            # non exist user id
            self.seller.seller_id = self.seller.seller_id + "_x"
            code = self.seller.add_book(self.store_id, 0, b)
            assert code != 200