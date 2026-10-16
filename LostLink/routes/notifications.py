from flask import Blueprint, render_template, session, redirect, url_for, flash
from database.mongo import get_db
from bson.objectid import ObjectId

notif_bp = Blueprint('notifications', __name__)

@notif_bp.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    db = get_db()
    notifs = list(db.notifications.find({"user_id": ObjectId(session['user_id'])}).sort("created_at", -1))
    
    return render_template('notifications.html', notifications=notifs)

@notif_bp.route('/notifications/read/<notif_id>')
def mark_read(notif_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    db = get_db()
    db.notifications.update_one(
        {"_id": ObjectId(notif_id), "user_id": ObjectId(session['user_id'])},
        {"$set": {"is_read": True}}
    )
    return redirect(url_for('notifications.notifications'))
