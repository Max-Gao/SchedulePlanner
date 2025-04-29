import sys
import requests
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QPushButton, QLabel, QLineEdit,
                           QCalendarWidget, QTimeEdit, QTableWidget,
                           QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from win10toast import ToastNotifier

class SchedulePlanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schedule Planner")
        self.setGeometry(100, 100, 800, 600)
        
        # API configuration
        self.api_url = "http://localhost:5000/api"  # Change this to your deployed API URL
        
        # Initialize Windows notifier
        self.toaster = ToastNotifier()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create form for adding new schedule
        form_layout = QHBoxLayout()
        
        # Title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Title")
        form_layout.addWidget(self.title_input)
        
        # Date picker
        self.calendar = QCalendarWidget()
        form_layout.addWidget(self.calendar)
        
        # Time inputs
        time_layout = QVBoxLayout()
        self.start_time = QTimeEdit()
        self.start_time.setDisplayFormat("HH:mm")
        time_layout.addWidget(QLabel("Start Time:"))
        time_layout.addWidget(self.start_time)
        
        self.end_time = QTimeEdit()
        self.end_time.setDisplayFormat("HH:mm")
        time_layout.addWidget(QLabel("End Time:"))
        time_layout.addWidget(self.end_time)
        
        self.reminder_time = QTimeEdit()
        self.reminder_time.setDisplayFormat("HH:mm")
        time_layout.addWidget(QLabel("Reminder Time:"))
        time_layout.addWidget(self.reminder_time)
        
        form_layout.addLayout(time_layout)
        
        # Add button
        add_button = QPushButton("Add Schedule")
        add_button.clicked.connect(self.add_schedule)
        form_layout.addWidget(add_button)
        
        layout.addLayout(form_layout)
        
        # Create table for displaying schedules
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Date", "Start Time", "End Time", "Reminder Time"])
        layout.addWidget(self.table)
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_schedules)
        layout.addWidget(refresh_button)
        
        # Set up timer for checking reminders
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_reminders)
        self.timer.start(60000)  # Check every minute
        
        # Load initial schedules
        self.load_schedules()
    
    def load_schedules(self):
        try:
            response = requests.get(f"{self.api_url}/schedules")
            if response.status_code == 200:
                schedules = response.json()
                self.table.setRowCount(len(schedules))
                for i, schedule in enumerate(schedules):
                    self.table.setItem(i, 0, QTableWidgetItem(str(schedule['id'])))
                    self.table.setItem(i, 1, QTableWidgetItem(schedule['title']))
                    self.table.setItem(i, 2, QTableWidgetItem(schedule['date']))
                    self.table.setItem(i, 3, QTableWidgetItem(schedule['start_time']))
                    self.table.setItem(i, 4, QTableWidgetItem(schedule['end_time']))
                    self.table.setItem(i, 5, QTableWidgetItem(schedule['reminder_time'] or ""))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load schedules: {str(e)}")
    
    def add_schedule(self):
        try:
            data = {
                'title': self.title_input.text(),
                'date': self.calendar.selectedDate().toString("yyyy-MM-dd"),
                'start_time': self.start_time.time().toString("HH:mm"),
                'end_time': self.end_time.time().toString("HH:mm"),
                'reminder_time': self.reminder_time.time().toString("HH:mm")
            }
            
            response = requests.post(f"{self.api_url}/schedules", json=data)
            if response.status_code == 201:
                self.load_schedules()
                self.title_input.clear()
            else:
                QMessageBox.critical(self, "Error", f"Failed to add schedule: {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add schedule: {str(e)}")
    
    def check_reminders(self):
        try:
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M")
            
            response = requests.get(f"{self.api_url}/schedules")
            if response.status_code == 200:
                schedules = response.json()
                for schedule in schedules:
                    if (schedule['date'] == current_date and 
                        schedule['reminder_time'] == current_time):
                        self.show_reminder(schedule)
        except Exception as e:
            print(f"Error checking reminders: {str(e)}")
    
    def show_reminder(self, schedule):
        message = f"即将开始: {schedule['title']}\n时间: {schedule['start_time']} - {schedule['end_time']}"
        self.toaster.show_toast(
            "日程提醒",
            message,
            duration=30,
            threaded=True
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SchedulePlanner()
    window.show()
    sys.exit(app.exec_()) 