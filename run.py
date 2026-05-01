"""Entry point to run the Flask application."""

import os

from app import create_app

# Flask app instance ตัวนี้ถูกใช้ทั้งตอน `python run.py` และตอน Gunicorn import `run:app`
app = create_app()

if __name__ == "__main__":
    # bind 0.0.0.0 เพื่อให้เครื่องอื่นในวง network เปิดผ่าน IP เครื่องเราได้
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
