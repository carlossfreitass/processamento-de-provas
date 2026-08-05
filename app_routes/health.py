"""
Blueprint de healthcheck.
"""

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def healthcheck():
    """Retorna status da aplicação."""
    return jsonify({"status": "ok", "service": "sisprova"}), 200