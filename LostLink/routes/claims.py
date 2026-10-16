from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.mongo import get_db
from bson.objectid import ObjectId
from datetime import datetime

claims_bp = Blueprint('claims', __name__)

@claims_bp.route('/claim/<match_id>', methods=['GET', 'POST'])
def claim_item(match_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    db = get_db()
    try:
        match = db.matches.find_one({"_id": ObjectId(match_id)})
    except:
        return render_template('404.html'), 404
        
    if not match:
        return render_template('404.html'), 404
        
    if request.method == 'POST':
        message = request.form.get('message')
        
        claim_doc = {
            "match_id": match['_id'],
            "claimant_id": ObjectId(session['user_id']),
            "item_id": match['found_item_id'],
            "message": message,
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        
        db.claims.insert_one(claim_doc)
        db.matches.update_one({"_id": match['_id']}, {"$set": {"status": "claimed"}})
        
        flash('Claim submitted successfully. Awaiting review.', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('claim_item.html', match=match)
