# Ubuntu 服务器部署指南

本指南将帮助你在 Ubuntu 服务器上部署个人主页项目，并配置 GitHub Actions 自动化部署。

## 📋 前置要求

- Ubuntu 20.04 或更高版本的服务器
- 服务器有公网 IP 地址
- 有服务器的 root 或 sudo 权限
- 已将代码推送到 GitHub 仓库

## 🚀 快速部署

### 第一步：在服务器上初始化环境

1. **SSH 登录到服务器**

```bash
ssh your_username@your_server_ip
```

2. **下载并运行部署脚本**

```bash
# 下载部署脚本
wget https://raw.githubusercontent.com/YOUR_USERNAME/homepage/main/deploy/setup_server.sh

# 或者手动创建脚本文件，复制内容

# 添加执行权限
chmod +x setup_server.sh

# 运行脚本
./setup_server.sh
```

脚本会自动完成以下操作：
- ✅ 安装 Python 3.11, Git, Nginx, Supervisor
- ✅ 克隆代码仓库
- ✅ 创建 Python 虚拟环境
- ✅ 安装项目依赖
- ✅ 配置 Systemd 服务
- ✅ 配置 Nginx 反向代理
- ✅ 启动应用

### 第二步：配置 SSH 密钥（用于 CI/CD）

1. **在服务器上生成部署专用的 SSH 密钥**

```bash
# 创建 .ssh 目录（如果不存在）
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 生成 SSH 密钥对（不要设置密码）
ssh-keygen -t ed25519 -C "deploy-key" -f ~/.ssh/deploy_key -N ""

# 将公钥添加到 authorized_keys
cat ~/.ssh/deploy_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 查看私钥内容（需要添加到 GitHub Secrets）
cat ~/.ssh/deploy_key
```

**重要：** 复制私钥内容（包括 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----`）

### 第三步：配置 GitHub Secrets

在 GitHub 仓库页面：

1. 进入 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**，添加以下密钥：

| Secret 名称 | 值 | 说明 |
|------------|---|------|
| `SERVER_HOST` | `your_server_ip` | 服务器 IP 地址 |
| `SERVER_USER` | `your_username` | 服务器用户名 |
| `SERVER_SSH_KEY` | `私钥内容` | 第二步生成的私钥 |
| `SERVER_PORT` | `22` | SSH 端口（默认 22） |
| `DEPLOY_PATH` | `/home/your_username/homepage` | 部署路径 |

**示例：**
- `SERVER_HOST`: `123.45.67.89`
- `SERVER_USER`: `ubuntu`
- `SERVER_SSH_KEY`: （粘贴完整的私钥内容）
- `SERVER_PORT`: `22`
- `DEPLOY_PATH`: `/home/ubuntu/homepage`

### 第四步：测试部署

1. **推送代码到 GitHub**

```bash
git add .
git commit -m "配置自动化部署"
git push origin main
```

2. **查看 GitHub Actions**

进入仓库的 **Actions** 标签页，查看部署流程是否成功。

3. **访问网站**

在浏览器访问：`http://your_server_ip`

## 🔧 手动部署和管理

### 服务管理命令

```bash
# 查看服务状态
sudo systemctl status homepage

# 启动服务
sudo systemctl start homepage

# 停止服务
sudo systemctl stop homepage

# 重启服务
sudo systemctl restart homepage

# 查看实时日志
sudo journalctl -u homepage -f

# 查看最近的日志
sudo journalctl -u homepage -n 100
```

### 手动更新部署

如果需要手动更新（不通过 CI/CD）：

```bash
cd /home/your_username/homepage
chmod +x deploy/update.sh
./deploy/update.sh
```

### Nginx 管理

```bash
# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🔒 配置 HTTPS（可选但推荐）

使用 Let's Encrypt 免费 SSL 证书：

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书（将 your-domain.com 替换为你的域名）
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

## 🎯 部署架构

```
Internet
   │
   ▼
Nginx (Port 80/443)
   │
   ▼
Gunicorn (Port 5000)
   │
   ▼
Flask Application
   │
   ▼
Static Files
```

## 📁 服务器目录结构

```
/home/your_username/homepage/
├── app.py
├── requirements.txt
├── static/
│   ├── index.html
│   └── images/
├── venv/              # Python 虚拟环境
├── deploy/
│   ├── setup_server.sh
│   └── update.sh
└── .git/
```

## 🐛 常见问题

### 1. 服务启动失败

```bash
# 查看详细错误日志
sudo journalctl -u homepage -n 50

# 检查端口占用
sudo netstat -tlnp | grep 5000

# 检查 Python 路径
which python3.11
```

### 2. Nginx 502 错误

```bash
# 检查 Gunicorn 是否运行
sudo systemctl status homepage

# 检查防火墙
sudo ufw status
sudo ufw allow 80
sudo ufw allow 443
```

### 3. 权限问题

```bash
# 修复文件权限
cd /home/your_username/homepage
sudo chown -R your_username:your_username .
chmod 755 -R static/
```

### 4. CI/CD 部署失败

- 检查 GitHub Secrets 是否配置正确
- 确认 SSH 密钥已添加到服务器
- 查看 Actions 日志中的具体错误信息

## 📊 性能优化建议

1. **配置 Nginx 缓存**
2. **使用 CDN 加速静态资源**
3. **增加 Gunicorn workers 数量**
4. **配置日志轮转**

```bash
# 配置日志轮转
sudo tee /etc/logrotate.d/homepage > /dev/null <<EOF
/var/log/homepage/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
EOF
```

## 🔄 回滚到之前的版本

```bash
cd /home/your_username/homepage
git log --oneline -n 10  # 查看最近的提交
git checkout <commit-hash>  # 回滚到指定版本
sudo systemctl restart homepage
```

## 📞 技术支持

- GitHub Issues: [提交问题](https://github.com/YOUR_USERNAME/homepage/issues)
- 服务器日志: `sudo journalctl -u homepage -f`

## ✅ 部署检查清单

- [ ] 服务器已安装必要软件
- [ ] 代码已克隆到服务器
- [ ] Python 虚拟环境已创建
- [ ] 依赖包已安装
- [ ] Systemd 服务已配置并启动
- [ ] Nginx 已配置反向代理
- [ ] 防火墙已开放 80/443 端口
- [ ] SSH 密钥已生成并配置
- [ ] GitHub Secrets 已配置
- [ ] CI/CD 流程测试通过
- [ ] 网站可以正常访问
- [ ] （可选）SSL 证书已配置

完成以上步骤后，你的个人主页就成功部署了！每次推送代码到 main 分支，都会自动触发部署流程。
