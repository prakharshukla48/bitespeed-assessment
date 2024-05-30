from flask import Flask, request, jsonify
from models import Contact
from database import db, init_db
import datetime

app = Flask(__name__)
init_db(app)

@app.route('/identify', methods=['POST'])
def identify():
    data = request.get_json()
    email = data.get('email')
    phone_number = data.get('phoneNumber')

    if email:
        primary_email = Contact.query.filter_by(email=email).first()
    if not primary_email and phone_number:
        primary_phone = Contact.query.filter_by(phone_number=phone_number).first()
    # print(f"is phone or email present ? {primary_phone}, {primary_email}")

    if primary_email or primary_phone:
        if primary_email:
            if phone_number:
                primary_contact_id = primary_email.id
                new_contact = Contact(email=email,
                                      phone_number=phone_number,
                                      linked_id=primary_email.id,
                                      link_precedence= "Secondary",
                                      created_at= datetime.datetime.now(),
                                      updated_at= datetime.datetime.now())
                db.session.add(new_contact)
                db.session.commit()

        else:
            if email:
                primary_contact_id = primary_phone.id
                new_contact = Contact(email=email,
                                      phone_number=phone_number,
                                      linked_id=primary_phone.id,
                                      link_precedence="Secondary",
                                      created_at=datetime.datetime.now(),
                                      updated_at=datetime.datetime.now())
                db.session.add(new_contact)
                db.session.commit()
    else:
        primary_contact_id = Contact.query.count() + 1
        new_contact = Contact(email=email,
                              phone_number=phone_number,
                              linked_id=None,
                              link_precedence="Primary",
                              created_at=datetime.datetime.now(),
                              updated_at=datetime.datetime.now())
        db.session.add(new_contact)
        db.session.commit()

    secondary_contacts = Contact.query.filter_by(linked_id=primary_contact_id).all()
    secondary_contact_ids = [contact.id for contact in secondary_contacts]
    emails = [contact.email for contact in secondary_contacts] + [Contact.query.get(primary_contact_id).email]
    phone_numbers = [contact.phone_number for contact in secondary_contacts] + [Contact.query.get(primary_contact_id).phone_number]
    # secondary_contact_ids = [c.id for c in contacts if c.id != primary_contact_id]

    response = {
        "contact": {
            "primaryContactId": primary_contact_id,
            "emails": set(emails),
            "phoneNumbers": set(phone_numbers),
            "secondaryContactIds": secondary_contact_ids
        }
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
