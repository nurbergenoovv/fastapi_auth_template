from dotenv import load_dotenv
import os

load_dotenv()

# DATABASE
DATABASE_HOST = os.environ.get("DATABASE_HOST")
DATABASE_PORT = os.environ.get("DATABASE_PORT")
DATABASE_USERNAME = os.environ.get("DATABASE_USERNAME")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_NAME = os.environ.get("DATABASE_NAME")

# JWT
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

# SMTP
SMTP_SERVER= os.environ.get("SMTP_SERVER")
SMTP_PORT= os.environ.get("SMTP_PORT")
SMTP_USERNAME= os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD= os.environ.get("SMTP_PASSWORD")
MAIL_STARTTLS=os.environ.get("MAIL_STARTTLS")
MAIL_SSL_TLS=os.environ.get("MAIL_SSL_TLS")
VALIDATE_CERTS=os.environ.get("VALIDATE_CERTS")

# DOMAIN
DOMAIN_NAME = os.environ.get("DOMAIN_NAME")
RESET_PASS_URL = os.environ.get("RESET_PASS_URL")
