from typing import List, Optional
import json
from datetime import datetime, timezone

from ..extensions import db
from ..models.parking import ParkingArea, ParkingSlot


class ParkingAreaDict:
    """Shape ข้อมูล parking area ให้เป็น JSON ที่ frontend ใช้ง่าย."""

    def __init__(self, **kwargs):
        self._id = kwargs.get('id')
        self._name = kwargs.get('name')
        self._address = kwargs.get('address')
        self._latitude = kwargs.get('latitude')
        self._longitude = kwargs.get('longitude')
        self._allowed_types = kwargs.get('allowed_types', [])
        self._total_slots = kwargs.get('total_slots', 0)
        self._available_slots = kwargs.get('available_slots', 0)
        self._unavailable_slots = kwargs.get('unavailable_slots', 0)

    def to_dict(self):
        return {
            "id": self._id,
            "name": self._name,
            "address": self._address,
            "latitude": self._latitude,
            "longitude": self._longitude,
            "allowed_types": self._allowed_types,
            "total_slots": self._total_slots,
            "available_slots": self._available_slots,
            "unavailable_slots": self._unavailable_slots,
        }


class ParkingSlotDict:
    """Shape ข้อมูล slot ให้ frontend ไม่ต้องรู้รายละเอียด column ใน database."""

    def __init__(self, **kwargs):
        self._id = kwargs.get('id')
        self._area_id = kwargs.get('area_id')
        self._name = kwargs.get('name')
        self._status = kwargs.get('status')

    def to_dict(self):
        return {
            "id": self._id,
            "area_id": self._area_id,
            "name": self._name,
            "status": self._status.lower() if self._status else "unknown"
        }


