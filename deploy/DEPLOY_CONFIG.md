# 部署配置说明

## 📋 快速开始

### 1. 复制配置文件

```bash
cp deploy_config.example.sh deploy_config.sh
```

### 2. 编辑配置

```bash
vim deploy_config.sh
```

或使用其他编辑器打开 `deploy_config.sh`。

### 3. 填写配置项

```bash
# 服务器配置
SERVER_HOST="your-server.com"      # 服务器地址或域名
SERVER_USER="root"                 # SSH 用户名
SERVER_PORT="22"                   # SSH 端口

# 部署路径
DEPLOY_PATH="/root/homepage"       # 服务器上的部署目录

# SSH 密钥路径（可选）
SSH_KEY_PATH="/path/to/your/key"  # SSH 私钥路径，留空使用默认

# GitHub 仓库
GITHUB_REPO="https://github.com/username/repo.git"  # 仓库地址
```

### 4. 保存并使用

配置完成后，就可以使用部署脚本了：

```bash
# 从 GitHub 部署
./deploy_local.sh

# 快速部署当前目录
./deploy_quick.sh
```

---

## 🔒 安全说明

### 配置文件已加入 .gitignore

`deploy_config.sh` 已添加到 `.gitignore`，不会被提交到 Git 仓库，保证你的敏感信息安全。

### 文件说明

- ✅ `deploy_config.example.sh` - 配置模板（会提交到 Git）
- ❌ `deploy_config.sh` - 实际配置（不会提交，包含敏感信息）

---

## 📝 配置项详解

### SERVER_HOST
服务器地址，可以是：
- 域名：`www.example.com`
- IP 地址：`123.45.67.89`
- SSH 配置别名：`myserver`（如果在 `~/.ssh/config` 中配置）

### SERVER_USER
SSH 登录用户名，例如：
- `root`
- `ubuntu`
- `your_username`

### SERVER_PORT
SSH 端口，默认：`22`

如果服务器使用非标准端口，修改为对应端口号。

### DEPLOY_PATH
服务器上的部署目录，例如：
- `/root/homepage`
- `/home/ubuntu/homepage`
- `/var/www/homepage`

**注意：** 确保该用户对此目录有写权限。

### SSH_KEY_PATH（可选）
SSH 私钥文件路径，例如：
- `/Users/yourname/.ssh/id_ed25519`
- `/Users/yourname/.ssh/id_rsa`
- `~/.ssh/custom_key`

**留空**则使用 SSH 默认密钥和 `~/.ssh/config` 中的配置。

### GITHUB_REPO
GitHub 仓库地址，例如：
- HTTPS：`https://github.com/username/repo.git`
- SSH：`git@github.com:username/repo.git`

---

## 🎯 使用示例

### 示例 1：标准配置

```bash
SERVER_HOST="www.example.com"
SERVER_USER="ubuntu"
SERVER_PORT="22"
DEPLOY_PATH="/home/ubuntu/homepage"
SSH_KEY_PATH=""  # 使用 ~/.ssh/config 配置
GITHUB_REPO="https://github.com/username/repo.git"
```

### 示例 2：使用自定义 SSH 密钥

```bash
SERVER_HOST="123.45.67.89"
SERVER_USER="root"
SERVER_PORT="22"
DEPLOY_PATH="/root/homepage"
SSH_KEY_PATH="/Users/yourname/.ssh/deploy_key"
GITHUB_REPO="https://github.com/username/repo.git"
```

### 示例 3：使用 SSH 配置别名

```bash
SERVER_HOST="myserver"  # ~/.ssh/config 中的别名
SERVER_USER="deploy"
SERVER_PORT="22"
DEPLOY_PATH="/var/www/app"
SSH_KEY_PATH=""  # SSH 配置中已指定密钥
GITHUB_REPO="git@github.com:username/repo.git"
```

---

## 🔧 SSH 配置别名（推荐）

如果你经常部署，推荐在 `~/.ssh/config` 中配置别名：

```ssh-config
Host myserver
    HostName www.example.com
    User ubuntu
    Port 22
    IdentityFile ~/.ssh/id_ed25519
```

然后在 `deploy_config.sh` 中：

```bash
SERVER_HOST="myserver"
SERVER_USER="ubuntu"  # 虽然 config 中已配置，但脚本需要
SSH_KEY_PATH=""       # 留空，使用 config 中的配置
```

---

## ⚠️ 常见问题

### Q: 配置文件不存在

```
错误: 配置文件不存在: deploy_config.sh
请复制 deploy_config.example.sh 为 deploy_config.sh 并填写配置
```

**解决：**
```bash
cp deploy_config.example.sh deploy_config.sh
vim deploy_config.sh  # 编辑配置
```

### Q: SSH 连接失败

**检查：**
1. 服务器地址是否正确
2. SSH 端口是否正确
3. SSH 密钥是否有权限访问

**测试连接：**
```bash
ssh username@server-host
```

### Q: 权限被拒绝

**检查：**
1. SSH 密钥文件权限：`chmod 600 ~/.ssh/id_ed25519`
2. 用户是否有部署目录的写权限
3. 是否需要 sudo 权限

---

## 🔄 更新配置

修改配置后，无需重启，直接运行部署脚本即可：

```bash
./deploy_quick.sh
```

---

## 📚 相关文档

- [LOCAL_DEPLOY.md](LOCAL_DEPLOY.md) - 详细使用指南
- [deploy/README.md](deploy/README.md) - 服务器部署文档

---

## 💡 最佳实践

1. **使用 SSH 密钥认证**，不要使用密码
2. **在 `~/.ssh/config` 配置服务器别名**，简化配置
3. **定期备份配置文件**（但不要提交到公开仓库）
4. **使用不同的配置文件**管理多个环境（开发、测试、生产）

祝部署顺利！🚀
