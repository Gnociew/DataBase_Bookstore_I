import pytest

from fe import conf
from fe.access.new_seller import register_new_seller
from fe.access import book
import uuid
from fe.access.new_buyer import register_new_buyer



class TestSearchBook:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # do before test
        self.seller_id = "test_add_books_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_add_books_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_payment_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id

        self.seller = register_new_seller(self.seller_id, self.password)
        self.buyer = register_new_buyer(self.buyer_id, self.password)

        code = self.seller.create_store(self.store_id)
        # print("错误检查：")
        # print(code)
        assert code == 200

        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, 100)
        # 插入所有图书
        for b in self.books:
            code = self.seller.add_book(self.store_id, 0, b)
            assert code == 200

        yield
        # do after test

    # 测试使用 id 查询已存在的图书
    def test_query_existing_book_withId(self):
            code,book = self.buyer.search_books("1000687")
            print(book)
            result_file_path = "fe/search_result.html"  # 前一级目录的文件路径

            with open(result_file_path, 'w', encoding='utf-8') as file:
                file.write(str(book))

            assert code == 200

    # 测试使用 id 查询不存在的图书
    def test_query_non_existing_book_withId(self):
        code,book = self.buyer.search_books("999")
        assert code != 200

    # 测试使用书名查询已存在的图书
    def test_query_existing_book_withName(self):
            code,book = self.buyer.search_books("Sculpting in Time")
            print(book)
            result_file_path = "fe/search_result.html"  # 前一级目录的文件路径

            with open(result_file_path, 'w', encoding='utf-8') as file:
                file.write(str(book))

            assert code == 200

    # 测试使用书名查询不存在的图书
    def test_query_non_existing_book_withName(self):
        code,book = self.buyer.search_books("数据科学与工程算法基础")
        assert code != 200

    # 测试使用标签查询已存在的图书
    def test_query_existing_book_withTag(self):
            code,book = self.buyer.search_books("Finance")
            print(book)
            result_file_path = "fe/search_result.html"  # 前一级目录的文件路径

            with open(result_file_path, 'w', encoding='utf-8') as file:
                file.write(str(book))

            assert code == 200

    # 测试使用标签查询已存在的图书
    def test_query_non_existing_book_withTag(self):
        code,book = self.buyer.search_books("数据科学")
        assert code != 200