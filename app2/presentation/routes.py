from flask import Blueprint, current_app, jsonify, redirect, render_template, request, send_from_directory, url_for

from business.services import MarketingService

web = Blueprint("marketing", __name__)


def service():
    return MarketingService(current_app.config["STORAGE_DIR"])


@web.get("/")
def index():
    return render_template("index.html")


@web.post("/campaigns")
def create_campaign():
    try:
        campaign = service().create_campaign(request.files.get("photo"))
    except ValueError as error:
        return render_template("index.html", error=str(error)), 400
    return redirect(url_for("marketing.scripts", campaign_id=campaign.id))


@web.get("/campaigns/<int:campaign_id>/scripts")
def scripts(campaign_id):
    campaign = service().repository.find(campaign_id)
    if campaign is None:
        return "Campaña no encontrada", 404
    return render_template("scripts.html", campaign=campaign, scripts=service().scripts(campaign))


@web.post("/campaigns/<int:campaign_id>/generate")
def generate(campaign_id):
    current_service = service()
    campaign = current_service.repository.find(campaign_id)
    if campaign is None:
        return "Campaña no encontrada", 404
    try:
        current_service.generate_assets(campaign, request.form.get("script_index"), request.form.get("platform"))
    except (ValueError, RuntimeError) as error:
        return render_template("scripts.html", campaign=campaign, scripts=current_service.scripts(campaign), error=str(error)), 400
    return redirect(url_for("marketing.detail", campaign_id=campaign.id))


@web.get("/campaigns/<int:campaign_id>")
def detail(campaign_id):
    campaign = service().repository.find(campaign_id)
    if campaign is None:
        return "Campaña no encontrada", 404
    return render_template("detail.html", campaign=campaign, scripts=service().scripts(campaign))


@web.post("/campaigns/<int:campaign_id>/publish")
def publish(campaign_id):
    current_service = service()
    campaign = current_service.repository.find(campaign_id)
    if campaign is None:
        return "Campaña no encontrada", 404
    try:
        current_service.publish(campaign)
    except ValueError as error:
        return render_template("detail.html", campaign=campaign, scripts=current_service.scripts(campaign), error=str(error)), 400
    return redirect(url_for("marketing.detail", campaign_id=campaign.id))


@web.get("/storage/<path:filename>")
def storage(filename):
    return send_from_directory(current_app.config["STORAGE_DIR"], filename)


@web.get("/api/campaigns/<int:campaign_id>")
def campaign_api(campaign_id):
    campaign = service().repository.find(campaign_id)
    if campaign is None:
        return jsonify({"error": "Campaña no encontrada"}), 404
    return jsonify({"id": campaign.id, "original_filename": campaign.original_filename, "scripts": service().scripts(campaign), "selected_script": campaign.selected_script, "social_platform": campaign.social_platform, "social_status": campaign.social_status, "assets": [{"type": asset.asset_type, "url": url_for("marketing.storage", filename=asset.file_path, _external=True)} for asset in campaign.assets]})
