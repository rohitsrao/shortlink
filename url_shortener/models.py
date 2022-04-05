from url_shortener import db
from datetime import datetime, timezone

class Link(db.Model):
    short = db.Column(db.String, primary_key=True)
    url = db.Column(db.String(), unique=True, nullable=False)
