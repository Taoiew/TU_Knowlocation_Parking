# TUparkingLocation

ระบบเว็บสำหรับดูสถานะที่จอดรถ โดยแยก frontend และ backend ออกจากกัน:
- Backend: Flask + SQLAlchemy
- Frontend: React + Vite + TypeScript
- ML: ตรวจจับสถานะที่จอดจากรูปภาพในโฟลเดอร์ `ML`

## Project Structure

```text
CS242_TUParkingLocation/
|- app/                 # Flask backend
|- frontend/            # React frontend
|- ML/                  # ML scripts, polygons, model lookup path
|- requirements.txt     # Python dependencies
|- run.py               # Start backend
|- system_check.py      # Project health check
|- TESTING_GUIDE.md     # Manual/system testing guide
```

## Run Locally

Backend:

```bash
pip install -r requirements.txt
python run.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

URLs:
- Frontend: `http://localhost:5173`
- Testing page: `http://localhost:5173/test`
- Backend API: `http://localhost:5000/api/parking/areas`

## ML Model Files

โค้ด ML อยู่ใน repo แต่ไฟล์ model weights ขนาดใหญ่จะไม่ถูกเก็บใน Git เพราะเกิน limit ของ GitHub

ไฟล์ที่ต้องเตรียมเองถ้าจะใช้ ML image detection:
- `ML/yolov8x.pt`
- หรือ `ML/parking_model.pt`

หมายเหตุ:
- ถ้าไม่มีไฟล์ `.pt` ระบบส่วน backend/frontend หลักยังทำงานได้
- แต่ฟีเจอร์อัปโหลดรูปในหน้า `/test` และ endpoint ML image detection จะใช้ไม่ได้

ลำดับการใช้งาน ML:
1. วางไฟล์ model ไว้ในโฟลเดอร์ `ML/`
2. ติดตั้ง dependencies จาก `requirements.txt`
3. เปิดหน้า `/test`
4. อัปโหลดรูปภาพเพื่อให้ ML วิเคราะห์สถานะที่จอด

## Git Notes

ไฟล์ต่อไปนี้ถูก ignore ไว้และไม่ควร push ขึ้น GitHub:
- virtual environments
- database/runtime files
- frontend build output
- ML model weights เช่น `ML/*.pt`

ถ้าคุณมี model file อยู่ในเครื่องและเคย `git add` ไปแล้ว ให้เอาออกจาก tracking ก่อน:

```bash
git rm --cached ML/parking_model.pt
git rm --cached ML/yolov8x.pt
```

แล้วค่อย commit ใหม่

## Testing

ดูขั้นตอนทดสอบทั้งหมดได้ใน [TESTING_GUIDE.md](./TESTING_GUIDE.md)
