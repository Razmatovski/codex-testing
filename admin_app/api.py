from flask import Blueprint, jsonify, request
from .models import Language, Currency, UnitOfMeasurement, Category, Service, Setting
from . import db
import re

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


@api_bp.route('/calculator-data', methods=['GET'])
def calculator_data():
    try:
        languages = [
            {"id": lang.code, "name": lang.name}
            for lang in Language.query.all()
        ]
        currencies = [
            {"id": cur.code, "symbol": cur.symbol, "name": cur.name}
            for cur in Currency.query.all()
        ]
        units = [
            {"id": unit.id, "name": unit.name, "abbreviation": unit.abbreviation}
            for unit in UnitOfMeasurement.query.all()
        ]
        categories = []
        for cat in Category.query.all():
            services = []
            for srv in Service.query.filter_by(category_id=cat.id).all():
                services.append({
                    "id": srv.id,
                    "name": srv.name,
                    "price": f"{srv.price:.2f}",
                    "unit_id": srv.unit_id,
                })
            categories.append({
                "id": cat.id,
                "name": cat.name,
                "services": services,
            })
        settings = {}
        for key in ["default_currency_id", "default_language_id"]:
            s = Setting.query.filter_by(key=key).first()
            if s:
                settings[key] = s.value
        data = {
            "settings": settings,
            "languages": languages,
            "currencies": currencies,
            "units_of_measurement": units,
            "categories": categories,
        }
        return jsonify(data), 200
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


def _is_number(value: str) -> bool:
    try:
        float(value)
        return True
    except Exception:
        return False


EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


@api_bp.route('/send-calculation', methods=['POST'])
def send_calculation():
    data = request.get_json(silent=True) or {}

    user_email = data.get('user_email')
    language_code = data.get('language_code')
    items = data.get('calculation_items')
    grand_total = data.get('grand_total_price')

    if not user_email or not EMAIL_REGEX.match(user_email):
        return jsonify({"status": "error", "message": "Invalid email address."}), 400

    if not language_code or not Language.query.filter_by(code=language_code).first():
        return jsonify({"status": "error", "message": "Invalid language code."}), 400

    if not items or not isinstance(items, list):
        return jsonify({"status": "error", "message": "calculation_items must be a non-empty list."}), 400

    for item in items:
        if not all(k in item for k in ["quantity", "price_per_unit", "item_total_price"]):
            return jsonify({"status": "error", "message": "Invalid item structure."}), 400
        if not (_is_number(item["quantity"]) and _is_number(item["price_per_unit"]) and _is_number(item["item_total_price"])):
            return jsonify({"status": "error", "message": "Numeric values required in items."}), 400

    if not grand_total or not _is_number(grand_total):
        return jsonify({"status": "error", "message": "Invalid grand_total_price."}), 400

    # Email sending placeholder
    print(f"Send calculation to {user_email}: total {grand_total}")

    return jsonify({"status": "success", "message": "Calculation successfully sent to your email."}), 200
