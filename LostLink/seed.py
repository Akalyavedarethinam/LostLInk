from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import os
import sys

# Add the project directory to sys.path to import matching logic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "lostlink")

def seed_db():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    
    print("Clearing existing data...")
    db.users.drop()
    db.items.drop()
    db.matches.drop()
    db.notifications.drop()
    db.claims.drop()
    
    print("Creating users...")
    admin_id = db.users.insert_one({
        "name": "Admin User",
        "email": "admin@lostlink.com",
        "password": generate_password_hash("Admin@123"),
        "role": "admin",
        "created_at": datetime.utcnow()
    }).inserted_id
    
    user1_id = db.users.insert_one({
        "name": "Alice Smith",
        "email": "user1@lostlink.com",
        "password": generate_password_hash("User@123"),
        "role": "user",
        "created_at": datetime.utcnow()
    }).inserted_id
    
    user2_id = db.users.insert_one({
        "name": "Bob Johnson",
        "email": "user2@lostlink.com",
        "password": generate_password_hash("User@123"),
        "role": "user",
        "created_at": datetime.utcnow()
    }).inserted_id
    
    print("Creating items...")
    # Lost Items
    lost1 = {
        "user_id": user1_id,
        "type": "lost",
        "item_name": "Black Wallet",
        "category": "Wallet",
        "location": "College Library",
        "date": (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d'),
        "description": "Black leather wallet with my college ID and some cash.",
        "image": "",
        "status": "active",
        "created_at": datetime.utcnow()
    }
    lost1_id = db.items.insert_one(lost1).inserted_id
    lost1['_id'] = lost1_id
    
    lost2 = {
        "user_id": user2_id,
        "type": "lost",
        "item_name": "MacBook Pro Charger",
        "category": "Electronics",
        "location": "Cafeteria",
        "date": (datetime.utcnow() - timedelta(days=5)).strftime('%Y-%m-%d'),
        "description": "White Apple charger with a slight scuff mark on the side.",
        "image": "",
        "status": "active",
        "created_at": datetime.utcnow()
    }
    db.items.insert_one(lost2)
    
    # Found Items
    found1 = {
        "user_id": user2_id,
        "type": "found",
        "item_name": "Black Leather Wallet",
        "category": "Wallet",
        "location": "College Library",
        "date": (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d'),
        "description": "Found a black wallet containing a student ID.",
        "image": "",
        "status": "active",
        "created_at": datetime.utcnow()
    }
    found1_id = db.items.insert_one(found1).inserted_id
    found1['_id'] = found1_id
    
    print("Generating matches...")
    # For matching to work in seed script outside flask context, we use the raw logic
    from services.matching import calculate_match_score, get_match_level
    from services.notifications import create_notification
    
    # Mocking flask app context for get_db
    import services.notifications
    services.notifications.get_db = lambda: db
    import services.matching
    services.matching.get_db = lambda: db
    
    # Calculate match
    score_data = calculate_match_score(lost1, found1)
    score = score_data['score']
    
    if score >= 50:
        match_doc = {
            "lost_item_id": lost1_id,
            "found_item_id": found1_id,
            "lost_user_id": user1_id,
            "found_user_id": user2_id,
            "match_score": score,
            "match_level": get_match_level(score),
            "breakdown": score_data['breakdown'],
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        match_id = db.matches.insert_one(match_doc).inserted_id
        
        db.notifications.insert_one({
            "user_id": user1_id,
            "match_id": match_id,
            "message": f"A potential match was found for your '{lost1['item_name']}'.",
            "match_score": score,
            "is_read": False,
            "created_at": datetime.utcnow()
        })
        
        db.notifications.insert_one({
            "user_id": user2_id,
            "match_id": match_id,
            "message": f"A potential match was found for the '{found1['item_name']}' you found.",
            "match_score": score,
            "is_read": False,
            "created_at": datetime.utcnow()
        })

    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_db()
