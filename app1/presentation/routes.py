from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from business.services import MatchService, PredictionService

web = Blueprint("web", __name__)
matches = MatchService()
predictions = PredictionService(match_service=matches)


@web.get("/")
def index():
    return render_template("index.html", matches=matches.list_matches(), predictions=predictions.list_predictions())


@web.post("/predictions")
def create_prediction():
    try:
        predictions.create_prediction(request.form.get("match_id"), request.form.get("winner"), request.form.get("home_score"), request.form.get("away_score"))
    except ValueError as error:
        return render_template("index.html", matches=matches.list_matches(), predictions=predictions.list_predictions(), error=str(error)), 400
    return redirect(url_for("web.index"))


@web.get("/api/matches")
def list_matches_api():
    return jsonify([match.to_dict() for match in matches.list_matches()])


@web.get("/api/predictions")
def list_predictions_api():
    return jsonify([prediction.to_dict() for prediction in predictions.list_predictions()])


@web.post("/api/predictions")
def create_prediction_api():
    payload = request.get_json(silent=True) or {}
    try:
        prediction = predictions.create_prediction(payload.get("match_id"), payload.get("winner"), payload.get("home_score"), payload.get("away_score"))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify(prediction.to_dict()), 201


@web.get("/api/mock/matches")
def mock_matches_api():
    return jsonify(MatchService().api_client.get_matches())
