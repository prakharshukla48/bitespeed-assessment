from flask import Flask, request, jsonify
from models import Contact
from database import db, init_db

app = Flask(__name__)
init_db(app)

@app.route('/identify', methods=['POST'])
def identify():
    data = request.get_json()
    email = data.get('email')
    phone_number = data.get('phoneNumber')
    primary_contact = None
    secondary_contacts = set()

    if email:
        primary_contact = Contact.query.filter_by(email=email).first()
    if not primary_contact and phone_number:
        primary_contact = Contact.query.filter_by(phone_number=phone_number).first()

    if primary_contact:
        primary_contact_id = primary_contact.primary_contact_id
    else:
        primary_contact_id = Contact.query.count() + 1
        new_contact = Contact(email=email, phone_number=phone_number, primary_contact_id=primary_contact_id)
        db.session.add(new_contact)
        db.session.commit()

    contacts = Contact.query.filter_by(primary_contact_id=primary_contact_id).all()
    emails = list({c.email for c in contacts if c.email})
    phone_numbers = list({c.phone_number for c in contacts if c.phone_number})
    secondary_contact_ids = [c.id for c in contacts if c.id != primary_contact_id]

    response = {
        "contact": {
            "primaryContactId": primary_contact_id,
            "emails": emails,
            "phoneNumbers": phone_numbers,
            "secondaryContactIds": secondary_contact_ids
        }
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
