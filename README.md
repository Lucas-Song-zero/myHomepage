# 个人主页

一个现代化的个人主页项目，采用 Python Flask 后端 + HTML/CSS 前端构建。

## ✨ 功能特性

- 🎨 简洁优雅的首页设计（渐变色背景）
- 📊 访客统计功能（自动记录）
- � 留言板系统
- 🗄️ SQLite 数据库支持
- 🔐 HTTPS/SSL 加密（自签名证书）
- 🚀 自动化部署脚本
- � 健康检查接口

## 📁 项目结构

```
homepage/
├── app.py                    # Flask 应用主文件
├── requirements.txt          # Python 依赖
├── .gitignore               # Git 忽略文件
│
├── static/                  # 静态文件目录
│   ├── index.html          # 首页
│   └── images/             # 图片目录（可放置背景图）
│
├── scripts/                 # 工具脚本
│   ├── init_db.py          # 数据库初始化
│   └── manage_db.py        # 数据库管理工具
│
├── deploy/                  # 部署相关
│   ├── deploy_local.sh     # 本地部署脚本
│   ├── deploy_quick.sh     # 快速部署脚本
│   ├── deploy_config.example.sh  # 配置文件示例
│   └── *.md                # 部署文档
│
└── .github/
    └── workflows/
        └── ci-cd.yml       # GitHub Actions 配置
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/CBDT-JWT/Home.git
cd homepage
```

### 2. 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
python scripts/init_db.py
```

### 4. 运行应用

```bash
# 开发环境
python app.py

# 生产环境
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

访问 http://localhost:5000 查看效果。

## 📡 API 接口

### 健康检查
```bash
GET /health
```
返回服务状态和数据库连接状态。

### 访客统计
```bash
GET /api/visitors
```
获取访客总数和最近访客记录。

### 留言板
```bash
# 获取所有留言
GET /api/messages

# 提交留言
POST /api/messages
Content-Type: application/json

{
  "name": "访客名称",
  "email": "email@example.com",  # 可选
  "content": "留言内容"
}
```

## 🗄️ 数据库管理

### 查看统计
```bash
python scripts/manage_db.py stats
```

### 清理旧数据
```bash
# 清理30天前的访客记录
python scripts/manage_db.py clear 30
```

### 导出数据
```bash
python scripts/manage_db.py export
```

## 🚀 生产环境部署

### 方式一：快速部署（推荐）

1. 复制配置文件：
```bash
cp deploy/deploy_config.example.sh deploy_config.sh
```

2. 编辑 `deploy_config.sh` 填写服务器信息

3. 执行部署：
```bash
# 从 GitHub 拉取并部署
./deploy/deploy_local.sh

# 或直接部署当前目录
./deploy/deploy_quick.sh
```

### 方式二：手动部署

详见 `deploy/` 目录下的部署文档。

### 使用 systemd 管理服务

服务配置文件位于服务器的 `/etc/systemd/system/homepage.service`

```bash
# 启动服务
sudo systemctl start homepage

# 停止服务
sudo systemctl stop homepage

# 重启服务
sudo systemctl restart homepage

# 查看状态
sudo systemctl status homepage

# 查看日志
sudo journalctl -u homepage -f
```

## 🔐 SSL/HTTPS 配置

项目已配置 HTTPS（使用自签名证书）。

要使用真实证书，请参考 `SSL_SETUP.md` 文档。

## 🛠️ 技术栈

- **后端**: Python 3.11+ / Flask 3.0
- **数据库**: SQLite / Flask-SQLAlchemy 3.1
- **前端**: HTML5 / CSS3
- **服务器**: Gunicorn 21.2 / Nginx
- **部署**: systemd / rsync

## 📝 开发说明

### 环境变量

- `PORT`: 运行端口（默认：443）
- `DATABASE_URL`: 数据库连接（默认：sqlite:///homepage.db）
- `SECRET_KEY`: 密钥（生产环境必须设置）

### 开发模式

```bash
export PORT=5000
python app.py  # 启用 debug 模式
```

## 📄 许可证

MIT License

## 🔗 相关链接

- 在线地址：https://www.weitao-jiang.cn
- GitHub：https://github.com/CBDT-JWT/Home

## 开发建议

- 使用虚拟环境管理 Python 依赖
- 推送代码前确保通过本地测试
- 定期更新依赖包

## API 接口

- `GET /`: 返回首页
- `GET /health`: 健康检查接口

## 许可证

MIT License

## 作者

[Your Name]

## 贡献

欢迎提交 Issue 和 Pull Request！
