from .database import db
from .models import Match, Prediction


class MatchRepository:
    def list_all(self):
        return Match.query.order_by(Match.kickoff).all()

    def find_by_id(self, match_id):
        return db.session.get(Match, match_id)

    def upsert(self, data):
        match = Match.query.filter_by(external_id=data["external_id"]).first()
        if match is None:
            match = Match(external_id=data["external_id"])
            db.session.add(match)
        for field in ("home_team", "away_team", "kickoff", "stage", "status", "home_score", "away_score"):
            setattr(match, field, data.get(field))
        return match


class PredictionRepository:
    def list_all(self):
        return Prediction.query.order_by(Prediction.created_at.desc()).all()

    def create(self, data):
        prediction = Prediction(**data)
        db.session.add(prediction)
        db.session.commit()
        return prediction
