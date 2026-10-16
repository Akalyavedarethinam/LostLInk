# LostLink – Intelligent Lost & Found Management System

LostLink is a complete web application designed to help users report and find lost items intelligently. It uses a custom string-matching algorithm to calculate similarities between lost and found items.

## Features
- **User Authentication**: Register, Login, Session Management.
- **Intelligent Matching**: Algorithm uses weighted metrics (Name, Category, Location, Date, Description).
- **Match Notifications**: Alerts when high-probability matches occur.
- **Claims System**: Users can claim items with verification messages.
- **Admin Panel**: Manage users, items, matches, and approve claims.
- **REST API**: External access via `/api/items`, `/api/matches`, etc.
- **Responsive UI**: Built with Bootstrap 5.

## Technology Stack
- **Backend**: Python, Flask
- **Database**: MongoDB (PyMongo)
- **Frontend**: HTML, CSS, Bootstrap 5, Jinja2

## Setup on Windows
1. **Ensure MongoDB is running locally**: 
   Download and install MongoDB Community Server. Start the MongoDB service. Default URI is `mongodb://localhost:27017/`.

2. **Create and Activate Virtual Environment**:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Copy `.env.example` to `.env` (it will work out-of-the-box for local testing).

5. **Seed the Database (Demo Data)**:
   ```cmd
   python seed.py
   ```

6. **Run the Application**:
   ```cmd
   python app.py
   ```

7. **Access the App**:
   Open browser at `http://localhost:5000`

## Demo Login Credentials (from seed.py)
- **Admin**: admin@lostlink.com / Admin@123
- **User 1**: user1@lostlink.com / User@123
- **User 2**: user2@lostlink.com / User@123

## Running Tests
```cmd
python -m unittest tests/test_matching.py
```
