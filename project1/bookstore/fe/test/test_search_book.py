import base64

import pytest

import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fe import conf
from fe.access.new_seller import register_new_seller
from fe.access import book
import uuid
from fe.access.new_buyer import register_new_buyer

if sys.stdout.encoding != 'utf-8':
    # 使用 UTF-8 重定向标准输出
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class TestSearchBook:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        # do before test
        self.seller_id = "test_search_books_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_search_books_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_search_books_buyer_id_{}".format(str(uuid.uuid1()))
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

            # 创建一个 HTML 文件以存储结果
            result_file_path = "E:/GitHub/DataBase_Bookstore/project1/bookstore/fe/search_id_result.html"
            # 确保目录存在
            os.makedirs(os.path.dirname(result_file_path), exist_ok=True)

            # 设置每页显示书籍数量
            books_per_page = 10
            num_pages = (len(book) + books_per_page - 1) // books_per_page  # 计算总页数

            with open(result_file_path, 'w', encoding='utf-8') as file:
                # 写入 HTML 和 CSS 的开头
                file.write("""
                <html>
                <head>
                    <meta charset='utf-8'>
                    <title>查询结果</title>
                    <style>
                        .page { display: none; }
                        .active { display: block; }
                        .button-container { margin-top: 20px; }
                        .button-container button { padding: 10px; margin: 5px; }
                    </style>
                </head>
                <body>
                    <h1>查询结果</h1>
                """)

                # 创建每一页的内容
                for page in range(num_pages):
                    file.write(f"<div class='page' id='page-{page + 1}'>")
                    file.write(f"<h2>第 {page + 1} 页</h2>\n<ul>\n")

                    # 当前页的起始和结束索引
                    start_index = page * books_per_page
                    end_index = min(start_index + books_per_page, len(book))

                    for item in book[start_index:end_index]:
                        decoded_book_info = json.loads(item['book_info'])
                        item['book_info'] = decoded_book_info  # 更新 item 中的 book_info

                        # 输出书籍信息到 HTML 文件
                        file.write("<li>\n")
                        for key, value in item.items():
                            if key == 'book_info':
                                file.write(f"<strong>{key}:</strong><br>\n")
                                for info_key, info_value in value.items():
                                    file.write(f"&nbsp;&nbsp;<strong>{info_key}:</strong> {info_value}<br>\n")
                            else:
                                file.write(f"<strong>{key}:</strong> {value}<br>\n")
                        file.write("</li>\n")

                    file.write("</ul>\n</div>")  # 结束当前页的无序列表

                # 添加 JavaScript 用于页面切换
                file.write("""
                    <div class="button-container">
                        <button onclick="changePage(-1)">上一页</button>
                        <button onclick="changePage(1)">下一页</button>
                    </div>

                    <script>
                        let currentPage = 1;
                        const totalPages = """ + str(num_pages) + """;

                        function showPage(page) {
                            document.querySelectorAll('.page').forEach(div => div.classList.remove('active'));
                            document.getElementById('page-' + page).classList.add('active');
                        }

                        function changePage(direction) {
                            currentPage += direction;
                            if (currentPage < 1) currentPage = 1;
                            if (currentPage > totalPages) currentPage = totalPages;
                            showPage(currentPage);
                        }

                        // 初始化显示第一页
                        showPage(currentPage);
                    </script>
                </body>
                </html>
                """)

            # 可以直接输出查看效果
            print(f"书籍信息已输出到 {result_file_path}")

            assert code == 200

    # 测试使用 id 查询不存在的图书
    def test_query_non_existing_book_withId(self):
        code,book = self.buyer.search_books("999")
        assert code != 200

    # 测试使用书名查询已存在的图书
    def test_query_existing_book_withName(self):
        title = "Sculpting in Time"
        encoded_tag = title.encode('unicode_escape').decode('utf-8')
        # 使用编码后的标签进行查询
        code, book = self.buyer.search_books(encoded_tag)
        # 创建一个 HTML 文件以存储结果
        result_file_path = "E:/GitHub/DataBase_Bookstore/project1/bookstore/fe/search_title_result.html"
        # 确保目录存在
        os.makedirs(os.path.dirname(result_file_path), exist_ok=True)

        # 设置每页显示书籍数量
        books_per_page = 10
        num_pages = (len(book) + books_per_page - 1) // books_per_page  # 计算总页数

        with open(result_file_path, 'w', encoding='utf-8') as file:
            # 写入 HTML 和 CSS 的开头
            file.write("""
            <html>
            <head>
                <meta charset='utf-8'>
                <title>查询结果</title>
                <style>
                    .page { display: none; }
                    .active { display: block; }
                    .button-container { margin-top: 20px; }
                    .button-container button { padding: 10px; margin: 5px; }
                </style>
            </head>
            <body>
                <h1>查询结果</h1>
            """)

            # 创建每一页的内容
            for page in range(num_pages):
                file.write(f"<div class='page' id='page-{page + 1}'>")
                file.write(f"<h2>第 {page + 1} 页</h2>\n<ul>\n")

                # 当前页的起始和结束索引
                start_index = page * books_per_page
                end_index = min(start_index + books_per_page, len(book))

                for item in book[start_index:end_index]:
                    decoded_book_info = json.loads(item['book_info'])
                    item['book_info'] = decoded_book_info  # 更新 item 中的 book_info

                    # 输出书籍信息到 HTML 文件
                    file.write("<li>\n")
                    for key, value in item.items():
                        if key == 'book_info':
                            file.write(f"<strong>{key}:</strong><br>\n")
                            for info_key, info_value in value.items():
                                file.write(f"&nbsp;&nbsp;<strong>{info_key}:</strong> {info_value}<br>\n")
                        else:
                            file.write(f"<strong>{key}:</strong> {value}<br>\n")
                    file.write("</li>\n")

                file.write("</ul>\n</div>")  # 结束当前页的无序列表

            # 添加 JavaScript 用于页面切换
            file.write("""
                <div class="button-container">
                    <button onclick="changePage(-1)">上一页</button>
                    <button onclick="changePage(1)">下一页</button>
                </div>

                <script>
                    let currentPage = 1;
                    const totalPages = """ + str(num_pages) + """;

                    function showPage(page) {
                        document.querySelectorAll('.page').forEach(div => div.classList.remove('active'));
                        document.getElementById('page-' + page).classList.add('active');
                    }

                    function changePage(direction) {
                        currentPage += direction;
                        if (currentPage < 1) currentPage = 1;
                        if (currentPage > totalPages) currentPage = totalPages;
                        showPage(currentPage);
                    }

                    // 初始化显示第一页
                    showPage(currentPage);
                </script>
            </body>
            </html>
            """)

        # 可以直接输出查看效果
        print(f"书籍信息已输出到 {result_file_path}")

        assert code == 200

    # 测试使用书名查询不存在的图书
    def test_query_non_existing_book_withName(self):
        title = "data science and engineering"
        encoded_tag = title.encode('unicode_escape').decode('utf-8')
        # 使用编码后的标签进行查询
        code, book = self.buyer.search_books(encoded_tag)
        # 创建一个 HTML 文件以存储结果
        result_file_path = "E:/GitHub/DataBase_Bookstore/project1/bookstore/fe/search_title_result.html"
        # 确保目录存在
        os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
        if code == 200:
            # 设置每页显示书籍数量
            books_per_page = 10
            num_pages = (len(book) + books_per_page - 1) // books_per_page  # 计算总页数

            with open(result_file_path, 'w', encoding='utf-8') as file:
                # 写入 HTML 和 CSS 的开头
                file.write("""
                <html>
                <head>
                    <meta charset='utf-8'>
                    <title>查询结果</title>
                    <style>
                        .page { display: none; }
                        .active { display: block; }
                        .button-container { margin-top: 20px; }
                        .button-container button { padding: 10px; margin: 5px; }
                    </style>
                </head>
                <body>
                    <h1>查询结果</h1>
                """)

                # 创建每一页的内容
                for page in range(num_pages):
                    file.write(f"<div class='page' id='page-{page + 1}'>")
                    file.write(f"<h2>第 {page + 1} 页</h2>\n<ul>\n")

                    # 当前页的起始和结束索引
                    start_index = page * books_per_page
                    end_index = min(start_index + books_per_page, len(book))

                    for item in book[start_index:end_index]:
                        decoded_book_info = json.loads(item['book_info'])
                        item['book_info'] = decoded_book_info  # 更新 item 中的 book_info

                        # 输出书籍信息到 HTML 文件
                        file.write("<li>\n")
                        for key, value in item.items():
                            if key == 'book_info':
                                file.write(f"<strong>{key}:</strong><br>\n")
                                for info_key, info_value in value.items():
                                    file.write(f"&nbsp;&nbsp;<strong>{info_key}:</strong> {info_value}<br>\n")
                            else:
                                file.write(f"<strong>{key}:</strong> {value}<br>\n")
                        file.write("</li>\n")

                    file.write("</ul>\n</div>")  # 结束当前页的无序列表

                # 添加 JavaScript 用于页面切换
                file.write("""
                    <div class="button-container">
                        <button onclick="changePage(-1)">上一页</button>
                        <button onclick="changePage(1)">下一页</button>
                    </div>

                    <script>
                        let currentPage = 1;
                        const totalPages = """ + str(num_pages) + """;

                        function showPage(page) {
                            document.querySelectorAll('.page').forEach(div => div.classList.remove('active'));
                            document.getElementById('page-' + page).classList.add('active');
                        }

                        function changePage(direction) {
                            currentPage += direction;
                            if (currentPage < 1) currentPage = 1;
                            if (currentPage > totalPages) currentPage = totalPages;
                            showPage(currentPage);
                        }

                        // 初始化显示第一页
                        showPage(currentPage);
                    </script>
                </body>
                </html>
                """)
        print(f"书籍信息已输出到 {result_file_path}")
        assert code != 200

    # 测试使用标签查询已存在的图书
    def test_query_existing_book_withTag(self):
        tag = "历史"
        encoded_tag = tag.encode('unicode_escape').decode('utf-8')
        # 使用编码后的标签进行查询
        code, book = self.buyer.search_books(encoded_tag)
        # 创建一个 HTML 文件以存储结果
        result_file_path = "E:/GitHub/DataBase_Bookstore/project1/bookstore/fe/search_tag_result.html"
        # 确保目录存在
        os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
        # 设置每页显示书籍数量
        books_per_page = 5
        num_pages = (len(book) + books_per_page - 1) // books_per_page  # 计算总页数

        with open(result_file_path, 'w', encoding='utf-8') as file:
            # 写入 HTML 和 CSS 的开头
            file.write("""
            <html>
            <head>
                <meta charset='utf-8'>
                <title>查询结果</title>
                <style>
                    .page { display: none; }
                    .active { display: block; }
                    .button-container { margin-top: 20px; }
                    .button-container button { padding: 10px; margin: 5px; }
                </style>
            </head>
            <body>
                <h1>查询结果</h1>
            """)

            # 创建每一页的内容
            for page in range(num_pages):
                file.write(f"<div class='page' id='page-{page + 1}'>")
                file.write(f"<h2>第 {page + 1} 页</h2>\n<ul>\n")

                # 当前页的起始和结束索引
                start_index = page * books_per_page
                end_index = min(start_index + books_per_page, len(book))

                for item in book[start_index:end_index]:
                    decoded_book_info = json.loads(item['book_info'])
                    item['book_info'] = decoded_book_info  # 更新 item 中的 book_info

                    # 输出书籍信息到 HTML 文件
                    file.write("<li>\n")
                    for key, value in item.items():
                        if key == 'book_info':
                            file.write(f"<strong>{key}:</strong><br>\n")
                            for info_key, info_value in value.items():
                                file.write(f"&nbsp;&nbsp;<strong>{info_key}:</strong> {info_value}<br>\n")
                        else:
                            file.write(f"<strong>{key}:</strong> {value}<br>\n")
                    file.write("</li>\n")

                file.write("</ul>\n</div>")  # 结束当前页的无序列表

            # 添加 JavaScript 用于页面切换
            file.write("""
                <div class="button-container">
                    <button onclick="changePage(-1)">上一页</button>
                    <button onclick="changePage(1)">下一页</button>
                </div>

                <script>
                    let currentPage = 1;
                    const totalPages = """ + str(num_pages) + """;

                    function showPage(page) {
                        document.querySelectorAll('.page').forEach(div => div.classList.remove('active'));
                        document.getElementById('page-' + page).classList.add('active');
                    }

                    function changePage(direction) {
                        currentPage += direction;
                        if (currentPage < 1) currentPage = 1;
                        if (currentPage > totalPages) currentPage = totalPages;
                        showPage(currentPage);
                    }

                    // 初始化显示第一页
                    showPage(currentPage);
                </script>
            </body>
            </html>
            """)

        # 可以直接输出查看效果
        print(f"书籍信息已输出到 {result_file_path}")
        assert code == 200

    # 测试使用标签查询不存在的图书
    def test_query_non_existing_book_withTag(self):
        tag = "dataengineering"
        encoded_tag = tag.encode('unicode_escape').decode('utf-8')
        # 使用编码后的标签进行查询
        code, book = self.buyer.search_books(encoded_tag)
        # 创建一个 HTML 文件以存储结果
        result_file_path = "E:/GitHub/DataBase_Bookstore/project1/bookstore/fe/search_tag_result.html"
        # 确保目录存在
        os.makedirs(os.path.dirname(result_file_path), exist_ok=True)
        if code == 200:
            # 设置每页显示书籍数量
            books_per_page = 10
            num_pages = (len(book) + books_per_page - 1) // books_per_page  # 计算总页数

            with open(result_file_path, 'w', encoding='utf-8') as file:
                # 写入 HTML 和 CSS 的开头
                file.write("""
                <html>
                <head>
                    <meta charset='utf-8'>
                    <title>查询结果</title>
                    <style>
                        .page { display: none; }
                        .active { display: block; }
                        .button-container { margin-top: 20px; }
                        .button-container button { padding: 10px; margin: 5px; }
                    </style>
                </head>
                <body>
                    <h1>查询结果</h1>
                """)

                # 创建每一页的内容
                for page in range(num_pages):
                    file.write(f"<div class='page' id='page-{page + 1}'>")
                    file.write(f"<h2>第 {page + 1} 页</h2>\n<ul>\n")

                    # 当前页的起始和结束索引
                    start_index = page * books_per_page
                    end_index = min(start_index + books_per_page, len(book))

                    for item in book[start_index:end_index]:
                        decoded_book_info = json.loads(item['book_info'])
                        item['book_info'] = decoded_book_info  # 更新 item 中的 book_info

                        # 输出书籍信息到 HTML 文件
                        file.write("<li>\n")
                        for key, value in item.items():
                            if key == 'book_info':
                                file.write(f"<strong>{key}:</strong><br>\n")
                                for info_key, info_value in value.items():
                                    file.write(f"&nbsp;&nbsp;<strong>{info_key}:</strong> {info_value}<br>\n")
                            else:
                                file.write(f"<strong>{key}:</strong> {value}<br>\n")
                        file.write("</li>\n")

                    file.write("</ul>\n</div>")  # 结束当前页的无序列表

                # 添加 JavaScript 用于页面切换
                file.write("""
                    <div class="button-container">
                        <button onclick="changePage(-1)">上一页</button>
                        <button onclick="changePage(1)">下一页</button>
                    </div>

                    <script>
                        let currentPage = 1;
                        const totalPages = """ + str(num_pages) + """;

                        function showPage(page) {
                            document.querySelectorAll('.page').forEach(div => div.classList.remove('active'));
                            document.getElementById('page-' + page).classList.add('active');
                        }

                        function changePage(direction) {
                            currentPage += direction;
                            if (currentPage < 1) currentPage = 1;
                            if (currentPage > totalPages) currentPage = totalPages;
                            showPage(currentPage);
                        }

                        // 初始化显示第一页
                        showPage(currentPage);
                    </script>
                </body>
                </html>
                """)

        print(f"书籍信息已输出到 {result_file_path}")
        assert code != 200