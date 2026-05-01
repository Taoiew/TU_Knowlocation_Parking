from flask_sqlalchemy import SQLAlchemy

# สร้าง SQLAlchemy ไว้กลางโปรเจกต์ก่อน แล้วค่อยผูกกับ Flask app ใน create_app()
# วิธีนี้ช่วยให้ models/services import `db` ได้โดยไม่เกิด circular import
db = SQLAlchemy()
