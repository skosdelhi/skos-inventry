import os

#SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://org_user:khirod123@localhost/social_org_db")
#SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://skos_db_user:8djNQZNWXXNgFx7RUgrQQrKYnd0oyev5@dpg-d26bpkali9vc73d4bhg0-a/skos_db")

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
SQLALCHEMY_TRACK_MODIFICATIONS = False
#SECRET_KEY = "super-secret-key"
SECRET_KEY = os.getenv("SECRET_KEY")
