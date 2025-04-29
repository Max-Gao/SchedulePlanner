from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///schedules.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

db = SQLAlchemy(app)

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
            return jsonify({'error': 'End time must be later than start time'}), 400
            
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
        return jsonify({'error': 'Invalid date or time format'}), 400
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
            return jsonify({'error': 'End time must be later than start time'}), 400
            
        schedule.title = data['title']
        schedule.date = data['date']
        schedule.start_time = data['start_time']
        schedule.end_time = data['end_time']
        schedule.reminder_time = data.get('reminder_time')
        db.session.commit()
        return jsonify(schedule.to_dict())
    except ValueError:
        return jsonify({'error': 'Invalid date or time format'}), 400
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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 