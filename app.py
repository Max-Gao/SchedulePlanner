from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, gettext as _
from datetime import datetime, timedelta
import os
import threading
import time
from win10toast import ToastNotifier

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///schedules.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['LANGUAGES'] = ['en', 'zh', 'es', 'fr', 'de', 'ja', 'ko', 'ru', 'ar']
app.secret_key = os.urandom(24)

# 创建全局的 ToastNotifier 实例
toaster = ToastNotifier()

# 用于跟踪已发送的提醒
sent_reminders = set()

def get_locale():
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(app.config['LANGUAGES'])

db = SQLAlchemy(app)
babel = Babel(app, locale_selector=get_locale)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.String(5), nullable=False)
    end_time = db.Column(db.String(5), nullable=False)
    reminder_time = db.Column(db.String(5), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'date': self.date,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'reminder_time': self.reminder_time
        }

with app.app_context():
    db.create_all()

def check_reminders():
    with app.app_context():
        try:
            now = datetime.now()
            current_date = now.strftime('%Y-%m-%d')
            current_time = now.strftime('%H:%M')
            
            print(f"正在检查提醒 - 当前时间: {current_date} {current_time}")
            
            # 查找需要提醒的日程
            schedules = Schedule.query.filter(
                Schedule.date == current_date,
                Schedule.reminder_time == current_time
            ).all()
            
            print(f"找到 {len(schedules)} 个需要提醒的日程")
            
            for schedule in schedules:
                # 创建唯一标识符
                reminder_key = f"{schedule.id}_{schedule.date}_{schedule.reminder_time}"
                
                # 检查是否已经发送过提醒
                if reminder_key not in sent_reminders:
                    try:
                        print(f"正在处理日程提醒: {schedule.title}")
                        message = f"即将开始: {schedule.title}\n时间: {schedule.start_time} - {schedule.end_time}"
                        print(f"提醒内容: {message}")
                        
                        # 发送 Windows 通知，设置较长的持续时间
                        toaster.show_toast(
                            "日程提醒",
                            message,
                            duration=30,  # 增加持续时间
                            threaded=True
                        )
                        
                        # 立即记录已发送的提醒，不等待通知关闭
                        sent_reminders.add(reminder_key)
                        
                        print(f"已发送通知: {schedule.title}")
                    except Exception as e:
                        print(f"发送通知时出错: {str(e)}")
        except Exception as e:
            print(f"检查提醒时出错: {str(e)}")

def reminder_thread():
    print("提醒线程已启动")
    while True:
        try:
            check_reminders()
            # 增加检查间隔到1分钟，减少重复检查的可能性
            time.sleep(60)
        except Exception as e:
            print(f"提醒线程出错: {str(e)}")
            time.sleep(60)

# 启动提醒线程
reminder_thread = threading.Thread(target=reminder_thread, daemon=True)
reminder_thread.start()
print("提醒线程启动成功")

@app.route('/test_reminder')
def test_reminder():
    try:
        message = "这是一条测试通知"
        print(f"正在发送测试通知: {message}")
        toaster.show_toast(
            "测试提醒",
            message,
            duration=30,
            threaded=True
        )
        return jsonify({'status': 'success', 'message': '测试通知已发送'})
    except Exception as e:
        print(f"发送测试通知时出错: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/')
def index():
    schedules = Schedule.query.order_by(Schedule.date, Schedule.start_time).all()
    return render_template('index.html', schedules=schedules)

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in app.config['LANGUAGES']:
        session['language'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    schedules = Schedule.query.order_by(Schedule.date, Schedule.start_time).all()
    return jsonify([schedule.to_dict() for schedule in schedules])

@app.route('/api/schedules', methods=['POST'])
def add_schedule():
    data = request.json
    try:
        # 验证日期和时间格式
        datetime.strptime(data['date'], '%Y-%m-%d')
        datetime.strptime(data['start_time'], '%H:%M')
        datetime.strptime(data['end_time'], '%H:%M')
        if 'reminder_time' in data and data['reminder_time']:
            datetime.strptime(data['reminder_time'], '%H:%M')
        
        # 检查时间顺序
        start_dt = datetime.strptime(f"{data['date']} {data['start_time']}", '%Y-%m-%d %H:%M')
        end_dt = datetime.strptime(f"{data['date']} {data['end_time']}", '%Y-%m-%d %H:%M')
        if end_dt <= start_dt:
            return jsonify({'error': _('End time must be later than start time')}), 400
            
        schedule = Schedule(
            title=data['title'],
            date=data['date'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            reminder_time=data.get('reminder_time')
        )
        db.session.add(schedule)
        db.session.commit()
        return jsonify(schedule.to_dict()), 201
    except ValueError:
        return jsonify({'error': _('Invalid date or time format')}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/schedules/<int:id>', methods=['PUT'])
def update_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    data = request.json
    try:
        # 验证日期和时间格式
        datetime.strptime(data['date'], '%Y-%m-%d')
        datetime.strptime(data['start_time'], '%H:%M')
        datetime.strptime(data['end_time'], '%H:%M')
        if 'reminder_time' in data and data['reminder_time']:
            datetime.strptime(data['reminder_time'], '%H:%M')
        
        # 检查时间顺序
        start_dt = datetime.strptime(f"{data['date']} {data['start_time']}", '%Y-%m-%d %H:%M')
        end_dt = datetime.strptime(f"{data['date']} {data['end_time']}", '%Y-%m-%d %H:%M')
        if end_dt <= start_dt:
            return jsonify({'error': _('End time must be later than start time')}), 400
            
        schedule.title = data['title']
        schedule.date = data['date']
        schedule.start_time = data['start_time']
        schedule.end_time = data['end_time']
        schedule.reminder_time = data.get('reminder_time')
        db.session.commit()
        return jsonify(schedule.to_dict())
    except ValueError:
        return jsonify({'error': _('Invalid date or time format')}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/schedules/<int:id>', methods=['DELETE'])
def delete_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    db.session.delete(schedule)
    db.session.commit()
    return '', 204

@app.route('/api/schedules/<int:id>', methods=['GET'])
def get_schedule(id):
    schedule = Schedule.query.get_or_404(id)
    return jsonify(schedule.to_dict())

if __name__ == '__main__':
    app.run(debug=True) 