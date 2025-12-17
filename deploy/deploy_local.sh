#!/bin/bash
# 本地部署脚本 - 从 GitHub 拉取并部署到服务器

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 加载配置文件
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/deploy_config.sh"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}错误: 配置文件不存在: $CONFIG_FILE${NC}"
    echo -e "${YELLOW}请复制 deploy/deploy_config.example.sh 为 deploy_config.sh 并填写配置${NC}"
    exit 1
fi

source "$CONFIG_FILE"

# 验证必需的配置
if [ -z "$SERVER_HOST" ] || [ -z "$SERVER_USER" ] || [ -z "$DEPLOY_PATH" ] || [ -z "$GITHUB_REPO" ]; then
    echo -e "${RED}错误: 配置文件中缺少必需的配置项${NC}"
    exit 1
fi

# 构建 SSH 命令
SSH_CMD="ssh"
if [ -n "$SSH_KEY_PATH" ]; then
    SSH_CMD="ssh -i $SSH_KEY_PATH"
fi
SSH_TARGET="$SERVER_USER@$SERVER_HOST"

TEMP_DIR="/tmp/homepage-deploy-$$"

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}开始部署个人主页${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo -e "服务器: ${GREEN}$SERVER_HOST${NC}"
echo -e "用户: ${GREEN}$SERVER_USER${NC}"
echo -e "路径: ${GREEN}$DEPLOY_PATH${NC}"
echo ""

# 步骤 1: 清理临时目录
echo -e "${YELLOW}[1/6] 清理临时目录...${NC}"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# 步骤 2: 从 GitHub 克隆最新代码
echo -e "${YELLOW}[2/6] 从 GitHub 拉取最新代码...${NC}"
git clone "$GITHUB_REPO" "$TEMP_DIR"
cd "$TEMP_DIR"
echo -e "${GREEN}✓ 代码拉取成功${NC}"

# 步骤 3: 确保服务器部署目录存在
echo -e "${YELLOW}[3/6] 准备服务器环境...${NC}"
$SSH_CMD "$SSH_TARGET" "mkdir -p $DEPLOY_PATH"
echo -e "${GREEN}✓ 服务器目录已准备${NC}"

# 步骤 4: 同步代码到服务器
echo -e "${YELLOW}[4/6] 同步代码到服务器...${NC}"
if [ -n "$SSH_KEY_PATH" ]; then
    rsync -avz --progress -e "ssh -i $SSH_KEY_PATH" \
        --exclude '.git' \
        --exclude '.github' \
        --exclude 'venv' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.env' \
        --exclude '.DS_Store' \
        --exclude 'deploy' \
        --exclude 'deploy_config.sh' \
        ./ "$SSH_TARGET:$DEPLOY_PATH/"
else
    rsync -avz --progress \
        --exclude '.git' \
        --exclude '.github' \
        --exclude 'venv' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.env' \
        --exclude '.DS_Store' \
        --exclude 'deploy' \
        --exclude 'deploy_config.sh' \
        ./ "$SSH_TARGET:$DEPLOY_PATH/"
fi
echo -e "${GREEN}✓ 代码同步完成${NC}"

# 步骤 5: 在服务器上安装依赖并重启服务
echo -e "${YELLOW}[5/6] 安装依赖并重启服务...${NC}"
$SSH_CMD "$SSH_TARGET" << ENDSSH
cd $DEPLOY_PATH

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 初始化数据库
python scripts/init_db.py

# 重启服务
if systemctl is-active --quiet homepage; then
    echo "重启服务..."
    sudo systemctl restart homepage
    echo "✓ 服务已重启"
else
    echo "启动服务..."
    sudo systemctl start homepage
    echo "✓ 服务已启动"
fi
ENDSSH
echo -e "${GREEN}✓ 服务部署完成${NC}"

# 步骤 6: 清理临时文件
echo -e "${YELLOW}[6/6] 清理临时文件...${NC}"
cd /
rm -rf "$TEMP_DIR"
echo -e "${GREEN}✓ 清理完成${NC}"

# 检查服务状态
echo ""
echo -e "${YELLOW}检查服务状态...${NC}"
$SSH_CMD "$SSH_TARGET" "sudo systemctl status homepage --no-pager -l" || true

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "访问地址: http://$SERVER_HOST"
echo ""
echo "查看日志: $SSH_CMD $SSH_TARGET 'sudo journalctl -u homepage -f'"
echo ""
