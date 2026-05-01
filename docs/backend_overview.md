# Backend File Overview

เอกสารนี้สรุปหน้าที่ของไฟล์ฝั่ง backend แบบอ่านตามโครงโปรเจกต์ได้เร็ว

## Root Backend Files

- `run.py` จุดเริ่มรัน Flask app ตอนรัน local หรือให้ Gunicorn import ใน Docker
- `requirements.txt` รายชื่อ Python packages ที่ backend และ ML ต้องใช้
- `Dockerfile` วิธีสร้าง Docker image ของ backend
- `docker-compose.yml` รวม service ของ backend, frontend และ PostgreSQL database
- `.env` ค่า config จริงของเครื่อง เช่น port และ `DATABASE_URL`
- `.env.example` ตัวอย่างค่า config สำหรับคนอื่นในทีม
- `README_API.md` เอกสาร endpoint ของ API

## app/

- `app/__init__.py` สร้าง Flask app, ตั้งค่า CORS/database, สร้างตาราง, seed ข้อมูล demo และ register routes
- `app/extensions.py` สร้างตัวแปร `db` ของ SQLAlchemy ให้ไฟล์อื่น import ใช้ร่วมกัน

## app/routes/

- `app/routes/parking_routes.py` API สำหรับอ่านข้อมูลลานจอดและรายละเอียด slot
- `app/routes/slot_routes.py` API สำหรับแก้สถานะจำนวนช่องว่าง หรือแก้สถานะ slot รายช่อง
- `app/routes/ml_routes.py` API สำหรับ ML summary, ML history และอัปโหลดรูปให้ image detection
- `app/routes/__init__.py` ทำให้โฟลเดอร์ routes เป็น Python package

## app/models/

- `app/models/parking.py` database model ของ `ParkingArea` และ `ParkingSlot`
- `app/models/ml_models.py` database model สำหรับ metadata ของ ML model, prediction history และ training history
- `app/models/__init__.py` ทำให้โฟลเดอร์ models เป็น Python package

## app/services/

- `app/services/parking_service.py` business logic หลักของระบบจอดรถ เช่น แปลง model เป็น dict, update slot, sync ผล ML เข้า database
- `app/services/ml_manager.py` business logic ฝั่ง ML database เช่น เพิ่ม model, ตั้ง active model, บันทึก prediction, อ่าน history
- `app/services/__init__.py` ทำให้โฟลเดอร์ services เป็น Python package

## ML/

- `ML/services/parking_prediction_service.py` service สำหรับ prediction แบบ summary จากข้อมูลใน database
- `ML/services/parking_image_detector.py` service สำหรับอัปโหลดรูป, โหลด YOLO model, ตรวจรถ และสรุปสถานะช่องจอด
- `ML/utils/data_preparer.py` เตรียม feature จาก database ให้ prediction service ใช้
- `ML/slots.json` polygon ของช่องจอดในภาพ ใช้บอกว่าแต่ละช่องอยู่ตรงไหน
- `ML/yolov8x.pt` หรือ `ML/parking_model.pt` model weights สำหรับ image detection
- `ML/detect.py`, `ML/polygon.py` script ช่วยงาน ML/manual tooling
- `ML/README.md` เอกสารย่อยของ ML module

## Flow หลัก

1. Frontend เรียก `/api/...`
2. Route ใน `app/routes/` รับ request และ validate input
3. Service ใน `app/services/` หรือ `ML/services/` ทำงานจริง
4. Model ใน `app/models/` อ่าน/เขียน database ผ่าน SQLAlchemy
5. Route ส่ง JSON กลับให้ frontend
