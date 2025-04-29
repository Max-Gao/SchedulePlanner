import requests
import json
from datetime import datetime, timedelta

# 获取当前时间
now = datetime.now()
current_time = now.strftime('%H:%M')
next_minute = (now + timedelta(minutes=1)).strftime('%H:%M')

# 添加测试日程
schedule_data = {
    "title": "测试提醒功能",
    "date": now.strftime('%Y-%m-%d'),
    "start_time": next_minute,
    "end_time": (now + timedelta(minutes=30)).strftime('%H:%M'),
    "reminder_time": current_time  # 设置为当前时间，应该立即触发提醒
}

print(f"创建日程：{schedule_data}")

response = requests.post(
    "http://127.0.0.1:5000/api/schedules",
    json=schedule_data
)

print("添加日程响应:", response.json())
print(f"\n已设置提醒时间为：{current_time}")
print("请等待系统通知...") 