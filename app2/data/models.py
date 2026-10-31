from datetime import datetime

from .database import db


class Campaign(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(255), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    scripts_json = db.Column(db.Text, nullable=False)
    selected_script = db.Column(db.Integer)
    social_platform = db.Column(db.String(30))
    social_status = db.Column(db.String(40), default="not_published", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    assets = db.relationship("Asset", back_populates="campaign", cascade="all, delete-orphan")


class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=False)
    asset_type = db.Column(db.String(20), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    campaign = db.relationship("Campaign", back_populates="assets")
