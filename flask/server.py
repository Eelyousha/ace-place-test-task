import json
import os

from enum import Enum

from models import Notification, Target, User
from smtp_client import SMTPServer

import mongoengine as me

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from mongoengine.queryset.visitor import Q


class Key(Enum):
    registration = "registration"
    new_message = "new_message"
    new_post = "new_post"
    new_login = "new_login"


app = Flask(__name__)


@app.route("/create_user", methods=["POST"])
def create_user():
    user_email = request.json.get("email")
    user = User(email=user_email)
    try:
        user.save()
    except me.ValidationError as e:
        return jsonify({"success": False, "status": "Incorrect email"}), 400

    return jsonify({"success": True, "new_user_data": user.to_mongo()}), 201


@app.route("/create", methods=["POST"])
def create_notification():
    def create_db_object(u_id, target_id, data):
        new_notification = Notification()
        new_notification.user_id = User(id=u_id)
        new_notification.target_id = target_id
        new_notification.data = data
        new_notification.save()

    u_id = request.json.get("user_id")
    target_id = request.json.get("target_id")
    key = request.json.get("key")
    data = request.json.get("data")

    if u_id is None:
        return jsonify({"success": False, "status": "No user_id passed"}), 400
    if not User.objects(id=u_id):
        return jsonify({"success": False, "status": "No such user_id"}), 400

    if (target_id is not None) and (not Target.objects(id=target_id)):
        return jsonify({"success": False, "status": "No such target_id"}), 400

    try:
        match key:
            case Key.registration.value:
                user_mail = User.objects(id=u_id).get().email
                SMTPServer().send_message(user_mail, key)
            case Key.new_message.value:
                create_db_object(u_id=u_id, target_id=target_id, data=data)
            case Key.new_post.value:
                create_db_object(u_id=u_id, target_id=target_id, data=data)
            case Key.new_login.value:
                create_db_object(u_id=u_id, target_id=target_id, data=data)
                user_mail = User(id=u_id).email
                SMTPServer().send_message(user_mail, key)
            case _:
                return "Incorrect key value", 400
    except Exception as e:
        return jsonify({"status": str(e)}), 400
    return jsonify({"success": True}), 201


@app.route("/list", methods=["GET"])
def list_notifications():
    u_id = request.args.get("user_id")
    skip = int(request.args.get("skip", 0))
    limit = int(request.args.get("limit", 10))

    if u_id is None:
        user_messages = Notification.objects
    else:
        user_messages = Notification.objects(user_id=User(id=u_id))
    user_messages = user_messages[skip:limit]

    user_messages_list = json.loads(user_messages.to_json())
    return (
        jsonify(
            {
                "success": True,
                "data": {
                    "elements": user_messages.count(),
                    "new": user_messages.filter(is_new=True).count(),
                    "request": {"user_id": u_id, "skip": skip, "limit": limit},
                    "list": user_messages_list,
                },
            }
        ),
        200,
    )


@app.route("/read", methods=["POST"])
def mark_as_read():
    u_id = request.json.get("user_id")
    n_id = request.json.get("notification_id")

    user_to_read = User(id=u_id)
    Notification.objects(Q(user_id=user_to_read) | Q(id=n_id)).update(is_new=False)

    return (
        jsonify(
            {
                "success": True,
            }
        ),
        200,
    )


if __name__ == "__main__":
    load_dotenv()
    DB_URI = os.getenv("DB_URI")
    PORT = os.getenv("PORT", 9090)
    me.connect(host=DB_URI)
    app.run(host="0.0.0.0", port=PORT)
