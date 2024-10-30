import requests
from urllib.parse import urljoin


class Auth:
    def __init__(self, url_prefix):
        self.url_prefix = urljoin(url_prefix, "auth/")

    def login(self, user_id: str, password: str, terminal: str) -> (int, str):
        json = {"user_id": user_id, "password": password, "terminal": terminal}
        url = urljoin(self.url_prefix, "login")
        r = requests.post(url, json=json)
        return r.status_code, r.json().get("token")

    def register(self, user_id: str, password: str) -> int:
        json = {"user_id": user_id, "password": password}
        url = urljoin(self.url_prefix, "register")
        r = requests.post(url, json=json)
        return r.status_code

    def password(self, user_id: str, old_password: str, new_password: str) -> int:
        json = {
            "user_id": user_id,
            "oldPassword": old_password,
            "newPassword": new_password,
        }
        url = urljoin(self.url_prefix, "password")
        r = requests.post(url, json=json)
        return r.status_code

    def logout(self, user_id: str, token: str) -> int:
        json = {"user_id": user_id}
        headers = {"token": token}
        url = urljoin(self.url_prefix, "logout")
        r = requests.post(url, headers=headers, json=json)
        return r.status_code

    def unregister(self, user_id: str, password: str) -> int:
        json = {"user_id": user_id, "password": password}
        url = urljoin(self.url_prefix, "unregister")
        r = requests.post(url, json=json)
        return r.status_code

    # 为更新信用分添加一个请求
    def update_credit(self, user_id: str, points: int) -> int:
        json = {"user_id": user_id, "points": points}
        url = urljoin(self.url_prefix, "update_credit")
        r = requests.post(url, json=json)
        return r.status_code

    # 为设置信用分添加一个请求
    def set_credit_score(self, user_id: str, score: int) -> int:
        json = {"user_id": user_id, "score": score}
        url = urljoin(self.url_prefix, "set_credit_score")
        r = requests.post(url, json=json)
        return r.status_code

    def confirm_receipt(self, user_id: str, order_id: str) -> int:
        json = {"user_id": user_id, "order_id": order_id}
        url = urljoin(self.url_prefix, "confirm_receipt")
        r = requests.post(url, json=json)
        return r.status_code

    def auto_confirm_receipt(self) -> int:
        url = urljoin(self.url_prefix, "auto_confirm_receipt")
        r = requests.post(url)
        return r.status_code

