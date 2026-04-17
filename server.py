from flask import Flask, render_template
from flask_socketio import SocketIO, send
from thefuzz import process 
import wikipediaapi # Library สำหรับดึงข้อมูล

app = Flask(__name__)
app.config['SECRET_KEY'] = 'psu-bot-search-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# สร้างตัวค้นหาข้อมูล (ระบุภาษาไทย)
wiki = wikipediaapi.Wikipedia(
    language='th',
    user_agent='PSU_Student_Bot/1.0 (contact: student@example.com)'
)

knowledge_base = {
    "สวัสดีครับ": "สวัสดีครับ! ผมคือบอทหาข้อมูล มีอะไรอยากทราบไหมครับ?",
}

def get_chatbot_response(user_text):
    # 1. ลองหาในฐานข้อมูลส่วนตัวก่อน (ใช้ Fuzzy Matching)
    result = process.extractOne(user_text, knowledge_base.keys())
    if result and result[1] > 70: 
        return knowledge_base[result[0]]
    
    # 2. ถ้าในฐานข้อมูลไม่มี ให้ไปหาใน Wikipedia
    try:
        page = wiki.page(user_text)
        if page.exists():
            # ดึงมาแค่ 200 ตัวอักษรแรกเพื่อให้สรุปสั้นๆ
            return f"ข้อมูลจาก Wikipedia: {page.summary[:300]}..."
        else:
            return "ขออภัยครับ ผมพยายามหาข้อมูลแล้วแต่ไม่พบ ลองเปลี่ยนคำค้นหาดูนะครับ"
    except:
        return "เกิดข้อผิดพลาดในการเชื่อมต่อฐานข้อมูลภายนอกครับ"

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    username = data.get('user', 'User')
    user_msg = data.get('msg', '')
    
    send({'user': username, 'msg': user_msg}, broadcast=True)
    
    bot_reply = get_chatbot_response(user_msg)
    send({'user': 'PSU Information Bot', 'msg': bot_reply}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
