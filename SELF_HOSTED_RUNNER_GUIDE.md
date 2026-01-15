# Self-hosted Runner 部署方案

## 📖 什么是 Self-hosted Runner？

Self-hosted Runner（自托管运行器）是运行在**你自己服务器上**的 GitHub Actions 执行器。与 GitHub 托管的运行器不同，它直接在你的服务器上执行部署任务，无需通过 SSH 远程连接。

### 🎯 适用场景

- ✅ 服务器在内网或私有网络（GitHub 托管运行器无法访问）
- ✅ 不想配置复杂的 SSH 密钥和防火墙规则
- ✅ 需要访问本地资源（数据库、内网服务等）
- ✅ 希望更快的部署速度（本地操作）
- ✅ 长期项目（免费且无使用时长限制）

---

## 🚀 快速设置指南

### 第一步：在服务器上安装 Runner

#### 1. 获取 Runner Token

在 GitHub 仓库页面：**Settings** → **Actions** → **Runners** → **New self-hosted runner**

选择操作系统（Linux）后，GitHub 会显示安装命令。

#### 2. 在服务器上执行安装命令

```bash
# SSH 登录到你的服务器
ssh your_user@your_server.com

# 创建 Runner 工作目录
mkdir -p ~/actions-runner && cd ~/actions-runner

# 下载 Runner（复制 GitHub 页面上的命令）
# 示例命令（实际 URL 和 token 请从 GitHub 获取）：
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# 解压
tar xzf ./actions-runner-linux-x64-*.tar.gz

# 配置 Runner（使用 GitHub 提供的 token）
./config.sh --url https://github.com/CBDT-JWT/Home --token YOUR_TOKEN_HERE

# 交互式配置：
# - Runner group: 直接回车（使用 Default）
# - Runner name: 输入名称，如 "homepage-server"
# - Labels: 直接回车（使用默认）
# - Work folder: 直接回车（使用 _work）
```

#### 3. 配置 Runner 工作目录指向项目路径

为了让 Runner 直接在你的项目目录工作，需要特殊配置：

```bash
# 方法 1：使用符号链接（推荐）
cd ~/actions-runner/_work/Home/Home
# 这个目录会在第一次运行后创建

# 方法 2：直接指定项目路径作为工作目录
# 在配置时指定: --work /path/to/your/homepage
```

#### 4. 安装并启动 Runner 服务

```bash
cd ~/actions-runner

# 安装为系统服务（推荐，开机自启）
sudo ./svc.sh install

# 启动服务
sudo ./svc.sh start

# 查看状态
sudo ./svc.sh status

# 查看日志
journalctl -u actions.runner.* -f
```

**或者前台运行（测试用）：**

```bash
./run.sh
```

### 第二步：修改工作流配置

我已经创建了新的工作流文件：`.github/workflows/deploy-self-hosted.yml`

**关键修改：**

```yaml
jobs:
  deploy:
    runs-on: self-hosted  # 使用自托管运行器（而不是 ubuntu-latest）
```

这个工作流会：
1. ✅ 检出代码到 Runner 的工作目录
2. ✅ 激活/创建 Python 虚拟环境
3. ✅ 安装依赖
4. ✅ 构建文档（如果需要）
5. ✅ 初始化数据库（如果不存在）
6. ✅ 创建必要目录
7. ✅ 重启服务

### 第三步：配置 sudoers（重启服务权限）

```bash
# 在服务器上运行
sudo visudo

# 添加以下行（替换 your_user 为实际的 Runner 运行用户）
your_user ALL=(ALL) NOPASSWD: /bin/systemctl restart homepage
your_user ALL=(ALL) NOPASSWD: /bin/systemctl status homepage
```

**或者，如果你用 root 运行 Runner（不推荐但更简单）：**

```bash
# 以 root 安装和运行 Runner
sudo ./svc.sh install root
sudo ./svc.sh start
```

### 第四步：测试部署

#### 方法 1：推送代码触发

```bash
# 在本地推送到 master 分支
git add .
git commit -m "Test self-hosted runner deployment"
git push origin master
```

#### 方法 2：手动触发

在 GitHub 仓库页面：**Actions** → **Deploy (Self-hosted Runner)** → **Run workflow**

---

## 🔍 验证 Runner 状态

### 在 GitHub 上查看

**Settings** → **Actions** → **Runners**

你应该看到：
- 🟢 绿色圆点 = Runner 在线且空闲
- 🔵 蓝色圆点 = Runner 正在执行任务
- 🔴 红色 = Runner 离线

### 在服务器上查看

```bash
# 查看 Runner 服务状态
sudo systemctl status actions.runner.*

# 查看实时日志
journalctl -u actions.runner.* -f

# 或者查看 Runner 日志文件
cd ~/actions-runner
tail -f _diag/Runner_*.log
```

---

## 🆚 两种方案对比

### Self-hosted Runner（新方案）

**优点：**
- ✅ 无需配置 SSH 密钥
- ✅ 可访问内网/私有网络
- ✅ 部署速度更快（本地操作）
- ✅ 免费且无时长限制
- ✅ 配置简单（一次性）

**缺点：**
- ⚠️ 需要服务器始终在线
- ⚠️ 需要在服务器上安装 Runner
- ⚠️ Runner 占用一定系统资源（约 100-200MB 内存）

### GitHub-hosted Runner + SSH（原方案）

**优点：**
- ✅ 无需在服务器上安装额外软件
- ✅ 不占用服务器资源
- ✅ 适合多服务器部署

**缺点：**
- ⚠️ 需要配置 SSH 密钥
- ⚠️ 需要服务器有公网 IP 和开放端口
- ⚠️ 无法访问内网资源
- ⚠️ GitHub Actions 有使用时长限制（免费版 2000 分钟/月）

