"""Flask routes for parking APIs and testing workflows."""

from typing import Tuple

from flask import Blueprint, Response, jsonify, request

from ..extensions import db
from ..models.parking import ParkingArea, ParkingSlot
from ..services.parking_service import parking_manager

parking_bp = Blueprint("parking", __name__)

def _get_area_or_404(
    area_id: int,
) -> Tuple[ParkingArea | None, Tuple[Response, int] | None]:
    # helper นี้ลดการเขียน logic หา area + คืน 404 ซ้ำในหลาย endpoint
    area = ParkingArea.query.get(area_id)
    if not area:
        return None, (jsonify({"error": "Parking area not found"}), 404)
    return area, None


def _refresh_area_available_slots(area: ParkingArea) -> None:
    area.available_slots_db = ParkingSlot.query.filter_by(
        area_id=area.id,
        _status="available",
    ).count()

def _parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


@parking_bp.route("/api/parking/areas", methods=["GET"])
def api_parking_areas() -> Response:
    """Return all parking areas for map/list pages."""
    return jsonify(parking_manager.get_all_parking_areas())


@parking_bp.route("/api/parking", methods=["GET"])
def api_parking_areas_alias() -> Response:
    """Compatibility alias for older frontend code."""
    return api_parking_areas()


@parking_bp.route("/api/parking/areas/<int:area_id>", methods=["GET"])
def api_parking_detail(area_id: int) -> Tuple[Response, int] | Response:
    """Return one parking area with its current slot list."""
    area = parking_manager.get_parking_area_by_id(area_id)
    if not area:
        return jsonify({"error": "Parking area not found"}), 404

    return jsonify(
        {
            "area": area,
            "slots": parking_manager.get_parking_slots(area_id),
        }
    )


@parking_bp.route("/api/parking/<int:area_id>", methods=["GET"])
def api_parking_detail_alias(area_id: int) -> Tuple[Response, int] | Response:
    """Compatibility alias for older frontend code."""
    return api_parking_detail(area_id)
