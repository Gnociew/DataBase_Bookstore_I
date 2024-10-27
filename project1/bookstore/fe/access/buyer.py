import requests
import simplejson
from urllib.parse import urljoin
from fe.access.auth import Auth


class Buyer:
    def __init__(self, url_prefix, user_id, password):
        self.url_prefix = urljoin(url_prefix, "buyer/")
        self.user_id = user_id
        self.password = password
        self.token = ""
        self.terminal = "my terminal"
        self.auth = Auth(url_prefix)
        code, self.token = self.auth.login(self.user_id, self.password, self.terminal)
        assert code == 200

    def new_order(self, store_id: str, book_id_and_count: [(str, int)]) -> (int, str):
        books = []
        for id_count_pair in book_id_and_count:
            books.append({"id": id_count_pair[0], "count": id_count_pair[1]})
        json = {"user_id": self.user_id, "store_id": store_id, "books": books}
        # print(simplejson.dumps(json))
        url = urljoin(self.url_prefix, "new_order")
        headers = {"token": self.token}
        # 发起 POST 请求
        try:
            r = requests.post(url, headers=headers, json=json)
            response_json = r.json()
            return r.status_code, response_json.get("order_id")

        except Exception as e:
            # 捕获异常并输出调试信息
            print(f"Exception occurred: {str(e)}")
            return 530, None

    def payment(self, order_id: str):
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "order_id": order_id,
        }
        url = urljoin(self.url_prefix, "payment")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def add_funds(self, add_value: str) -> int:
        json = {
            "user_id": self.user_id,
            "password": self.password,
            "add_value": add_value,
        }
        url = urljoin(self.url_prefix, "add_funds")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json)
        return r.status_code
    
        
    def search_books(self, key_words:str) :
        json_data = {
            "key_words":key_words,
        }
        # print(key_words,json_data)
        # print("access.buyer",key_words)
        url = urljoin(self.url_prefix, "search_books")
        headers = {"token": self.token}
        r = requests.post(url, headers=headers, json=json_data)
        # print("access",r.status_code)
        response_json = r.json()
        # print("access response json:", response_json)
        return r.status_code, response_json.get("book_info", {})  # 默认返回空字典
       

    # # 将订单标记为已发货
    # def shipping_order(self, order_id: str) -> int:
    #     url = urljoin(self.url_prefix, "shipping_order")  # 假设后端有这个 API
    #     headers = {"token": self.token}
    #     json = {"order_id": order_id}
    #
    #     r = requests.post(url, headers=headers, json=json)
    #     return r.status_code
    #
    # # 用户确认收货
    # def confirm_receipt(self, order_id: str) -> (int, str):
    #     url = urljoin(self.url_prefix, "confirm_receipt")  # 假设后端有这个 API
    #     headers = {"token": self.token}
    #     json = {"user_id": self.user_id, "order_id": order_id}
    #     response = requests.post(url, headers=headers, json=json)
    #     return response.status_code
    #
    # # 平台自动确认收货
    # def auto_confirm_receipt(self) -> (int, str):
    #     url = urljoin(self.url_prefix, "auto_confirm_receipt")  # 假设后端有这个 API
    #     headers = {"token": self.token}
    #     r = requests.post(url, headers=headers)
    #     return r.status_code
