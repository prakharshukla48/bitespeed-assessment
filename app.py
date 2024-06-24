from flask import Flask, request, jsonify
from models import Contact
from database import db, init_db
import datetime
import os
from config import config
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for
import time, hashlib

load_dotenv()

app = Flask(__name__, template_folder='templates')
env_name = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env_name])
init_db(app)
tokens = {}

def verify_token(token):
    token_data = tokens.get(token)
    if not token_data:
        return None
    if token_data["expires_at"] < time.time():
        del tokens[token]
        return None
    return token_data["email"]

def token_required(f):
    def wrap(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer"):
            return jsonify({"msg": "Missing or invalid token"}), 401

        token = auth_header.split(" ")[1]
        email = verify_token(token)
        if not email:
            return jsonify({"msg": "Invalid or expired token"}), 401

        request.user_email = email
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap


def generate_token(email, expires_in=3600):
    expiration_time = time.time() + expires_in
    token = hashlib.sha256(f"{email}{expiration_time}{app.secret_key}".encode()).hexdigest()
    tokens[token] = {"email": email, "expires_at": expiration_time}
    return token

@app.route("/submit", methods=['POST'])
def submit():
    user_email = request.form['email']
    user_phone = request.form['phone']
    try:
        contact = Contact.query.filter_by(email=user_email, phone_number=user_phone).first()
    except :
        return f" email : {user_email} or phone : {user_phone} not found"
    if contact :
        token = generate_token(contact.email)
        return f'Thank you, {contact.email}!. here is your access token {token}'
    else:
        return jsonify({"msg": "Invalid credentials"}), 401


@app.route("/register", methods=['POST'])
def register():
    user_email = request.form['email']
    user_phone = request.form['phone']
    primary_contact_id = Contact.query.count() + 1
    new_contact = Contact(email=user_email,
                          phone_number=user_phone,
                          linked_id=None,
                          link_precedence="Primary",
                          created_at=datetime.datetime.now(),
                          updated_at=datetime.datetime.now(),
                          deleted_at=None)
    db.session.add(new_contact)
    db.session.commit()
    return f'Thank you, {user_email} for registering!'


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route('/home')
def home():
    return "Hello welcome to the app, please use endpoint : 'https://uniqueaccounts.onrender.com/identify' to test the usecases for the assignment ";



@app.route('/identify', methods=['POST'])
@token_required
def identify():
    data = request.get_json()
    email = data.get('email')
    phone_number = data.get('phoneNumber')
    primary_email, primary_phone = None, None

    if email:
        primary_email = Contact.query.filter_by(email=email).first()
    if phone_number:
        primary_phone = Contact.query.filter_by(phone_number=phone_number).first()

    if primary_email and primary_phone:
        print("both email and phone found")

        linked_id_email = primary_email.linked_id
        linked_id_phone = primary_phone.linked_id
        if linked_id_email == linked_id_phone == None:
            primary_phone.linked_id = primary_email.id
            primary_phone.link_precedence = "Secondary"
            primary_phone.updated_at = datetime.datetime.now()
            db.session.commit()
            primary_contact_id = primary_email.id
        elif linked_id_email:
            primary_contact_id = linked_id_email
        elif linked_id_phone:
            primary_contact_id = linked_id_phone

    elif primary_email or primary_phone:
        print("Either of them present")
        if primary_email:
            linked_id = primary_email.linked_id
            if not linked_id:
                primary_contact_id = primary_email.id
            else:
                primary_contact_id = linked_id
            if phone_number:
                new_contact = Contact(email=email,
                                      phone_number=phone_number,
                                      linked_id=primary_contact_id,
                                      link_precedence= "Secondary",
                                      created_at= datetime.datetime.now(),
                                      updated_at= datetime.datetime.now(),
                                      deleted_at=None)
                db.session.add(new_contact)
                db.session.commit()

        else:

            linked_id = primary_phone.linked_id
            if not linked_id:
                primary_contact_id = primary_phone.id
            else:
                primary_contact_id = linked_id
            if email:
                new_contact = Contact(email=email,
                                      phone_number=phone_number,
                                      linked_id=primary_contact_id,
                                      link_precedence="Secondary",
                                      created_at=datetime.datetime.now(),
                                      updated_at=datetime.datetime.now(),
                                      deleted_at=None)
                db.session.add(new_contact)
                db.session.commit()
    else:
        if email or phone_number:
            primary_contact_id = Contact.query.count() + 1
            new_contact = Contact(email=email,
                                  phone_number=phone_number,
                                  linked_id=None,
                                  link_precedence="Primary",
                                  created_at=datetime.datetime.now(),
                                  updated_at=datetime.datetime.now(),
                                  deleted_at=None)
            db.session.add(new_contact)
            db.session.commit()
        else:
            return "No contact details were provided"

    secondary_contacts = Contact.query.filter_by(linked_id=primary_contact_id).all()
    secondary_contact_ids = [contact.id for contact in secondary_contacts]
    emails = [contact.email for contact in secondary_contacts] + [Contact.query.get(primary_contact_id).email]
    phone_numbers = [contact.phone_number for contact in secondary_contacts] + [Contact.query.get(primary_contact_id).phone_number]

    response = {
        "contact": {
            "primaryContactId": primary_contact_id,
            "emails": list(set(emails)),
            "phoneNumbers": list(set(phone_numbers)),
            "secondaryContactIds": secondary_contact_ids
        }
    }
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
