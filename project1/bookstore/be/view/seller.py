from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import seller
import json
from bson import ObjectId

bp_seller = Blueprint("seller", __name__, url_prefix="/seller")


@bp_seller.route("/create_store", methods=["POST"])
def seller_create_store():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    s = seller.Seller()
    code, message = s.create_store(user_id, store_id)
    return jsonify({"message": message}), code


@bp_seller.route("/add_book", methods=["POST"])
def seller_add_book():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_info: str = request.json.get("book_info")
    stock_level: str = request.json.get("stock_level", 0)

    s = seller.Seller()
    code, message = s.add_book(
        user_id, store_id, book_info.get("id"), json.dumps(book_info), book_info.get("title"), book_info.get("price"),
        stock_level
    )

    return jsonify({"message": message}), code


@bp_seller.route("/add_stock_level", methods=["POST"])
def add_stock_level():
    user_id: str = request.json.get("user_id")
    store_id: str = request.json.get("store_id")
    book_id: str = request.json.get("book_id")
    add_num: str = request.json.get("add_stock_level", 0)

    s = seller.Seller()
    code, message = s.add_stock_level(user_id, store_id, book_id, add_num)

    return jsonify({"message": message}), code

def convert_objectid_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(i) for i in obj]
    return obj

@bp_seller.route("/get_book_rank10", methods=["POST"])
def get_book_rank10():
    s = seller.Seller()
    code, book_info = s.get_book_rank10()
    print("view",code)
    # print("view_book_info", book_info)
    # book_info_json = json.dumps(book_info)
    book_info = convert_objectid_to_str(book_info)
    response = jsonify({"book_info": book_info})
    response.status_code = code  # 设置响应的状态码
    return response  # 直接返回响应对象

@bp_seller.route("/mark_order_shipped", methods=["POST"])
def mark_order_shipped():
    order_id = request.json.get("order_id")
    s = seller.Seller()
    code, message = s.mark_order_shipped(order_id)
    return jsonify({"message": message}), code

