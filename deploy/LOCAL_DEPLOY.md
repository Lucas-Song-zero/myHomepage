# 本地部署脚本使用指南

## 📁 脚本说明

### 1. deploy_local.sh - 完整部署
从 GitHub 拉取最新代码并部署到服务器

**特点：**
- ✅ 从 GitHub 拉取最新代码
- ✅ 使用临时目录，不影响本地
- ✅ 自动同步到服务器
- ✅ 自动安装依赖
- ✅ 自动重启服务
- ✅ 显示详细进度

### 2. deploy_quick.sh - 快速部署
直接从当前目录部署到服务器

**特点：**
- ✅ 快速，无需从 GitHub 拉取
- ✅ 适合本地开发测试
- ✅ 同步当前目录代码
- ✅ 自动重启服务

---

## 🚀 使用方法

### 方式 1：从 GitHub 部署（推荐）

```bash
./deploy_local.sh
```

**流程：**
1. 从 GitHub 克隆最新代码到临时目录
2. 同步代码到服务器
3. 在服务器上安装依赖
4. 重启服务
5. 清理临时文件

### 方式 2：快速部署（开发测试）

```bash
./deploy_quick.sh
```

**流程：**
1. 直接同步当前目录到服务器
2. 在服务器上安装依赖
3. 重启服务

---

## 📋 前置要求

### 1. SSH 配置

确保 `~/.ssh/config` 中已配置服务器：

```ssh-config
Host www.weitao-jiang.cn
  HostName www.weitao-jiang.cn
  User root
  Port 22
  IdentityFile /Users/weitaojiang/.ssh/id_ed25519
```

### 2. SSH 密钥

确保可以免密登录：

```bash
# 测试连接
ssh www.weitao-jiang.cn "echo 'Connection OK'"
```

如果提示输入密码，需要配置 SSH 密钥：

```bash
ssh-copy-id www.weitao-jiang.cn
```

### 3. 服务器初始化

确保服务器已运行初始化脚本：

```bash
# 在服务器上
chmod +x deploy/setup.sh
./deploy/setup.sh
```

---

## 🎯 使用场景

### 场景 1：生产环境部署
使用 `deploy_local.sh` 确保部署的是 GitHub 上的最新代码：

```bash
# 1. 提交代码到 GitHub
git add .
git commit -m "更新功能"
git push origin master

# 2. 从 GitHub 部署
./deploy_local.sh
```

### 场景 2：快速测试
使用 `deploy_quick.sh` 快速测试本地修改：

```bash
# 修改代码后直接部署
./deploy_quick.sh
```

### 场景 3：紧急修复
快速修复线上问题：

```bash
# 1. 本地修改
vim app.py

# 2. 快速部署
./deploy_quick.sh

# 3. 确认没问题后提交
git add .
git commit -m "修复 bug"
git push origin master
```

---

## 🔧 自定义配置

### 修改服务器地址

编辑脚本，修改配置部分：

```bash
# 打开脚本
vim deploy_local.sh

# 修改配置
SERVER_HOST="your-server.com"
SERVER_USER="your-username"
DEPLOY_PATH="/path/to/deploy"
```

### 修改排除文件

在 `rsync` 命令中添加 `--exclude` 选项：

```bash
rsync -avz \
    --exclude 'your-file' \
    --exclude 'your-folder' \
    ...
```

---

## 📝 常用命令

### 查看服务状态

```bash
ssh www.weitao-jiang.cn "sudo systemctl status homepage"
```

### 查看日志

```bash
ssh www.weitao-jiang.cn "sudo journalctl -u homepage -f"
```

### 重启服务

```bash
ssh www.weitao-jiang.cn "sudo systemctl restart homepage"
```

### 手动更新依赖

```bash
ssh www.weitao-jiang.cn << 'EOF'
cd /root/homepage
source venv/bin/activate
pip install -r requirements.txt
EOF
```

---

## 🐛 故障排查

### 问题 1：SSH 连接失败

```bash
# 测试连接
ssh -v www.weitao-jiang.cn

# 检查 SSH 配置
cat ~/.ssh/config | grep -A 5 www.weitao-jiang.cn
```

### 问题 2：权限错误

```bash
# 检查服务器目录权限
ssh www.weitao-jiang.cn "ls -la /root/"

# 修复权限
ssh www.weitao-jiang.cn "sudo chown -R root:root /root/homepage"
```

### 问题 3：服务启动失败

```bash
# 查看详细错误
ssh www.weitao-jiang.cn "sudo journalctl -u homepage -n 50"

# 手动启动测试
ssh www.weitao-jiang.cn "cd /root/homepage && source venv/bin/activate && python app.py"
```

### 问题 4：依赖安装失败

```bash
# SSH 到服务器手动安装
ssh www.weitao-jiang.cn
cd /root/homepage
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -v
```

---

## ⚡ 性能优化

### 使用压缩传输

脚本已默认使用 `-z` 参数启用压缩。

### 增量同步

rsync 默认只传输修改的文件，已是增量同步。

### 并行执行

如果需要同时部署多个服务器，可以使用：

```bash
./deploy_quick.sh &
ssh server2 "deploy command" &
wait
```

---

## 🔒 安全建议

1. **使用 SSH 密钥**：不要在脚本中存储密码
2. **限制权限**：脚本权限设为 700
   ```bash
   chmod 700 deploy_*.sh
   ```
3. **审计日志**：记录每次部署
   ```bash
   ./deploy_local.sh 2>&1 | tee -a deploy.log
   ```

---

## 📚 相关文档

- [deploy/README.md](deploy/README.md) - 服务器部署指南
- [deploy/QUICKSTART.md](deploy/QUICKSTART.md) - 快速开始
- [DEPLOYMENT.md](DEPLOYMENT.md) - 完整部署文档

---

## 💡 提示

- 首次部署使用 `deploy_local.sh`
- 日常开发使用 `deploy_quick.sh`
- 定期从 GitHub 部署确保代码一致性
- 重要更新前先在测试环境验证

祝部署顺利！🚀
