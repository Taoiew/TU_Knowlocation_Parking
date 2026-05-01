from typing import Tuple
from flask import Blueprint, Response, jsonify, request

from ..extensions import db
from ..models.parking import ParkingArea
from ..services.parking_service import parking_manager

slot_bp = Blueprint("slot", __name__)


def _get_area_or_404(area_id: int):
    # ใช้เช็คก่อนทำงานกับ slot เพื่อไม่ให้ update ผิด area
    area = ParkingArea.query.get(area_id)
    if not area:
        return None, (jsonify({"error": "Parking area not found"}), 404)
    return area, None


@slot_bp.route("/api/parking/areas/<int:area_id>/slots", methods=["GET"])
def api_parking_slots(area_id: int):
    _, error_response = _get_area_or_404(area_id)
    if error_response:
        return error_response

    return jsonify(parking_manager.get_parking_slots(area_id))

@slot_bp.route("/api/parking/areas/<int:area_id>/update", methods=["POST"])
def update_parking_available(area_id: int):
    try:
        # endpoint นี้ใช้ตอนอยาก set จำนวนช่องว่างแบบเร็ว แล้ว service จะกระจายสถานะลง slots ให้
        data = request.get_json(silent=True) or {}
        available_slots = data.get("available_slots")

        result = parking_manager.update_available_slots(area_id, available_slots)

        return jsonify(result), 200

    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400

@slot_bp.route("/api/parking/areas/<int:area_id>/slots/<int:slot_id>", methods=["POST"])
def update_slot_status(area_id: int, slot_id: int):
    try:
        # endpoint นี้แก้สถานะราย slot เช่น available -> occupied -> maintenance
        data = request.get_json(silent=True) or {}
        new_status = data.get("status")

        result = parking_manager.update_single_slot(area_id, slot_id, new_status)

        return jsonify(result), 200

    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
