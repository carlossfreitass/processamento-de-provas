"""
Blueprint de input — recebe dados para processamento de provas.
"""

from flask import Blueprint, jsonify, request

input_bp = Blueprint("input", __name__)

@input_bp.route("/input", methods=["POST"])
def receive_input():
    """
    Placeholder para receber e processar dados de entrada.
    """
    payload = request.get_json(silent=True) or {}

    return jsonify({
        "received": True,
        "message": "Endpoint /input operacional — lógica de parsing será implementada nas próximas fases.",
        "echo": payload,
    }), 200