"""SQLAlchemy models for parking areas and slots."""

from datetime import datetime, timezone
from ..extensions import db


class ParkingArea(db.Model):
    """ลานจอดหนึ่งพื้นที่ เช่น หลังยิม7 หรือ SC1."""

    __tablename__ = 'parking_areas'

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column('name', db.String(100), nullable=False)
    _address = db.Column('address', db.String(255), nullable=True)
    _latitude = db.Column('latitude', db.Float, nullable=True)
    _longitude = db.Column('longitude', db.Float, nullable=True)
    _allowed_types = db.Column('allowed_types', db.String(50), nullable=False, default="staff,general")  # comma-separated: staff,general,disabled
    _total_slots = db.Column('total_slots', db.Integer, nullable=False)
    available_slots_db = db.Column('available_slots', db.Integer, nullable=False) 

    # ลานจอดหนึ่งพื้นที่มีหลาย slot
    slots = db.relationship('ParkingSlot', backref='area', lazy=True)

    def __init__(self, **kwargs):
        """Explicit constructor for ParkingArea."""
        # Extract property-based fields to set them via setters
        name = kwargs.pop('name', None)
        total_slots = kwargs.get('total_slots') # Keep in kwargs for super() if needed, or set here
        allowed_types = kwargs.pop('allowed_types', None)
        
        super(ParkingArea, self).__init__(**kwargs)
        
        if name: self.name = name
        if allowed_types: self.allowed_types = allowed_types
        if 'latitude' in kwargs: self.latitude = kwargs['latitude']
        if 'longitude' in kwargs: self.longitude = kwargs['longitude']
        # total_slots is already set via super() because it's _total_slots in kwargs usually? 
        # No, it's likely 'total_slots' in kwargs.
        if 'total_slots' in kwargs: self.total_slots = kwargs['total_slots']

        if 'available_slots_db' not in kwargs and self.total_slots:
            self.available_slots_db = self.total_slots

    # Getters and Setters using properties
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        self._name = value

    @property
    def total_slots(self):
        return self._total_slots
    
    @total_slots.setter
    def total_slots(self, value):
        if value < 0:
            raise ValueError("Total slots cannot be negative")
        self._total_slots = value

    @property
    def allowed_types(self):
        return self._allowed_types
    
    @allowed_types.setter
    def allowed_types(self, value):
        # จำกัดประเภทผู้ใช้ที่จอดได้ เพื่อกันข้อมูลผิดตั้งแต่ชั้น model
        valid_types = {'staff', 'general', 'disabled'}
        types = [t.strip() for t in value.split(",")]
        if not all(t in valid_types for t in types):
            raise ValueError(f"Invalid type in {value}. Must be from {valid_types}")
        self._allowed_types = value

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        self._address = value

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        self._latitude = value

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        self._longitude = value

    @property
    def unavailable_slots(self):
        return self.total_slots - self.available_slots_db

    # Complex Business Logic
    def check_access_permission(self, user_type: str) -> bool:
        """
        Complex logic to check if a specific user type is allowed 
        and if there's enough capacity for their specific category.
        """
        allowed = self.get_allowed_types_list()
        if user_type not in allowed:
            return False
        
        # Additional complex rule: disabled users always get priority if capacity > 0
        if user_type == 'disabled' and self.available_slots_db > 0:
            return True
            
        # Standard capacity check
        return self.available_slots_db > (self.total_slots * 0.1) # Keep 10% buffer for staff

    def get_allowed_types_list(self) -> list:
        """แปลง 'staff,general' -> ['staff', 'general']"""
        return [t.strip() for t in self.allowed_types.split(",") if t.strip()]

    def is_full(self, occupied_count: int) -> bool:
        """Check if the parking area is full."""
        return occupied_count >= self.total_slots

    def available_slots(self, occupied_count: int) -> int:
        """Calculate available slots."""
        return max(0, self.total_slots - occupied_count)


class ParkingSlot(db.Model):
    """ช่องจอดเดี่ยวใน parking area."""

    __tablename__ = 'parking_slots'

    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey('parking_areas.id'), nullable=False)
    _name = db.Column('name', db.String(20), nullable=False)
    _status = db.Column('status', db.String(20), nullable=False, default='available')  # 'available' or 'occupied'
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __init__(self, **kwargs):
        """Explicit constructor for ParkingSlot."""
        name = kwargs.pop('name', None)
        status = kwargs.pop('status', None)
        super(ParkingSlot, self).__init__(**kwargs)
        if name: self.name = name
        if status: self.status = status

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        self.update_status(value)

    # Complex Business Logic
    def perform_maintenance_check(self) -> dict:
        """
        Logic-heavy method to validate slot health and status.
        In a real app, this might check sensor data.
        """
        is_healthy = True
        status_report = "Healthy"
        
        if self._status == 'maintenance':
            is_healthy = False
            status_report = "Requires Attention"
        
        return {
            "slot_id": self.id,
            "is_healthy": is_healthy,
            "report": status_report,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def is_available(self) -> bool:
        """Check if this slot is available."""
        return self.status == 'available'

    def update_status(self, new_status: str):
        """Safely update the slot status with validation logic."""
        # ทุกทางที่แก้ status ควรผ่าน method นี้ เพื่อกัน typo เช่น "availble"
        valid_statuses = ['available', 'occupied', 'maintenance']
        if new_status in valid_statuses:
            self._status = new_status
        else:
            raise ValueError(f"Invalid status: {new_status}")
