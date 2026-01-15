# GitHub Actions 自动化部署方案

本项目使用 GitHub Actions 实现自动化部署，每次推送到 `master` 分支时自动部署到服务器。

## 📋 目录

- [工作流程说明](#工作流程说明)
- [前置准备](#前置准备)
- [配置步骤](#配置步骤)
- [触发部署](#触发部署)
- [故障排查](#故障排查)

---

## 🔄 工作流程说明

GitHub Actions 工作流（`.github/workflows/deploy.yml`）会自动执行以下步骤：

1. **检出代码** - 从仓库拉取最新代码
2. **设置 Python 环境** - 准备 Python 3.11 环境
3. **安装文档构建工具** - 安装 mkdocs（如需要）
4. **准备 SSH 密钥** - 配置用于连接服务器的密钥
5. **连通性检查** - 测试 DNS 解析和服务器可达性
6. **构建文档** - 如果存在 mkdocs 配置则构建文档
7. **同步代码到服务器** - 使用 rsync 上传文件
8. **执行远程部署命令** - 安装依赖、初始化数据库、重启服务

---

## 🛠️ 前置准备

### 1. 服务器要求

- Linux 服务器（推荐 Ubuntu/CentOS）
- 已安装 Python 3.x
- 已安装并配置 systemd 服务（服务名：`homepage`）
- 服务器可通过公网 SSH 访问（GitHub Actions 托管运行器需要连接）

### 2. 本地要求

- Git 已安装
- SSH 密钥工具（ssh-keygen）
- GitHub CLI（可选，用于快速设置密钥）

---

## ⚙️ 配置步骤

### 步骤 1: 生成 SSH 密钥对

在本地终端执行：

```bash
# 生成新的 SSH 密钥对（用于 GitHub Actions）
ssh-keygen -t ed25519 -f ~/.ssh/homepage_deploy -C "github-actions-deploy" -N ""
```

这会生成两个文件：
- `~/.ssh/homepage_deploy` - 私钥（用于 GitHub Secrets）
- `~/.ssh/homepage_deploy.pub` - 公钥（上传到服务器）

### 步骤 2: 上传公钥到服务器

**方法 A：使用 ssh-copy-id**

```bash
# 替换为你的服务器用户和地址
ssh-copy-id -i ~/.ssh/homepage_deploy.pub your_user@your_server.com
```

**方法 B：手动添加**

```bash
# 读取公钥内容
cat ~/.ssh/homepage_deploy.pub

# 登录服务器
ssh your_user@your_server.com

# 添加公钥到 authorized_keys
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "你的公钥内容" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**测试连接：**

```bash
# 使用私钥测试 SSH 连接
ssh -i ~/.ssh/homepage_deploy your_user@your_server.com

# 如果使用非标准端口（例如 2222）
ssh -i ~/.ssh/homepage_deploy -p 2222 your_user@your_server.com
```

### 步骤 3: 配置 GitHub Secrets

在 GitHub 仓库页面：**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

添加以下 4 个必需密钥：

#### 必需密钥

| 密钥名称 | 说明 | 示例值 |
|---------|------|--------|
| `SSH_PRIVATE_KEY` | SSH 私钥完整内容 | `-----BEGIN OPENSSH PRIVATE KEY-----`<br/>`...`<br/>`-----END OPENSSH PRIVATE KEY-----` |
| `DEPLOY_HOST` | 服务器地址（域名或 IP） | `example.com` 或 `192.168.1.100` |
| `DEPLOY_USER` | SSH 登录用户名 | `deployuser` |
| `DEPLOY_PATH` | 服务器上的项目路径 | `/srv/homepage` 或 `/home/user/projects/homepage` |

#### 可选密钥

| 密钥名称 | 说明 | 示例值 |
|---------|------|--------|
| `DEPLOY_PORT` | SSH 端口（默认 22） | `2222` |

**使用 GitHub CLI 快速添加密钥：**

```bash
# 设置私钥
gh secret set SSH_PRIVATE_KEY < ~/.ssh/homepage_deploy

# 设置其他变量
gh secret set DEPLOY_HOST --body 'your_server.com'
gh secret set DEPLOY_USER --body 'your_username'
gh secret set DEPLOY_PATH --body '/path/to/project'

# 可选：如果使用非标准端口
gh secret set DEPLOY_PORT --body '2222'
```

### 步骤 4: 配置服务器权限

#### A. 确保项目目录存在

```bash
# 在服务器上创建部署目录
sudo mkdir -p /path/to/project
sudo chown your_username:your_username /path/to/project
```

#### B. 配置 systemd 服务重启权限

编辑 sudoers 文件（使用 `visudo`）：

```bash
sudo visudo
```

添加以下行（允许无密码重启服务）：

```bash
# 替换 your_username 为实际的部署用户名
your_username ALL=(ALL) NOPASSWD: /bin/systemctl restart homepage
your_username ALL=(ALL) NOPASSWD: /bin/systemctl status homepage
```

**测试权限：**

```bash
# 在服务器上测试（应该不需要输入密码）
sudo systemctl restart homepage
sudo systemctl status homepage
```

#### C. 准备项目依赖文件

确保服务器上已有：

```bash
# requirements.txt - Python 依赖
# scripts/init_db.py - 数据库初始化脚本
# scripts/init_gomoku_db.py - 五子棋数据库初始化
# scripts/init_admin_db.py - 管理员数据库初始化
```

---

## 🚀 触发部署

### 自动触发

推送代码到 `master` 分支时自动部署：

```bash
git add .
git commit -m "Update feature"
git push origin master
```

### 手动触发

在 GitHub 仓库页面：**Actions** → **Deploy to Server** → **Run workflow**

---

## 🔍 故障排查

### 问题 1: `Could not resolve hostname`

**错误信息：**
```
ssh: Could not resolve hostname ***: Name or service not known
```

**可能原因：**
1. `DEPLOY_HOST` 密钥值错误或为空
2. 服务器域名无法解析（内网地址）
3. 密钥中包含多余字符（如 `ssh://` 前缀或尾部斜杠）

**解决方法：**

```bash
# 1. 检查 DNS 解析
nslookup your_server.com
getent hosts your_server.com

# 2. 如果域名无法解析，改用 IP 地址
gh secret set DEPLOY_HOST --body '192.168.1.100'

# 3. 确保密钥值格式正确（仅域名或 IP，无协议前缀）
# ✅ 正确: example.com
# ✅ 正确: 192.168.1.100
# ❌ 错误: ssh://example.com
# ❌ 错误: example.com/
```

### 问题 2: `Permission denied (publickey)`

**错误信息：**
```
Permission denied (publickey,gssapi-keyex,gssapi-with-mic)
```

**可能原因：**
1. 公钥未正确添加到服务器
2. 私钥格式错误
3. `~/.ssh/authorized_keys` 权限不正确

**解决方法：**

```bash
# 在服务器上检查权限
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# 验证公钥是否存在
cat ~/.ssh/authorized_keys | grep github-actions-deploy

# 检查 SSH 服务配置
sudo grep "PubkeyAuthentication" /etc/ssh/sshd_config
# 应该是: PubkeyAuthentication yes

# 重启 SSH 服务（如果修改了配置）
sudo systemctl restart sshd
```

### 问题 3: `Connection timed out`

**错误信息：**
```
ssh: connect to host xxx port 22: Connection timed out
```

**可能原因：**
1. 服务器防火墙阻止 SSH 端口
2. 服务器在私有网络（GitHub Actions 无法访问）
3. 使用了非标准 SSH 端口但未配置

**解决方法：**

```bash
# 1. 检查防火墙规则（服务器上）
sudo ufw status
sudo firewall-cmd --list-all

# 2. 开放 SSH 端口
sudo ufw allow 22/tcp
# 或
sudo firewall-cmd --add-port=22/tcp --permanent
sudo firewall-cmd --reload

# 3. 如果使用非标准端口，添加 DEPLOY_PORT 密钥
gh secret set DEPLOY_PORT --body '2222'

# 4. 如果服务器在内网，考虑使用自托管 Runner
# 参考: https://docs.github.com/actions/hosting-your-own-runners
```

### 问题 4: `systemctl restart` 需要密码

**错误信息：**
```
sudo: a password is required
```

**解决方法：**

参考[步骤 4B](#b-配置-systemd-服务重启权限)配置 sudoers 文件。

### 问题 5: 查看 Actions 运行日志

在 GitHub 仓库页面：**Actions** → 选择最新的工作流运行 → 查看各步骤日志

关键步骤：
- **Pre-deploy connectivity check** - 查看 DNS 和连接测试结果
- **Rsync to server** - 查看文件同步日志
- **Run remote deploy commands** - 查看服务器端执行结果

---

## 📝 工作流文件说明

工作流配置文件位于：`.github/workflows/deploy.yml`

### 关键功能

1. **排除不必要的文件**
   ```yaml
   --exclude '.git' --exclude 'venv' --exclude '__pycache__'
   --exclude '*.pyc' --exclude 'homepage.db' --exclude 'static/uploads'
   ```

2. **条件执行**
   - mkdocs 构建：仅当存在 `mkdocs.yml` 时执行
   - 数据库初始化：仅当 `homepage.db` 不存在时执行

3. **安全措施**
   - SSH 密钥权限设置为 600
   - StrictHostKeyChecking 启用
   - 使用 ssh-keyscan 预加载主机密钥

### 自定义修改

如需修改工作流行为，编辑 `.github/workflows/deploy.yml`：

```yaml
# 修改 Python 版本
- uses: actions/setup-python@v4
  with:
    python-version: '3.11'  # 改为其他版本

# 修改触发分支
on:
  push:
    branches: [ 'master' ]  # 改为其他分支如 'main'
```

---

## 🔐 安全建议

1. **定期轮换 SSH 密钥**
   ```bash
   # 每 6-12 个月生成新密钥并更新
   ssh-keygen -t ed25519 -f ~/.ssh/homepage_deploy_new
   gh secret set SSH_PRIVATE_KEY < ~/.ssh/homepage_deploy_new
   ```

2. **最小权限原则**
   - 部署用户仅授予必要的 sudo 权限（仅 systemctl restart）
   - 不要使用 root 用户部署

3. **监控部署日志**
   - 定期检查 Actions 日志
   - 设置 GitHub Actions 通知（失败时邮件提醒）

4. **备份数据库**
   ```bash
   # 在服务器上设置定期备份
   crontab -e
   # 添加：每天凌晨 3 点备份数据库
   0 3 * * * /path/to/backup_script.sh
   ```

---

## 📚 参考资源

- [GitHub Actions 文档](https://docs.github.com/actions)
- [GitHub Secrets 管理](https://docs.github.com/actions/security-guides/encrypted-secrets)
- [SSH 密钥管理](https://www.ssh.com/academy/ssh/keygen)
- [自托管 Runner 设置](https://docs.github.com/actions/hosting-your-own-runners)

---

## ✅ 部署检查清单

部署前确认：

- [ ] 已生成 SSH 密钥对
- [ ] 公钥已添加到服务器 `~/.ssh/authorized_keys`
- [ ] 已在 GitHub 添加 4 个必需密钥（SSH_PRIVATE_KEY, DEPLOY_HOST, DEPLOY_USER, DEPLOY_PATH）
- [ ] 服务器上项目目录存在且权限正确
- [ ] sudoers 已配置无密码重启服务
- [ ] 本地测试 SSH 连接成功
- [ ] `requirements.txt` 和初始化脚本存在
- [ ] systemd 服务 `homepage` 已配置

部署后验证：

- [ ] Actions 工作流运行成功（绿色勾）
- [ ] 服务器上代码已更新
- [ ] 服务已重启：`systemctl status homepage`
- [ ] 网站可正常访问：http://www.weitao-jiang.cn
- [ ] 数据库和上传目录完好

---

**最后更新时间：** 2026-01-15

**有问题？** 查看 Actions 日志或联系维护人员。
