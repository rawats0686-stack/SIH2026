from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pywhatkit as kit
import uvicorn
import os

app = FastAPI(title="KaushalSetu Telemetry Engine")

# CORS Allow All
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SurveyRequest(BaseModel):
    phone: str
    name: str
    course: str
    sector: str

def deliver_whatsapp(phone: str, name: str, course: str, sector: str):
    clean_phone = "".join(filter(str.isdigit, phone))
    if not clean_phone.startswith("91") and len(clean_phone) == 10:
        clean_phone = "91" + clean_phone
    target = f"+{clean_phone}"

    msg = (
        f"Namaste {name} ji,\n\n"
        f"Aapne {course} ({sector}) ka training course complete kiya tha. "
        f"Government Skill Tracking survey ke liye niche diye sawalo ka jawab isi chat me de:\n\n"
        f"1. Kya aapko naukri ya self-employment mila? (Haan / Nahi)\n"
        f"2. Agar Haan: Company Name, Job Role aur Monthly Salary likhein.\n"
        f"3. Agar Nahi: Kaunsi skill missing thi ya interview me kya requirement thi?"
    )

    print(f"[*] Sending message to {target}...")
    try:
        kit.sendwhatmsg_instantly(
            phone_no=target,
            message=msg,
            wait_time=15,
            tab_close=True,
            close_time=4
        )
        print("[+] Delivered successfully!")
    except Exception as e:
        print(f"[-] PyWhatKit Error: {e}")

@app.get("/", response_class=HTMLResponse)
def home():
    html_file = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>index.html not found! Keep index.html and main.py in the same folder.</h1>"

@app.post("/api/send-real-whatsapp")
def send_real_whatsapp(data: SurveyRequest, background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(
            deliver_whatsapp, 
            data.phone, 
            data.name, 
            data.course, 
            data.sector
        )
        return {"status": "success", "phone": data.phone}
    except Exception as err:
        return {"status": "error", "detail": str(err)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
