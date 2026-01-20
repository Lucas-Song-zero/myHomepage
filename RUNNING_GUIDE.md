# 网站运行与访问指南

本指南将详细说明如何在本地环境中运行并访问这个Flask个人主页网站。

## 📋 环境要求

- Python 3.11+
- Git（可选，用于克隆项目）

## 🚀 快速开始

### 1. 获取项目代码

#### 方式一：直接下载（推荐）

将项目文件下载并解压到本地目录。

#### 方式二：使用Git克隆

```bash
git clone 
cd homepage
```

### 2. 安装Python依赖

#### 2.1 创建虚拟环境（推荐）

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 安装依赖包

```bash
pip install -r requirements.txt
```

### 3. 初始化数据库

运行数据库初始化脚本：

```bash
python scripts/init_db.py
```

这将创建SQLite数据库文件 `homepage.db` 并初始化所需的表结构。

### 4. 运行应用

#### 4.1 开发环境运行

在开发环境中，可以直接使用Flask内置的服务器运行：

```bash
python app.py
```

#### 4.2 生产环境运行

在生产环境中，建议使用Gunicorn作为WSGI服务器：

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 5. 访问网站

应用启动后，可以通过以下地址访问网站：

- 默认访问地址：http://localhost:5000
- 首页：http://localhost:5000/static/index.html
- 健康检查接口：http://localhost:5000/health

## 📂 网站主要页面

网站包含以下主要页面：

- **首页**：`/static/index.html` - 个人主页
- **博客系统**：`/static/blog.html` - 博客页面
- **管理后台**：`/static/admin_login.html` - 管理员登录页面
- **五子棋游戏**：`/static/gomoku.html` - 五子棋游戏
- **PDF查看器**：`/static/pdf_viewer.html` - PDF文件查看器
- **Markdown查看器**：`/static/markdown_viewer.html` - Markdown文件查看器

## 🔧 高级配置

### 环境变量

可以通过设置以下环境变量来自定义应用配置：

- `PORT`：运行端口（默认：5000）
- `DATABASE_URL`：数据库连接URL（默认：SQLite）
- `SECRET_KEY`：应用密钥（生产环境必须设置）

例如：

```bash
export PORT=8080
export SECRET_KEY="your-secret-key"
python app.py
```

### 自定义背景图

可以将自定义背景图放置在 `static/images/` 目录下，并修改 `index.html` 中的背景图引用。

## 🐛 常见问题

### 1. 无法启动应用

- 检查Python版本是否符合要求（3.11+）
- 确保虚拟环境已激活
- 检查依赖是否已正确安装
- 查看控制台输出的错误信息

### 2. 数据库连接错误

- 确保已运行 `scripts/init_db.py` 初始化数据库
- 检查数据库文件 `homepage.db` 是否存在
- 检查数据库文件权限

### 3. 无法访问页面

- 检查应用是否正在运行
- 检查端口是否被占用
- 尝试访问 http://localhost:5000/health 确认服务状态

## 📝 其他命令

### 数据库管理

```bash
# 查看数据库统计信息
python scripts/manage_db.py stats

# 清理旧访客记录
python scripts/manage_db.py clear 30

# 导出数据
python scripts/manage_db.py export
```

### 重置数据库

```bash
bash scripts/reset_db.sh
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！
