# Schedule Planner

一个日程管理应用程序，包含后端API和Windows客户端。后端部署在AWS上，客户端运行在本地Windows系统上。

## 项目架构

项目分为两个主要部分：

1. **后端API** (`app.py`)
   - 基于Flask的RESTful API
   - 使用PostgreSQL数据库存储数据
   - 部署在AWS Elastic Beanstalk上

2. **Windows客户端** (`client.py`)
   - 基于PyQt5的图形界面
   - 使用Windows通知系统
   - 通过API与后端通信

## 文件结构

```
SchedulePlanner/
├── app.py                 # 后端API主文件
├── requirements.txt       # 后端依赖
├── Procfile              # Elastic Beanstalk配置文件
├── client.py             # Windows客户端主文件
├── client_requirements.txt # 客户端依赖
└── .ebextensions/        # Elastic Beanstalk配置目录
    └── 01_environment.config  # 环境变量配置
```

## 功能特点

- 创建、查看、更新和删除日程
- 设置日程提醒时间
- Windows系统通知提醒
- 多语言支持
- 响应式设计

## 安装和配置

### 后端部署

1. 在AWS上创建RDS PostgreSQL数据库
2. 配置环境变量：
   ```
   DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/dbname
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=production
   ```
3. 部署到Elastic Beanstalk：
   ```bash
   eb init
   eb create
   eb deploy
   ```

### 客户端安装

1. 安装Python依赖：
   ```bash
   pip install -r client_requirements.txt
   ```

2. 配置API地址：
   - 打开`client.py`
   - 修改`self.api_url`为你的Elastic Beanstalk应用URL

3. 运行客户端：
   ```bash
   python client.py
   ```

## API接口

### 获取所有日程
- **GET** `/api/schedules`
- 返回所有日程列表

### 创建新日程
- **POST** `/api/schedules`
- 请求体：
  ```json
  {
    "title": "会议",
    "date": "2024-03-20",
    "start_time": "14:00",
    "end_time": "15:00",
    "reminder_time": "13:45"
  }
  ```

### 更新日程
- **PUT** `/api/schedules/<id>`
- 请求体：同创建日程

### 删除日程
- **DELETE** `/api/schedules/<id>`

### 获取单个日程
- **GET** `/api/schedules/<id>`

## 使用说明

1. **添加日程**
   - 在标题输入框中输入日程标题
   - 选择日期
   - 设置开始时间、结束时间和提醒时间
   - 点击"Add Schedule"按钮

2. **查看日程**
   - 日程列表会自动显示在表格中
   - 可以点击"Refresh"按钮刷新列表

3. **接收提醒**
   - 当到达提醒时间时，会显示Windows通知
   - 通知包含日程标题和时间信息

## 注意事项

- 确保客户端能够访问后端API
- 保持客户端程序运行以接收提醒
- 建议使用强密码保护数据库
- 定期备份数据库

## 故障排除

1. **无法连接到API**
   - 检查网络连接
   - 确认API URL配置正确
   - 检查防火墙设置

2. **通知不显示**
   - 确保Windows通知设置已启用
   - 检查程序是否在运行
   - 确认系统时间正确

3. **数据库连接问题**
   - 检查数据库连接字符串
   - 确认数据库服务正在运行
   - 验证数据库用户权限

## 技术支持

如有问题，请提交Issue或联系技术支持。

## 许可证

MIT License 