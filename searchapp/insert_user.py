import os
import django
import sys

# Add the project root directory to Python's sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_search.settings')  # Replace 'company_search' with your project name
django.setup()

from pymongo import MongoClient
from django.contrib.auth.hashers import make_password

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['migration']
login_credentials_collection = db['login_credentials']

# User details
user_data = {
    "username": "tamil",  # Your desired username
    "password": make_password("123"),  # Hashed password
    "role": "superadmin"  # User role
}

# Insert the user into the login_credentials collection
login_credentials_collection.insert_one(user_data)

print("User inserted successfully with username 'tamil' and role 'superadmin'.")
