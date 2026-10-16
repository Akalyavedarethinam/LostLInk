from flask import Blueprint, render_template, session, redirect, url_for, flash
from database.mongo import get_db
from bson.objectid import ObjectId

matches_bp = Blueprint('matches', __name__)

@matches_bp.route('/match/<match_id>')
def match_details(match_id):
    if 'user_id' not in session:
        flash('Please login to view match details.', 'warning')
        return redirect(url_for('auth.login'))
        
    db = get_db()
    try:
        match = db.matches.find_one({"_id": ObjectId(match_id)})
    except:
        return render_template('404.html'), 404
        
    if not match:
        return render_template('404.html'), 404
        
    user_id = str(session['user_id'])
    if str(match['lost_user_id']) != user_id and str(match['found_user_id']) != user_id and session.get('user_role') != 'admin':
        flash('Unauthorized to view this match.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    lost_item = db.items.find_one({"_id": match['lost_item_id']})
    found_item = db.items.find_one({"_id": match['found_item_id']})
    
    return render_template('match_details.html', match=match, lost_item=lost_item, found_item=found_item)
