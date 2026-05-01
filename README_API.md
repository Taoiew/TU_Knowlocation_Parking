# ขั้นตอนการใช้งาน (ทดสอบ API)

1️⃣ **Get All Parking Areas** <br>
Method: ``GET`` <br>
URL: ``{{baseUrl}}/api/parking/areas`` <br>
Headers: None <br>
Body: None <br>
Expected Response (200):
```json
[
  {
    "address": "Tambon Khlong Nueng, Amphoe Khlong Luang, Pathum Thani 12120",
    "allowed_types": [
      "staff",
      "general"
    ],
    "available_slots": 2,
    "id": 1,
    "latitude": 14.0754,
    "longitude": 100.6041,
    "name": "GYM 7",
    "total_slots": 60,
    "unavailable_slots": 58
  },
  {
    "address": "99 Moo 18 Paholyothin Road, Khlong Nueng",
    "allowed_types": [
      "staff",
      "general",
      "disabled"
    ],
    "available_slots": 8,
    "id": 2,
    "latitude": 14.07,
    "longitude": 100.6,
    "name": "Parking 1",
    "total_slots": 120,
    "unavailable_slots": 112
  },
  ...
]
```

2️⃣ **Get Parking Area by ID** <br>
Method: ``GET`` <br>
URL: ``{{baseUrl}}/api/parking/areas/"AreaID"`` <br>
Headers: None <br>
Body: None <br>
Expected Response (200):
```json
{
  "area": {
    "address": "Tambon Khlong Nueng, Amphoe Khlong Luang, Pathum Thani 12120",
    "allowed_types": [
      "staff",
      "general"
    ],
    "available_slots": 2,
    "id": 1,
    "latitude": 14.0754,
    "longitude": 100.6041,
    "name": "GYM 7",
    "total_slots": 60,
    "unavailable_slots": 58
  },
  "slots": [
    {
      "area_id": 1,
      "id": 1,
      "name": "Slot-01",
      "status": "available"
    },
    ...
  ]
}
```

3️⃣ **Get Parking Slots by Area** <br>
Method: ``GET`` <br>
URL: ``{{baseUrl}}/api/parking/areas/"AreaID"/slots`` <br>
Headers: None <br>
Body: None <br>
Expected Response (200):
```json
[
    {
      "id": 1,
      "slot_name": "A1",
      "status": "available"
    },
    {
      "id": 2,
      "slot_name": "A2",
      "status": "occupied"
    }
]
```

4️⃣ **Update Available Parking Slots** <br>
Method: ``POST`` <br>
URL: ``{{baseUrl}}/api/parking/areas/"AreaID"/update"`` <br>
Headers: None <br>
Body: <br>
```json
{
  "available_slots": 10
}
```
Expected Response (200):
```json
{
  "area": {
    "address": "Tambon Khlong Nueng, Amphoe Khlong Luang, Pathum Thani 12120",
    "allowed_types": [
      "staff",
      "general"
    ],
    "available_slots": 10,
    "id": 1,
    "latitude": 14.0754,
    "longitude": 100.6041,
    "name": "GYM 7",
    "total_slots": 60,
    "unavailable_slots": 50
  },
  "message": "Updated GYM 7: 10 slots available",
  "slots": [
    {
      "area_id": 1,
      "id": 1,
      "name": "Slot-01",
      "status": "available"
    },
    ...
  ]
}
```

5️⃣ **Update Parking Slot Status** <br>
Method: ``POST`` <br>
URL: ``{{baseUrl}}/api/parking/areas/"AreaID"/slots/"SlotID"`` <br>
Headers: None <br>
Body: <br>
```json
{
  "status": "occupied"
}
```
Expected Response (200):
```json
{
  "area": {
    "address": "Tambon Khlong Nueng, Amphoe Khlong Luang, Pathum Thani 12120",
    "allowed_types": [
      "staff",
      "general"
    ],
    "available_slots": 10,
    "id": 1,
    "latitude": 14.0754,
    "longitude": 100.6041,
    "name": "GYM 7",
    "total_slots": 60,
    "unavailable_slots": 50
  },
  "message": "Slot Slot-01: occupied -> available",
  "slot": {
    "id": 1,
    "name": "Slot-01",
    "status": "available"
  },
  "slots": [
    {
      "area_id": 1,
      "id": 1,
      "name": "Slot-01",
      "status": "available"
    },
    ...
  ]
}
```

6️⃣ **Predict Parking Availability** <br>
Method: ``POST`` <br>
URL: ``{{baseUrl}}/api/parking/areas/"AreaID"/ml-predict`` <br>
Headers: None <br>
Body: <br>
Expected Response (200):
```json
{
  "area_id": 1,
  "area_name": "GYM 7",
  "available_slots": 10,
  "confidence": 0.85,
  "model": "default_model_v1",
  "occupancy_rate": "83.3%",
  "prediction": "likely_full",
  "total_slots": 60
}
```

7️⃣ **Detect Vehicles from Image** <br>
Method: ``POST`` <br>
URL: ``{{baseUrl}}/api/parking/areas/"AreaID"/ml-image-detect`` <br>
Headers: None <br>
Body: <br>
```json
image = [upload image file]
apply_to_area = true (optional)
```
Expected Response (200):
```json
{
  "area": {
    "id": 1,
    "name": "GYM 7",
    "available_slots": 12,
    "total_slots": 60,
    "unavailable_slots": 48
  },
  "db_slots": [
    {
      "id": 1,
      "name": "Slot-01",
      "status": "available"
    },
    {
      "id": 2,
      "name": "Slot-02",
      "status": "occupied"
    }
  ],
  "ml_result": {
    "vehicles_detected": 5,
    "slot_results": [
      {
        "slot_name": "Slot-01",
        "status": "available"
      },
      {
        "slot_name": "Slot-02",
        "status": "occupied"
      }
    ]
  },
  "sync": {
    "applied": true,
    "synced_slots": 2,
    "remaining_slots_marked_maintenance": 0
  }
}
```

