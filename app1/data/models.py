from datetime import datetime

from .database import db


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(80), unique=True, nullable=False)
    home_team = db.Column(db.String(120), nullable=False)
    away_team = db.Column(db.String(120), nullable=False)
    kickoff = db.Column(db.DateTime, nullable=False)
    stage = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="scheduled")
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    predictions = db.relationship(
        "Prediction", back_populates="match", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "external_id": self.external_id,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "kickoff": self.kickoff.isoformat(),
            "stage": self.stage,
            "status": self.status,
            "home_score": self.home_score,
            "away_score": self.away_score,
        }


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), nullable=False)
    predicted_winner = db.Column(db.String(120), nullable=False)
    predicted_home_score = db.Column(db.Integer, nullable=False)
    predicted_away_score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    match = db.relationship("Match", back_populates="predictions")

    def to_dict(self):
        return {
            "id": self.id,
            "match_id": self.match_id,
            "match": f"{self.match.home_team} vs {self.match.away_team}",
            "predicted_winner": self.predicted_winner,
            "predicted_home_score": self.predicted_home_score,
            "predicted_away_score": self.predicted_away_score,
            "created_at": self.created_at.isoformat(),
        }
