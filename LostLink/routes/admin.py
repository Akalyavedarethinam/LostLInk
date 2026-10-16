from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from database.mongo import get_db
from bson.objectid import ObjectId

admin_bp = Blueprint('admin', __name__)

def is_admin():
    return session.get('user_role') == 'admin'

@admin_bp.before_request
def check_admin():
    if not is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

@admin_bp.route('/dashboard')
def dashboard():
    db = get_db()
    stats = {
        "users": db.users.count_documents({}),
        "lost": db.items.count_documents({"type": "lost"}),
        "found": db.items.count_documents({"type": "found"}),
        "matches": db.matches.count_documents({"status": "pending"}),
        "claims": db.claims.count_documents({"status": "pending"}),
        "recovered": db.items.count_documents({"status": "recovered"})
    }
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
def users():
    db = get_db()
    all_users = list(db.users.find())
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/items')
def items():
    db = get_db()
    all_items = list(db.items.find().sort("created_at", -1))
    return render_template('admin/items.html', items=all_items)

@admin_bp.route('/items/delete/<item_id>')
def delete_item(item_id):
    db = get_db()
    db.items.delete_one({"_id": ObjectId(item_id)})
    db.matches.delete_many({"$or": [{"lost_item_id": ObjectId(item_id)}, {"found_item_id": ObjectId(item_id)}]})
    flash('Item deleted.', 'success')
    return redirect(url_for('admin.items'))

@admin_bp.route('/matches')
def matches():
    db = get_db()
    all_matches = list(db.matches.find().sort("created_at", -1))
    return render_template('admin/matches.html', matches=all_matches)

@admin_bp.route('/claims')
def claims():
    db = get_db()
    all_claims = list(db.claims.find().sort("created_at", -1))
    for claim in all_claims:
        claim['claimant'] = db.users.find_one({"_id": claim['claimant_id']})
    return render_template('admin/claims.html', claims=all_claims)

@admin_bp.route('/claims/approve/<claim_id>')
def approve_claim(claim_id):
    db = get_db()
    claim = db.claims.find_one({"_id": ObjectId(claim_id)})
    if claim:
        db.claims.update_one({"_id": ObjectId(claim_id)}, {"$set": {"status": "approved"}})
        # Mark items as recovered
        match = db.matches.find_one({"_id": claim['match_id']})
        if match:
            db.items.update_one({"_id": match['lost_item_id']}, {"$set": {"status": "recovered"}})
            db.items.update_one({"_id": match['found_item_id']}, {"$set": {"status": "recovered"}})
            db.matches.update_one({"_id": claim['match_id']}, {"$set": {"status": "recovered"}})
        flash('Claim approved. Items marked as recovered.', 'success')
    return redirect(url_for('admin.claims'))

@admin_bp.route('/claims/reject/<claim_id>')
def reject_claim(claim_id):
    db = get_db()
    db.claims.update_one({"_id": ObjectId(claim_id)}, {"$set": {"status": "rejected"}})
    flash('Claim rejected.', 'info')
    return redirect(url_for('admin.claims'))
