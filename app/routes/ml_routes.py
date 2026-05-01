from typing import Tuple
from flask import Blueprint, Response, jsonify, request

from ..extensions import db
from ..models.parking import ParkingArea
from ..services.parking_service import parking_manager
from ML.services.parking_prediction_service import ParkingPredictionService

ml_bp = Blueprint("ml", __name__)
# สร้าง service ครั้งเดียวเพื่อ reuse manager/preparer ระหว่าง request
prediction_service = ParkingPredictionService()


def _get_area_or_404(area_id: int):
    # ML ทุก endpoint ผูกกับ parking area จึงต้อง validate area ก่อนเสมอ
    area = ParkingArea.query.get(area_id)
    if not area:
        return None, (jsonify({"error": "Parking area not found"}), 404)
    return area, None


def _parse_bool(value: str | None) -> bool:
    # form-data ส่ง boolean มาเป็น string เช่น "true" หรือ "1"
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


@ml_bp.route("/api/ml/health", methods=["GET"])
def ml_health():
    return jsonify({
        "status": "ok",
        "summary_prediction": "available",
        "image_detection": "requires ML/yolov8x.pt or ML/parking_model.pt"
    })


@ml_bp.route("/api/parking/areas/<int:area_id>/ml-predict", methods=["POST"])
def ml_predict_area(area_id: int):
    try:
        # summary prediction ใช้ข้อมูล slot ปัจจุบันจาก DB ไม่ต้องอัปโหลดรูป
        _, error_response = _get_area_or_404(area_id)
        if error_response:
            return error_response

        result = prediction_service.make_prediction(area_id)
        if not result.get("success"):
            return jsonify({"error": result.get("error", "ML prediction failed")}), 400

        return jsonify({
            "area_id": result["parking_area_id"],
            "area_name": result["area_name"],
            "available_slots": result["available_slots"],
            "confidence": result["confidence"],
            "model": result["model_name"],
            "occupancy_rate": result["occupancy_rate"],
            "prediction": result["prediction"],
            "prediction_id": result["prediction_id"],
            "predicted_available_slots": result["predicted_available_slots"],
            "total_slots": result["total_slots"],
        }), 200

    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400


@ml_bp.route("/api/parking/areas/<int:area_id>/ml-history", methods=["GET"])
def ml_prediction_history(area_id: int):
    try:
        _, error_response = _get_area_or_404(area_id)
        if error_response:
            return error_response

        limit = request.args.get("limit", default=10, type=int)
        return jsonify(prediction_service.get_prediction_history(area_id, limit)), 200

    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@ml_bp.route("/api/parking/areas/<int:area_id>/ml-image-detect", methods=["POST"])
def ml_detect_area_from_image(area_id: int):
    try:
        area, error_response = _get_area_or_404(area_id)
        if error_response:
            return error_response

        uploaded_file = request.files.get("image")

        if not uploaded_file or not uploaded_file.filename:
            return jsonify({"error": "image file is required"}), 400

        image_bytes = uploaded_file.read()

        if not image_bytes:
            return jsonify({"error": "uploaded image is empty"}), 400

        # import ตรงนี้เพื่อไม่ให้ backend โหลด YOLO ตั้งแต่ start app
        # app หลักจึงยังเปิดได้ แม้ยังไม่มีไฟล์ model หรือยังไม่ใช้ image detection
        from ML.services.parking_image_detector import parking_image_detector

        try:
            result = parking_image_detector.analyze(image_bytes)
        except FileNotFoundError as exc:
            return jsonify({
                "error": str(exc),
                "hint": "Place ML/yolov8x.pt or ML/parking_model.pt in the ML folder, then rerun this request."
            }), 400

        apply_to_area = _parse_bool(request.form.get("apply_to_area"))

        sync_summary = {
            "applied": False,
            "synced_slots": 0
        }

        # 🔥 ย้าย logic ไป service
        if apply_to_area:
            analyzed_slots = result["slot_results"]

            sync_summary = parking_manager.sync_slots_from_ml(
                area_id,
                analyzed_slots
            )

        return jsonify({
            "area": parking_manager.get_parking_area_by_id(area_id),
            "db_slots": parking_manager.get_parking_slots(area_id),
            "ml_result": result,
            "sync": sync_summary
        }), 200

    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