class ParkingManager:
    """รวม business logic ของ parking ไว้ที่เดียว แทนการยัด logic ทั้งหมดใน route."""

    def __init__(self, db_name: str = "sqlite:///tu_parking.db"):
        self._db_name = db_name

    # =========================
    # REPORT
    # =========================
    def generate_occupancy_report(self) -> dict:
        areas = ParkingArea.query.all()
        total_slots = sum(a.total_slots for a in areas)
        total_available = sum(a.available_slots_db for a in areas)

        return {
            "summary": {
                "total_areas": len(areas),
                "global_total_slots": total_slots,
                "global_available": total_available,
                "occupancy_rate": (total_slots - total_available) / total_slots if total_slots > 0 else 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    # =========================
    # GET
    # =========================
    
    def get_all_parking_areas(self) -> List[dict]:
        areas = ParkingArea.query.all()
        results = []

        for area in areas:
            data = ParkingAreaDict(
                id=area.id,
                name=area.name,
                address=area.address,
                latitude=area.latitude,
                longitude=area.longitude,
                allowed_types=area.get_allowed_types_list(),
                total_slots=area.total_slots,
                available_slots=area.available_slots_db,
                unavailable_slots=area.unavailable_slots,
            )
            results.append(data.to_dict())

        return results

    def get_parking_area_by_id(self, area_id: int) -> Optional[dict]:
        area = ParkingArea.query.get(area_id)
        if not area:
            return None

        data = ParkingAreaDict(
            id=area.id,
            name=area.name,
            address=area.address,
            latitude=area.latitude,
            longitude=area.longitude,
            allowed_types=area.get_allowed_types_list(),
            total_slots=area.total_slots,
            available_slots=area.available_slots_db,
            unavailable_slots=area.unavailable_slots,
        )
        return data.to_dict()

    def get_parking_slots(self, area_id: int) -> List[dict]:
        slots = ParkingSlot.query.filter_by(area_id=area_id)\
            .order_by(ParkingSlot._name).all()

        return [
            ParkingSlotDict(
                id=s.id,
                area_id=s.area_id,
                name=s.name,
                status=s.status
            ).to_dict()
            for s in slots
        ]

    # =========================
    # CREATE
    # =========================
    
    def add_parking_area(self, name: str, total_slots: int, address=None, lat=None, lon=None):
        area = ParkingArea(
            name=name,
            address=address,
            latitude=lat,
            longitude=lon,
            total_slots=total_slots,
            available_slots_db=total_slots
        )
        db.session.add(area)
        db.session.commit()
        return area

    def add_parking_slot(self, area_id: int, name: str, status: str = 'available'):
        slot = ParkingSlot(area_id=area_id, name=name, status=status)
        db.session.add(slot)
        db.session.commit()
        return slot

    # =========================
    # UPDATE
    # =========================
    
    def update_slot(self, slot_id: int, new_status: str) -> bool:
        slot = ParkingSlot.query.get(slot_id)
        if slot:
            slot.update_status(new_status)
            db.session.commit()
            return True
        return False

    def update_available_slots(self, area_id: int, available_slots: int):
        """Set จำนวนช่องว่างของ area แล้ว update สถานะ slot ให้สอดคล้องกัน."""
        area = ParkingArea.query.get(area_id)
        if not area:
            raise ValueError("Parking area not found")

        if not isinstance(available_slots, int):
            raise ValueError("available_slots must be integer")

        if available_slots < 0 or available_slots > area.total_slots:
            raise ValueError(f"available_slots must be between 0 and {area.total_slots}")

        slots = ParkingSlot.query.filter_by(area_id=area_id)\
            .order_by(ParkingSlot._name).all()

        # ใช้ rule ง่าย ๆ: slot ต้น ๆ เป็น available ที่เหลือเป็น occupied
        for index, slot in enumerate(slots, start=1):
            if index <= available_slots:
                slot.update_status("available")
            else:
                slot.update_status("occupied")

        area.available_slots_db = available_slots
        db.session.commit()

        return {
            "message": f"Updated {area.name}: {available_slots} slots available",
            "area": self.get_parking_area_by_id(area_id),
            "slots": self.get_parking_slots(area_id),
        }

    def update_single_slot(self, area_id: int, slot_id: int, new_status: str):
        """Update slot เดียว แล้วคำนวณ available_slots ของ area ใหม่จากสถานะจริง."""
        slot = ParkingSlot.query.get(slot_id)
        if not slot or slot.area_id != area_id:
            raise ValueError("Slot not found")

        old_status = slot.status
        slot.update_status(new_status)

        area = ParkingArea.query.get(area_id)
        area.available_slots_db = ParkingSlot.query.filter_by(
            area_id=area_id, _status="available"
        ).count()

        db.session.commit()

        return {
            "message": f"Slot {slot.name}: {old_status} -> {new_status}",
            "slot": {
                "id": slot.id,
                "name": slot.name,
                "status": slot.status,
            },
            "area": self.get_parking_area_by_id(area_id),
            "slots": self.get_parking_slots(area_id),
        }

    def sync_slots_from_ml(self, area_id: int, analyzed_slots: list):
        """แทน slot เดิมด้วยผล image detection เพื่อให้ DB ตรงกับภาพล่าสุด."""
        area = ParkingArea.query.get(area_id)
        if not area:
            raise ValueError("Parking area not found")

        # ผลจาก ML มีจำนวน slot ตาม polygon ที่วิเคราะห์ จึง rebuild slot list ของ area นี้ใหม่
        ParkingSlot.query.filter_by(area_id=area_id).delete()

        for i, slot in enumerate(analyzed_slots, start=1):
            db.session.add(ParkingSlot(
                area_id=area_id,
                name=f"Slot-{i:02d}",
                status=slot["status"]
            ))

        db.session.flush()

        total_slots = len(analyzed_slots)
        available_slots = sum(
            1 for s in analyzed_slots if s["status"] == "available"
        )

        area.total_slots = total_slots
        area.available_slots_db = available_slots

        db.session.commit()

        return {
            "applied": True,
            "synced_slots": total_slots,
            "message": f"Database updated with {total_slots} detected slots"
        }

    # =========================
    # DELETE
    # =========================
    
    def delete_slot(self, slot_id: int) -> bool:
        slot = ParkingSlot.query.get(slot_id)
        if slot:
            db.session.delete(slot)
            db.session.commit()
            return True
        return False

    def get_all_slots_json(self) -> str:
        slots = ParkingSlot.query.all()
        return json.dumps([
            {"id": s.id, "area_id": s.area_id, "name": s.name, "status": s.status}
            for s in slots
        ])


parking_manager = ParkingManager()
