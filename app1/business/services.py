from datetime import datetime

from data.database import db
from data.repositories import MatchRepository, PredictionRepository


class MatchApiClient:
    """Proveedor simulado: representa una API pública de resultados."""

    def get_matches(self):
        return [
            {"external_id": "ucl-2025-001", "home_team": "Real Madrid", "away_team": "Manchester City", "kickoff": "2025-02-19T20:00:00", "stage": "Playoffs", "status": "scheduled"},
            {"external_id": "ucl-2025-002", "home_team": "Bayern München", "away_team": "Paris Saint-Germain", "kickoff": "2025-02-20T20:00:00", "stage": "Playoffs", "status": "scheduled"},
            {"external_id": "ucl-2025-003", "home_team": "Liverpool", "away_team": "Inter de Milán", "kickoff": "2025-03-05T20:00:00", "stage": "Octavos de final", "status": "scheduled"},
            {"external_id": "ucl-2025-004", "home_team": "Barcelona", "away_team": "Borussia Dortmund", "kickoff": "2025-03-05T20:00:00", "stage": "Octavos de final", "status": "scheduled"},
        ]


class MatchService:
    def __init__(self, repository=None, api_client=None):
        self.repository = repository or MatchRepository()
        self.api_client = api_client or MatchApiClient()

    def sync_matches(self):
        for item in self.api_client.get_matches():
            item["kickoff"] = datetime.fromisoformat(item["kickoff"])
            self.repository.upsert(item)
        db.session.commit()

    def list_matches(self):
        return self.repository.list_all()

    def get_match(self, match_id):
        return self.repository.find_by_id(match_id)


class PredictionService:
    VALID_DRAW = "Empate"

    def __init__(self, match_service=None, repository=None):
        self.match_service = match_service or MatchService()
        self.repository = repository or PredictionRepository()

    def create_prediction(self, match_id, winner, home_score, away_score):
        match = self.match_service.get_match(match_id)
        if match is None:
            raise ValueError("El partido indicado no existe")
        try:
            home_score, away_score = int(home_score), int(away_score)
        except (TypeError, ValueError) as exc:
            raise ValueError("Los marcadores deben ser números enteros") from exc
        if home_score < 0 or away_score < 0:
            raise ValueError("Los marcadores no pueden ser negativos")
        if winner not in {match.home_team, match.away_team, self.VALID_DRAW}:
            raise ValueError("El ganador debe ser uno de los equipos o Empate")
        if home_score > away_score and winner != match.home_team:
            raise ValueError("El ganador no coincide con el marcador estimado")
        if away_score > home_score and winner != match.away_team:
            raise ValueError("El ganador no coincide con el marcador estimado")
        if home_score == away_score and winner != self.VALID_DRAW:
            raise ValueError("Un marcador empatado requiere seleccionar Empate")
        return self.repository.create({"match_id": match_id, "predicted_winner": winner, "predicted_home_score": home_score, "predicted_away_score": away_score})

    def list_predictions(self):
        return self.repository.list_all()
