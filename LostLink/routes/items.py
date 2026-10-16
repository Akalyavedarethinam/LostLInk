from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, send_from_directory
from database.mongo import get_db
from services.matching import generate_matches_for_item
from bson.objectid import ObjectId
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import re

items_bp = Blueprint('items', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@items_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@items_bp.route('/report/lost', methods=['GET', 'POST'])
def report_lost():
    if 'user_id' not in session:
        flash('Please login to report an item.', 'warning')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        return process_report('lost')
        
    return render_template('report_item.html', report_type='lost')

@items_bp.route('/report/found', methods=['GET', 'POST'])
def report_found():
    if 'user_id' not in session:
        flash('Please login to report an item.', 'warning')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        return process_report('found')
        
    return render_template('report_item.html', report_type='found')

def process_report(type_str):
    db = get_db()
    item_name = request.form.get('item_name')
    category = request.form.get('category')
    description = request.form.get('description')
    location = request.form.get('location')
    date_str = request.form.get('date')
    
    if not all([item_name, category, location, date_str]):
        flash('Please fill out all required fields.', 'danger')
        return redirect(request.url)
        
    filename = ""
    file = request.files.get('image')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to prevent overwriting
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

    item_doc = {
        "user_id": ObjectId(session['user_id']),
        "type": type_str,
        "item_name": item_name,
        "category": category,
        "description": description,
        "location": location,
        "date": date_str,
        "image": filename,
        "status": "active",
        "created_at": datetime.utcnow()
    }
    
    res = db.items.insert_one(item_doc)
    item_doc['_id'] = res.inserted_id
    
    flash(f'{type_str.capitalize()} item reported successfully.', 'success')
    
    # Trigger matching
    generate_matches_for_item(item_doc)
    
    return redirect(url_for('main.dashboard'))

@items_bp.route('/browse')
def browse():
    db = get_db()
    query = {"status": {"$in": ["active", "matched"]}}
    
    item_type = request.args.get('type')
    category = request.args.get('category')
    keyword = request.args.get('keyword')
    
    if item_type and item_type in ['lost', 'found']:
        query['type'] = item_type
    if category and category != 'All':
        query['category'] = category
    if keyword:
        # Regex search for keyword in name, description, location
        regex = re.compile(keyword, re.IGNORECASE)
        query['$or'] = [
            {'item_name': regex},
            {'description': regex},
            {'location': regex}
        ]
        
    items = list(db.items.find(query).sort("created_at", -1))
    return render_template('browse.html', items=items)

@items_bp.route('/item/<item_id>')
def item_details(item_id):
    db = get_db()
    try:
        item = db.items.find_one({"_id": ObjectId(item_id)})
    except:
        return render_template('404.html'), 404
        
    if not item:
        return render_template('404.html'), 404
        
    reporter = db.users.find_one({"_id": item['user_id']})
    
    # Check if user has matches for this item
    matches = []
    if 'user_id' in session and str(item['user_id']) == session['user_id']:
        match_query = {"lost_item_id": item['_id']} if item['type'] == 'lost' else {"found_item_id": item['_id']}
        matches = list(db.matches.find(match_query))
        
    return render_template('item_details.html', item=item, reporter=reporter, matches=matches)
