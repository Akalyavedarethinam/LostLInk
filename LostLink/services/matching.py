import difflib
from datetime import datetime
from database.mongo import get_db
from services.notifications import create_notification
from flask import current_app

def calculate_text_similarity(text1, text2):
    if not text1 or not text2:
        return 0
    t1 = str(text1).lower().strip()
    t2 = str(text2).lower().strip()
    if t1 == t2:
        return 100.0
    return difflib.SequenceMatcher(None, t1, t2).ratio() * 100.0

def calculate_match_score(lost_item, found_item):
    # Name Similarity = 30%
    name_sim = calculate_text_similarity(lost_item.get('item_name', ''), found_item.get('item_name', ''))
    
    # Category Match = 20%
    category_sim = 100.0 if lost_item.get('category') == found_item.get('category') else 0.0
    
    # Location Match = 20%
    loc_sim = calculate_text_similarity(lost_item.get('location', ''), found_item.get('location', ''))
    
    # Date Similarity = 10%
    try:
        if isinstance(lost_item.get('date'), str):
            lost_date = datetime.strptime(lost_item.get('date'), '%Y-%m-%d')
        else:
            lost_date = lost_item.get('date')
            
        if isinstance(found_item.get('date'), str):
            found_date = datetime.strptime(found_item.get('date'), '%Y-%m-%d')
        else:
            found_date = found_item.get('date')
            
        delta = abs((found_date - lost_date).days)
        if delta == 0:
            date_sim = 100.0
        elif delta == 1:
            date_sim = 90.0
        elif delta == 2:
            date_sim = 75.0
        elif delta == 3:
            date_sim = 60.0
        elif 4 <= delta <= 7:
            date_sim = 40.0
        else:
            date_sim = 20.0
    except Exception:
        date_sim = 0.0

    # Description Similarity = 20%
    desc_sim = calculate_text_similarity(lost_item.get('description', ''), found_item.get('description', ''))

    total_score = (
        (0.30 * name_sim) +
        (0.20 * category_sim) +
        (0.20 * loc_sim) +
        (0.10 * date_sim) +
        (0.20 * desc_sim)
    )
    
    return {
        "score": round(total_score, 2),
        "breakdown": {
            "name": round(name_sim, 2),
            "category": round(category_sim, 2),
            "location": round(loc_sim, 2),
            "date": round(date_sim, 2),
            "description": round(desc_sim, 2)
        }
    }

def get_match_level(score):
    if score >= 90:
        return "Very Strong Match"
    elif score >= 75:
        return "Strong Match"
    elif score >= 50:
        return "Possible Match"
    else:
        return "Low Match"

def generate_matches_for_item(item):
    db = get_db()
    if db is None:
        return
        
    threshold = current_app.config.get('MATCH_THRESHOLD', 50)
    
    if item['type'] == 'lost':
        opposite_items = db.items.find({"type": "found", "status": "active"})
    else:
        opposite_items = db.items.find({"type": "lost", "status": "active"})
        
    for opp in opposite_items:
        # Check if match already exists
        lost_id = item['_id'] if item['type'] == 'lost' else opp['_id']
        found_id = opp['_id'] if item['type'] == 'lost' else item['_id']
        
        existing_match = db.matches.find_one({
            "lost_item_id": lost_id,
            "found_item_id": found_id
        })
        
        if existing_match:
            continue
            
        lost_item = item if item['type'] == 'lost' else opp
        found_item = opp if item['type'] == 'lost' else item
            
        match_result = calculate_match_score(lost_item, found_item)
        score = match_result['score']
        
        if score >= threshold:
            match_doc = {
                "lost_item_id": lost_id,
                "found_item_id": found_id,
                "lost_user_id": lost_item['user_id'],
                "found_user_id": found_item['user_id'],
                "match_score": score,
                "match_level": get_match_level(score),
                "breakdown": match_result['breakdown'],
                "status": "pending",
                "created_at": datetime.utcnow()
            }
            res = db.matches.insert_one(match_doc)
            match_id = res.inserted_id
            
            # Notify lost user
            create_notification(
                lost_item['user_id'],
                match_id,
                f"A potential match was found for your '{lost_item['item_name']}'.",
                score
            )
            # Notify found user
            create_notification(
                found_item['user_id'],
                match_id,
                f"A potential match was found for the '{found_item['item_name']}' you found.",
                score
            )
