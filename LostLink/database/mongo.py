from pymongo import MongoClient
import sys

db = None
client = None

def init_db(app):
    global db, client
    try:
        client = MongoClient(app.config["MONGO_URI"], serverSelectionTimeoutMS=5000)
        # Verify connection
        client.admin.command('ping')
        db = client[app.config["DATABASE_NAME"]]
        
        # Create indexes
        db.users.create_index("email", unique=True)
        db.items.create_index("type")
        db.items.create_index("category")
        db.items.create_index("location")
        db.items.create_index("status")
        db.matches.create_index("lost_item_id")
        db.matches.create_index("found_item_id")
        db.notifications.create_index("user_id")
        db.claims.create_index("claimant_id")
        
        print("Successfully connected to MongoDB.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Please make sure MongoDB is running and MONGO_URI is correct.")
        
def get_db():
    return db
