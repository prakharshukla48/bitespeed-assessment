from database import db

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=True)
    primary_contact_id = db.Column(db.Integer, nullable=False)

    def __init__(self, email, phone_number, primary_contact_id):
        self.email = email
        self.phone_number = phone_number
        self.primary_contact_id = primary_contact_id