---

## 🛠️ 进阶配置

### 1. 多个 Runner（高可用）

```bash
# 在同一服务器上运行多个 Runner（不同目录）
mkdir ~/actions-runner-1 ~/actions-runner-2
# 分别配置...
```

### 2. Runner 标签（区分不同环境）

```bash
# 配置时添加自定义标签
./config.sh --url https://github.com/CBDT-JWT/Home \
  --token YOUR_TOKEN \
  --labels production,web-server
```

工作流中使用：

```yaml
jobs:
  deploy:
    runs-on: [self-hosted, production]  # 只在带 production 标签的 Runner 上运行
```

### 3. 定期更新 Runner

```bash
cd ~/actions-runner
sudo ./svc.sh stop
./config.sh remove --token YOUR_REMOVE_TOKEN
# 下载最新版并重新配置
sudo ./svc.sh install
sudo ./svc.sh start
```

### 4. 监控 Runner 健康状态

```bash
# 创建监控脚本
cat > ~/check-runner.sh << 'EOF'
#!/bin/bash
if ! systemctl is-active --quiet actions.runner.*; then
  echo "Runner is down, restarting..."
  sudo systemctl start actions.runner.*
  # 可选：发送通知
fi
EOF

chmod +x ~/check-runner.sh

# 添加到 crontab（每 5 分钟检查一次）
crontab -e
# 添加：*/5 * * * * /home/your_user/check-runner.sh
```

---

## 🔐 安全建议

### 1. 使用专用用户运行 Runner

```bash
# 创建专用用户
sudo useradd -m -s /bin/bash github-runner
sudo su - github-runner

# 在该用户下安装 Runner
mkdir actions-runner && cd actions-runner
# ... 继续配置
```

### 2. 限制 Runner 权限

只授予必要的 sudo 权限：

```bash
sudo visudo
# 添加：
github-runner ALL=(ALL) NOPASSWD: /bin/systemctl restart homepage
github-runner ALL=(ALL) NOPASSWD: /bin/systemctl status homepage
# 不要给 ALL 权限
```

### 3. 定期审查 Runner 日志

```bash
# 查看最近的执行记录
cd ~/actions-runner/_diag
ls -lt | head -10
```

### 4. 使用 Runner Groups（组织级别）

如果是组织仓库，可以创建 Runner 组来管理访问权限。

---

## 📝 故障排查

### 问题 1: Runner 无法连接到 GitHub

**错误信息：**
```
Failed to connect to GitHub
```

**解决方法：**

```bash
# 检查网络连接
ping github.com
curl -I https://github.com

# 检查代理设置（如果服务器需要代理）
export https_proxy=http://proxy.example.com:8080
./config.sh --url ... --token ...
```

### 问题 2: Runner 启动后立即退出

**解决方法：**

```bash
# 查看错误日志
cd ~/actions-runner
cat _diag/Runner_*.log | tail -50

# 常见原因：token 过期，重新配置
./config.sh remove --token YOUR_REMOVE_TOKEN
./config.sh --url ... --token YOUR_NEW_TOKEN
```

### 问题 3: 工作流中找不到 Python/其他工具

**解决方法：**

```bash
# 确保 Runner 用户的 PATH 包含必要路径
sudo visudo -f /etc/sudoers.d/github-runner
# 添加：
Defaults:github-runner env_keep += "PATH"
Defaults:github-runner secure_path = /usr/local/bin:/usr/bin:/bin

# 或在工作流中显式指定路径
- run: /usr/bin/python3 -m venv venv
```

### 问题 4: Permission denied 错误

**解决方法：**

```bash
# 确保 Runner 用户对项目目录有权限
cd /path/to/your/homepage
sudo chown -R github-runner:github-runner .

# 或添加到相关组
sudo usermod -aG www-data github-runner
```

---

## 🎯 推荐方案选择

### 选择 Self-hosted Runner，如果：
- ✅ 服务器在内网或有网络限制
- ✅ 经常部署（每天多次）
- ✅ 需要访问本地资源
- ✅ 只有一个或少数几个服务器

### 选择 GitHub-hosted Runner + SSH，如果：
- ✅ 服务器有公网 IP 和开放端口
- ✅ 部署频率低（每周几次）
- ✅ 管理多个不同的服务器
- ✅ 不想在服务器上安装额外软件

---

## 📚 相关资源

- [GitHub Actions Self-hosted Runners 官方文档](https://docs.github.com/actions/hosting-your-own-runners)
- [Runner 安全指南](https://docs.github.com/actions/security-guides/security-hardening-for-github-actions#hardening-for-self-hosted-runners)
- [Runner 故障排查](https://docs.github.com/actions/hosting-your-own-runners/managing-self-hosted-runners/monitoring-and-troubleshooting-self-hosted-runners)

---

## ✅ 快速检查清单

安装前：
- [ ] 服务器已安装 Git、Python、systemd
- [ ] 创建或确认 Runner 运行用户
- [ ] 检查网络连接（可访问 github.com）

安装中：
- [ ] 从 GitHub 获取最新的 Runner token
- [ ] 下载并解压 Runner
- [ ] 运行 `./config.sh` 配置
- [ ] 安装为服务：`sudo ./svc.sh install`
- [ ] 启动服务：`sudo ./svc.sh start`

安装后：
- [ ] 在 GitHub Settings → Runners 看到绿色在线状态
- [ ] 配置 sudoers（重启服务权限）
- [ ] 推送代码或手动触发 workflow 测试
- [ ] 检查 Actions 日志确认部署成功
- [ ] 访问网站验证更新

---

**下一步：** 按照上述步骤在服务器上安装 Runner，然后推送代码测试！

有任何问题随时告诉我。 🚀
