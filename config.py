import os

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://org_user:khirod123@localhost/social_org_db")
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "super-secret-key"