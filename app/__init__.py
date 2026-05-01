"""TUparkingLocation - Flask Application Factory"""

import os

from flask import Flask
from flask_cors import CORS
from .extensions import db
from .routes.parking_routes import parking_bp
from .routes.slot_routes import slot_bp
from .routes.ml_routes import ml_bp
from .models.parking import ParkingArea, ParkingSlot
from .models.ml_models import MLModel, Prediction, TrainingHistory


def create_app():
    app = Flask(__name__)

    # อ่าน CORS จาก env เพื่อให้ local, Docker, หรือ deploy ตั้ง frontend origin ได้โดยไม่แก้โค้ด
    cors_origins = os.getenv("CORS_ORIGINS", "*")
    CORS(app, origins=cors_origins.split(",") if cors_origins != "*" else "*")
    
    # Docker ใช้ PostgreSQL ผ่าน DATABASE_URL ส่วน local ถ้าไม่ตั้ง env จะ fallback เป็น SQLite
    database_url = os.getenv("DATABASE_URL", "sqlite:///tu_parking.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy
    db.init_app(app)

    # Create tables and seed data
    with app.app_context():
        # โปรเจกต์นี้ยังไม่มี migration tool จึงสร้างตารางจาก model ตอน app start
        db.create_all()
        seed_mock_data()
       

    # Register routes
    app.register_blueprint(parking_bp)
    app.register_blueprint(slot_bp)
    app.register_blueprint(ml_bp)

    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}
    
    return app


def seed_mock_data():
    """Seed mock Thammasat University parking data"""
    if ParkingArea.query.count() > 0:
        return

    print("🌱 Seeding mock parking data for TUparkingLocation...")

    # กำหนดข้อมูลพื้นที่จอดรถในมหาวิทยาลัยธรรมศาสตร์ (Rangsit Campus) พร้อมจำนวนช่องจอดและประเภทผู้ใช้ที่อนุญาต

    areas_data = [
        
        {"name": "หลังยิม7",     "lat": 14.069599573072148, "lon": 100.60013965939902, "total_slots": 29,  "available_slots": 2,  "allowed_types": "staff,general",          "address": "Tambon Khlong Nueng, Amphoe Khlong Luang, Pathum Thani 12120"},
        {"name": "ยิม4-6",      "lat": 14.066159446950925, "lon": 100.60454919931888, "total_slots": 120, "available_slots": 8,  "allowed_types": "staff,general,disabled",   "address": "99 Moo 18 Paholyothin Road, Khlong Nueng"},
        {"name": "SC1",         "lat": 14.069969584365227, "lon": 100.60358519438483, "total_slots": 80,  "available_slots": 35, "allowed_types": "staff",                   "address": "TU Main Library Zone, Pathum Thani 12120"},
        {"name": "กิติยาอาคาร", "lat": 14.07121336507646,  "lon": 100.60757966766195, "total_slots": 45,  "available_slots": 12, "allowed_types": "staff,general",            "address": "Faculty of Engineering, Thammasat University"},
        {"name": "SC3",         "lat": 14.070634271504174, "lon": 100.60620919341392, "total_slots": 90,  "available_slots": 67, "allowed_types": "staff,disabled",          "address": "SC Building Zone, Rangsit Campus"},
        {"name": "ศกร.",        "lat": 14.071498746657918, "lon": 100.6037244823913,  "total_slots": 60,  "available_slots": 30, "allowed_types": "staff,general,disabled",   "address": "Thammasat University, Rangsit Campus"},
    ]

    for data in areas_data:
        area = ParkingArea(
            name=data["name"],
            address=data["address"],
            latitude=data["lat"],
            longitude=data["lon"],
            allowed_types=data.get("allowed_types", "staff,general"),
            total_slots=data["total_slots"],
            available_slots_db=data["available_slots"]
        )
        db.session.add(area)
        db.session.flush()                     # ต้อง flush ก่อนเพื่อให้ area.id ถูกสร้าง แล้วเอาไปผูก slots

        # สร้าง slot ตามจำนวน total_slots และตั้งสถานะตาม available_slots mock
        for i in range(1, data["total_slots"] + 1):
            status = "available" if i <= data["available_slots"] else "occupied"
            slot = ParkingSlot(
                area_id=area.id,
                name=f"Slot-{i:02d}",
                status=status
            )
            db.session.add(slot)

    db.session.commit()
    print("✅ Mock data seeded successfully! Database is ready.")


def ensure_demo_defaults():
    """Keep demo data aligned with the current testing scenario."""
    gym7 = ParkingArea.query.filter(ParkingArea.name.in_(["หลังยิม7", "GYM 7", "GYM-7"])).first()
    if not gym7:
        return

    target_total_slots = 29
    target_available_slots = 2
    gym7.total_slots = target_total_slots
    gym7.available_slots_db = target_available_slots

    ordered_slots = (
        ParkingSlot.query.filter_by(area_id=gym7.id)
        .order_by(ParkingSlot.name)
        .all()
    )
    for index, slot in enumerate(ordered_slots, start=1):
        if index > target_total_slots:
            db.session.delete(slot)
            continue
        slot.status = "available" if index <= target_available_slots else "occupied"

    existing_count = min(len(ordered_slots), target_total_slots)
    for index in range(existing_count + 1, target_total_slots + 1):
        db.session.add(
            ParkingSlot(
                area_id=gym7.id,
                name=f"Slot-{index:02d}",
                status="available" if index <= target_available_slots else "occupied",
            )
        )

    db.session.commit()
