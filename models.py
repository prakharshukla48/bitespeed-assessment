from database import db

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=True)
    phone_number = db.Column(db.String(15), nullable=True)
    linked_id = db.Column(db.Integer, nullable=True)
    link_precedence =db.Column(db.String(15))
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, email, phone_number, linked_id, link_precedence, created_at, updated_at, deleted_at):
        self.email = email
        self.phone_number = phone_number
        self.linked_id = linked_id
        self.link_precedence = link_precedence
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at
