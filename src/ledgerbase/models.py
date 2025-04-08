from ledgerbase import db  # Fully-qualified import for clarity and typing


class ExampleModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
