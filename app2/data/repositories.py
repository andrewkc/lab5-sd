from .database import db
from .models import Asset, Campaign


class CampaignRepository:
    def create(self, campaign):
        db.session.add(campaign)
        db.session.commit()
        return campaign

    def find(self, campaign_id):
        return db.session.get(Campaign, campaign_id)

    def add_asset(self, campaign_id, asset_type, file_path):
        asset = Asset(campaign_id=campaign_id, asset_type=asset_type, file_path=file_path)
        db.session.add(asset)
        db.session.commit()
        return asset

    def update(self, campaign):
        db.session.commit()
        return campaign
