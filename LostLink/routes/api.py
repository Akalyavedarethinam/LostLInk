from flask import Blueprint, jsonify, request
from database.mongo import get_db
from bson import json_util
import json

api_bp = Blueprint('api', __name__)

def parse_json(data):
    return json.loads(json_util.dumps(data))

@api_bp.route('/items', methods=['GET'])
def get_items():
    db = get_db()
    items = list(db.items.find())
    return jsonify(parse_json(items)), 200

@api_bp.route('/matches', methods=['GET'])
def get_matches():
    db = get_db()
    matches = list(db.matches.find())
    return jsonify(parse_json(matches)), 200

@api_bp.route('/notifications', methods=['GET'])
def get_notifications():
    db = get_db()
    # Expect user_id in params or headers, for simple API keep it open for demo
    user_id = request.args.get('user_id')
    if user_id:
        from bson.objectid import ObjectId
        notifs = list(db.notifications.find({"user_id": ObjectId(user_id)}))
    else:
        notifs = list(db.notifications.find())
    return jsonify(parse_json(notifs)), 200
