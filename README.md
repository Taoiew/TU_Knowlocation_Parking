# Pain Point
  “Students may have difficulty finding available parking areas on campus.”
  # Problem
  1. หาที่จอดรถยาก (avilable / not available)
  2. ไม่รู้ว่าที่ไหนจอดได้บ้าง (นักศึกษา/บุคคลากร)
  3. ไม่รู้ตำแหน่งที่จอดแบบชัดเจน
  4. ไม่มีประชาสัมพันธ์เกี่ยวกับที่จอดรถ
# Solution
    1.Parking location : พิกัดที่จอดรถ
    2.Parking Status : สถานะของที่จอดรถ 
      (available / not available / pending)
    3.Parking Type : ที่จอดรถสำหรับผู้ใช้งานแต่ละกลุ่ม
      (general / staff / handicaps)
# Beneficial
  1. ประหยัดเวลาในการหาที่จอดรถ
  2. ลดความเสี่ยงในการจอดผิดที่
  3. เข้าถึงข้อมูลที่จอดรถแบบชัดเจน

# System Architecture
<img width="1919" height="1079" alt="Screenshot 2026-04-30 205740" src="https://github.com/user-attachments/assets/eb52f2a8-932d-4819-b68a-c4ca169425a4" />
  
# Class Diagram(UML)
<img width="1265" height="653" alt="678422613_1296734052553127_168391006614671707_n" src="https://github.com/user-attachments/assets/5f42bef3-0a7e-48f7-991e-d66607fe59b0" />
  
# ผลการดำเนินงาน
  Frontend: https://github.com/ShinyG1thub/CS242-TUParkingLocation-Frontend.git
  Backend: https://github.com/ShinyG1thub/CS242-TUParkingLocation-Backend.git
  ML: https://colab.research.google.com/drive/1MBmaJ4TmNKlHyuM3Qv_dYDqaFrnk1TRa?usp=sharing
  Implementation: https://github.com/Taoiew/TU_Knowlocation_Parking.git
# แจกแจงงานที่สมาชิกแต่ละคน
1.นายอธิชล เรืองหิรัญ (6709681172): Frontend + Backend
2.นายกรกฎ หาญมนตรี (6709616376): Machine Learning + Implementation
3.นายพัชรพล คุณวโรตม์ (6709616715): Backend
4.นายชยากร จิตรอุดมกุล (6709616400): Backend
5.นายชัชวีร์ ไทยเจริญ (6709616426): Frontend


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

## Run With Docker

This setup runs 3 services:
- `frontend`: React + Vite on port `5173`
- `backend`: Flask + Gunicorn on port `5000`
- `db`: PostgreSQL on port `5432`

Create or edit `.env` from `.env.example` if you need different ports or database credentials.

```bash
docker compose up --build
```

URLs:
- Frontend: `http://localhost:5173`
- Testing page: `http://localhost:5173/test`
- Backend health check: `http://localhost:5000/api/health`
- ML health check: `http://localhost:5000/api/ml/health`
- ML summary prediction: `POST http://localhost:5000/api/parking/areas/1/ml-predict`
- Backend API: `http://localhost:5000/api/parking/areas`

Open the frontend from the host port, for example `http://localhost:5173`.
Do not use the Vite container network URL such as `http://172.x.x.x:5173`; that address is only for Docker's internal network.
For ngrok demos, `.ngrok-free.dev` is allowed by Vite through `VITE_ALLOWED_HOSTS`.

Stop services:

```bash
docker compose down
```

Reset database data:

```bash
docker compose down -v
```

## ML Model Files

โค้ด ML อยู่ใน repo แต่ไฟล์ model weights ขนาดใหญ่จะไม่ถูกเก็บใน Git เพราะเกิน limit ของ GitHub
resource: https://drive.google.com/drive/folders/1TVxRAQsIOhJNHmLgDyn_ioq2BS7dwxKI?usp=sharing
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
