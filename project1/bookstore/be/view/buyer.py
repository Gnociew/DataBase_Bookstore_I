from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.buyer import Buyer
import json
from bson import ObjectId
from be.model.seller import Seller
from be.model.user import User

bp_buyer = Blueprint("buyer", __name__, url_prefix="/buyer")

@bp_buyer.route("/new_order", methods=["POST"])
def new_order():
    # 获取请求参数
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    books: [] = request.json.get("books")
    # 处理书籍信息
    id_and_count = [] # 书的ID和要购买的本数
    for book in books:
        book_id = book.get("id")
        count = book.get("count")
        id_and_count.append((book_id, count))

    b = Buyer()
    # 返回值
    code, message, order_id = b.new_order(user_id, store_id, id_and_count)
    return jsonify({"message": message, "order_id": order_id}), code


@bp_buyer.route("/payment", methods=["POST"])
def payment():
    # 获取请求参数
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    password: str = request.json.get("password")
    b = Buyer()
    # 返回值
    code, message = b.payment(user_id, password, order_id)
    return jsonify({"message": message}), code


@bp_buyer.route("/add_funds", methods=["POST"])
def add_funds():
    user_id = request.json.get("user_id")
    password = request.json.get("password")
    add_value = request.json.get("add_value")
    b = Buyer()
    code, message = b.add_funds(user_id, password, add_value)
    return jsonify({"message": message}), code

def convert_objectid_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(i) for i in obj]
    return obj

@bp_buyer.route("/search_books", methods=["POST"])
def search_books():
    key_words = request.json.get("key_words")
    # print("beview",key_words)
    b = Buyer()
    code, book_info = b.search_books(key_words)
    # print("view",code)
    # print("view_book_info", book_info)
    # book_info_json = json.dumps(book_info)
    book_info = convert_objectid_to_str(book_info)
    response = jsonify({"book_info": book_info})
    response.status_code = code  # 设置响应的状态码
    return response  # 直接返回响应对象

@bp_buyer.route("/view_finished_orders", methods=["POST"])
def view_finished_orders():
    user_id = request.json.get("user_id")
    # print("beview",key_words)
    b = Buyer()
    code, order = b.view_finished_orders(user_id)
    # print("view",code)
    # print("view_book_info", book_info)
    # book_info_json = json.dumps(book_info)
    order = convert_objectid_to_str(order)
    response = jsonify({"order": order})
    response.status_code = code  # 设置响应的状态码
    return response  # 直接返回响应对象

@bp_buyer.route("/cancel_order", methods=["POST"])
def cancel_order():
    """
    处理取消订单的请求。
    接收 JSON 数据中的 user_id 和 order_id，调用模型层的 cancel_order 方法。
    返回 JSON 响应和相应的状态码。
    """
    data = request.get_json()
    user_id = data.get("user_id")
    order_id = data.get("order_id")

    if not user_id or not order_id:
        return jsonify({"message": "缺少必要的参数"}), 400

    buyer_model = Buyer()
    code, msg = buyer_model.cancel_order(user_id, order_id)

    response = jsonify({"message": msg})
    response.status_code = code
    return response

@bp_buyer.route("/auto_cancel_order", methods=["POST"])
def auto_cancel_order():
    """
    处理自动取消订单的请求。
    """
    b = Buyer()
    code, msg = b.auto_cancel_order()
    response = jsonify({"message": msg})
    response.status_code = code
    return response
