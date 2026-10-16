from datetime import datetime
from database.mongo import get_db

def create_notification(user_id, match_id, message, match_score):
    db = get_db()
    if db is None:
        return
    notification = {
        "user_id": user_id,
        "match_id": match_id,
        "message": message,
        "match_score": match_score,
        "is_read": False,
        "created_at": datetime.utcnow()
    }
    db.notifications.insert_one(notification)
