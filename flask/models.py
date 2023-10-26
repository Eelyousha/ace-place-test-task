import datetime
import uuid

from mongoengine import *


class Target(Document):
    id = UUIDField(binary=False, default=lambda: str(uuid.uuid4()), primary_key=True)

    meta = {"allow_inheritance": False}


class User(Document):
    id = UUIDField(binary=False, default=lambda: str(uuid.uuid4()), primary_key=True)
    email = EmailField()

    meta = {"allow_inheritance": False}


class Notification(Document):
    id = UUIDField(binary=False, default=lambda: str(uuid.uuid4()), primary_key=True)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
    is_new = BooleanField(default=True)
    user_id = ReferenceField(User, required=True)
    key = StringField()
    target_id = ReferenceField(Target, required=False)
    data = DictField(required=False)

    meta = {"allow_inheritance": False}
