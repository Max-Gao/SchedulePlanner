import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os

class EditDialog:
    def __init__(self, parent, schedule):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("编辑日程")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建输入区域
        self.create_input_area(schedule)
        
        # 添加按钮
        ttk.Button(self.dialog, text="保存", command=self.save).grid(row=4, column=0, columnspan=2, pady=10)
        
        # 配置网格权重
        self.dialog.columnconfigure(1, weight=1)
        
        # 等待对话框关闭
        self.result = None
        parent.wait_window(self.dialog)
    
    def create_input_area(self, schedule):
        # 标题输入
        ttk.Label(self.dialog, text="标题:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.title_entry = ttk.Entry(self.dialog, width=40)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.title_entry.insert(0, schedule["title"])
        
        # 日期输入
        ttk.Label(self.dialog, text="日期:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_entry = ttk.Entry(self.dialog, width=40)
        self.date_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.date_entry.insert(0, schedule["date"])
        
        # 开始时间输入
        ttk.Label(self.dialog, text="开始时间:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.start_time_entry = ttk.Entry(self.dialog, width=40)
        self.start_time_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.start_time_entry.insert(0, schedule["start_time"])
        
        # 结束时间输入
        ttk.Label(self.dialog, text="结束时间:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.end_time_entry = ttk.Entry(self.dialog, width=40)
        self.end_time_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.end_time_entry.insert(0, schedule["end_time"])
    
    def save(self):
        title = self.title_entry.get().strip()
        date = self.date_entry.get().strip()
        start_time = self.start_time_entry.get().strip()
        end_time = self.end_time_entry.get().strip()
        
        if not all([title, date, start_time, end_time]):
            messagebox.showerror("错误", "请填写所有字段", parent=self.dialog)
            return
        
        try:
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
            
            # 检查时间顺序
            start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
            if end_dt <= start_dt:
                messagebox.showerror("错误", "结束时间必须晚于开始时间", parent=self.dialog)
                return
                
        except ValueError:
            messagebox.showerror("错误", "日期或时间格式不正确", parent=self.dialog)
            return
        
        self.result = {
            "title": title,
            "date": date,
            "start_time": start_time,
            "end_time": end_time
        }
        self.dialog.destroy()

class ScheduleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("日程计划应用")
        self.root.geometry("800x500")
        
        # 创建数据存储文件
        self.data_file = "schedule_data.json"
        self.schedules = self.load_schedules()
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建输入区域
        self.create_input_area()
        
        # 创建日程列表
        self.create_schedule_list()
        
        # 创建右键菜单
        self.create_context_menu()
        
        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)

    def create_input_area(self):
        # 标题输入
        ttk.Label(self.main_frame, text="标题:").grid(row=0, column=0, sticky=tk.W)
        self.title_entry = ttk.Entry(self.main_frame, width=40)
        self.title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # 日期输入
        ttk.Label(self.main_frame, text="日期:").grid(row=1, column=0, sticky=tk.W)
        self.date_entry = ttk.Entry(self.main_frame, width=40)
        self.date_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # 开始时间输入
        ttk.Label(self.main_frame, text="开始时间:").grid(row=2, column=0, sticky=tk.W)
        self.start_time_entry = ttk.Entry(self.main_frame, width=40)
        self.start_time_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.start_time_entry.insert(0, datetime.now().strftime("%H:%M"))
        
        # 结束时间输入
        ttk.Label(self.main_frame, text="结束时间:").grid(row=3, column=0, sticky=tk.W)
        self.end_time_entry = ttk.Entry(self.main_frame, width=40)
        self.end_time_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.end_time_entry.insert(0, (datetime.now() + timedelta(hours=1)).strftime("%H:%M"))
        
        # 添加按钮
        ttk.Button(self.main_frame, text="添加日程", command=self.add_schedule).grid(row=4, column=0, columnspan=2, pady=10)

    def create_schedule_list(self):
        # 创建树形视图
        columns = ("标题", "日期", "开始时间", "结束时间")
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=5, column=2, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 删除按钮
        ttk.Button(self.main_frame, text="删除选中", command=self.delete_schedule).grid(row=6, column=0, columnspan=2, pady=5)
        
        # 绑定右键点击事件
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # 加载已有日程
        self.refresh_schedule_list()

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="编辑", command=self.edit_schedule)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def edit_schedule(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先选择要编辑的日程")
            return
        
        index = self.tree.index(selected_items[0])
        schedule = self.schedules[index]
        
        dialog = EditDialog(self.root, schedule)
        if dialog.result:
            self.schedules[index] = dialog.result
            self.save_schedules()
            self.refresh_schedule_list()

    def add_schedule(self):
        title = self.title_entry.get().strip()
        date = self.date_entry.get().strip()
        start_time = self.start_time_entry.get().strip()
        end_time = self.end_time_entry.get().strip()
        
        if not all([title, date, start_time, end_time]):
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        try:
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
            
            # 检查时间顺序
            start_dt = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_dt = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
            if end_dt <= start_dt:
                messagebox.showerror("错误", "结束时间必须晚于开始时间")
                return
                
        except ValueError:
            messagebox.showerror("错误", "日期或时间格式不正确")
            return
        
        schedule = {
            "title": title,
            "date": date,
            "start_time": start_time,
            "end_time": end_time
        }
        
        self.schedules.append(schedule)
        self.save_schedules()
        self.refresh_schedule_list()
        
        # 清空输入框
        self.title_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.start_time_entry.delete(0, tk.END)
        self.end_time_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.start_time_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.end_time_entry.insert(0, (datetime.now() + timedelta(hours=1)).strftime("%H:%M"))

    def delete_schedule(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("提示", "请先选择要删除的日程")
            return
        
        for item in selected_items:
            index = self.tree.index(item)
            del self.schedules[index]
        
        self.save_schedules()
        self.refresh_schedule_list()

    def refresh_schedule_list(self):
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 按日期和开始时间排序
        sorted_schedules = sorted(self.schedules, key=lambda x: (x["date"], x["start_time"]))
        
        # 添加日程到列表
        for schedule in sorted_schedules:
            self.tree.insert("", tk.END, values=(
                schedule["title"],
                schedule["date"],
                schedule["start_time"],
                schedule["end_time"]
            ))

    def load_schedules(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    schedules = json.load(f)
                    # 转换旧格式数据
                    converted_schedules = []
                    for schedule in schedules:
                        if "datetime" in schedule:
                            # 旧格式1：datetime字段
                            dt = datetime.strptime(schedule["datetime"], "%Y-%m-%d %H:%M")
                            converted_schedule = {
                                "title": schedule["title"],
                                "date": dt.strftime("%Y-%m-%d"),
                                "start_time": dt.strftime("%H:%M"),
                                "end_time": (dt + timedelta(hours=1)).strftime("%H:%M")
                            }
                        elif "date" in schedule and "time" in schedule:
                            # 旧格式2：date和time字段
                            dt = datetime.strptime(f"{schedule['date']} {schedule['time']}", "%Y-%m-%d %H:%M")
                            converted_schedule = {
                                "title": schedule["title"],
                                "date": dt.strftime("%Y-%m-%d"),
                                "start_time": dt.strftime("%H:%M"),
                                "end_time": (dt + timedelta(hours=1)).strftime("%H:%M")
                            }
                        else:
                            # 已经是新格式数据
                            converted_schedule = schedule
                        converted_schedules.append(converted_schedule)
                    return converted_schedules
            except:
                return []
        return []

    def save_schedules(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.schedules, f, ensure_ascii=False, indent=2)

def main():
    root = tk.Tk()
    app = ScheduleApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 