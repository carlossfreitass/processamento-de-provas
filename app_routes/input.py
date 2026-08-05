"""
Blueprint de input — recebe dados para processamento de provas.
"""

from flask import Blueprint, jsonify, request
from services.parser import parse_input

input_bp = Blueprint("input", __name__)

@input_bp.route("/input", methods=["POST"])
def receive_input():
    """
    Recebe o HTML da prova e aciona o pipeline de parsing completo.
    """
    payload = request.get_json(silent=True) or {}
    raw_html = payload.get("html", "")

    if not raw_html:
        return jsonify({"error": "O campo 'html' é obrigatório ou está vazio."}), 400

    try:
        # Executa o pipeline de ponta a ponta
        resultado = parse_input(raw_html)

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500