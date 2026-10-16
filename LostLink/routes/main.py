from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from database.mongo import get_db
from bson.objectid import ObjectId

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to view your dashboard.', 'warning')
        return redirect(url_for('auth.login'))
        
    db = get_db()
    user_id = ObjectId(session['user_id'])
    
    my_lost = list(db.items.find({"user_id": user_id, "type": "lost"}))
    my_found = list(db.items.find({"user_id": user_id, "type": "found"}))
    
    # Potential matches involving this user
    matches = list(db.matches.find({
        "$or": [
            {"lost_user_id": user_id},
            {"found_user_id": user_id}
        ],
        "status": {"$ne": "closed"}
    }).sort("created_at", -1))
    
    # Fetch item details for matches
    for match in matches:
        match['lost_item'] = db.items.find_one({"_id": match['lost_item_id']})
        match['found_item'] = db.items.find_one({"_id": match['found_item_id']})

    recovered = db.items.count_documents({"user_id": user_id, "status": "recovered"})

    return render_template('dashboard.html', 
                           my_lost=my_lost, 
                           my_found=my_found, 
                           matches=matches,
                           total_lost=len(my_lost),
                           total_found=len(my_found),
                           recovered=recovered)

@main_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    user_id = ObjectId(session['user_id'])
    
    if request.method == 'POST':
        new_name = request.form.get('name')
        if new_name:
            db.users.update_one({"_id": user_id}, {"$set": {"name": new_name}})
            session['user_name'] = new_name
            flash('Profile updated successfully.', 'success')
            
    user = db.users.find_one({"_id": user_id})
    stats = {
        'lost': db.items.count_documents({"user_id": user_id, "type": "lost"}),
        'found': db.items.count_documents({"user_id": user_id, "type": "found"}),
        'recovered': db.items.count_documents({"user_id": user_id, "status": "recovered"})
    }
    
    return render_template('profile.html', user=user, stats=stats)
