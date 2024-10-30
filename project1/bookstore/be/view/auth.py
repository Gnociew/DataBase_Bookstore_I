from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import user

bp_auth = Blueprint("auth", __name__, url_prefix="/auth")


@bp_auth.route("/login", methods=["POST"])
def login():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    terminal = request.json.get("terminal", "")
    u = user.User()
    code, message, token = u.login(
        user_id=user_id, password=password, terminal=terminal
    )
    return jsonify({"message": message, "token": token}), code


@bp_auth.route("/logout", methods=["POST"])
def logout():
    user_id: str = request.json.get("user_id")
    token: str = request.headers.get("token")
    u = user.User()
    code, message = u.logout(user_id=user_id, token=token)
    return jsonify({"message": message}), code


@bp_auth.route("/register", methods=["POST"])
def register():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.register(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/unregister", methods=["POST"])
def unregister():
    user_id = request.json.get("user_id", "")
    password = request.json.get("password", "")
    u = user.User()
    code, message = u.unregister(user_id=user_id, password=password)
    return jsonify({"message": message}), code


@bp_auth.route("/password", methods=["POST"])
def change_password():
    user_id = request.json.get("user_id", "")
    old_password = request.json.get("oldPassword", "")
    new_password = request.json.get("newPassword", "")
    u = user.User()
    code, message = u.change_password(
        user_id=user_id, old_password=old_password, new_password=new_password
    )
    return jsonify({"message": message}), code

@bp_auth.route("/update_credit", methods=["POST"])
def update_credit():
    user_id = request.json.get("user_id", "")
    points = request.json.get("points", 0)
    u = user.User()
    code, message = u.update_credit(user_id, points)
    return jsonify({"message": message}), code

@bp_auth.route("/set_credit_score", methods=["POST"])
def set_credit_score():
    user_id = request.json.get("user_id", "")
    score = request.json.get("score", 0)
    u = user.User()
    code, message = u.set_credit_score(user_id=user_id, score=score)
    return jsonify({"message": message}), code

@bp_auth.route("/confirm_receipt", methods=["POST"])
def confirm_receipt():
    user_id: str = request.json.get("user_id")
    order_id: str = request.json.get("order_id")
    u = user.User()
    code, message = u.confirm_receipt(user_id=user_id, order_id=order_id)
    return jsonify({"message": message}), code

@bp_auth.route("/auto_confirm_receipt", methods=["POST"])
def auto_confirm_receipt():
    u = user.User()
    code, message = u.auto_confirm_receipt()
    return jsonify({"message": message}), code