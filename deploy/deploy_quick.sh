#!/bin/bash
# 快速部署脚本 - 直接从当前目录部署

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
if [ -z "$SERVER_HOST" ] || [ -z "$SERVER_USER" ] || [ -z "$DEPLOY_PATH" ]; then
    echo -e "${RED}错误: 配置文件中缺少必需的配置项${NC}"
    exit 1
fi

# 构建 SSH 命令
SSH_CMD="ssh"
if [ -n "$SSH_KEY_PATH" ]; then
    SSH_CMD="ssh -i $SSH_KEY_PATH"
fi
SSH_TARGET="$SERVER_USER@$SERVER_HOST"

echo -e "${YELLOW}快速部署到 $SERVER_HOST${NC}"
echo ""

# 同步代码
echo -e "${YELLOW}同步代码...${NC}"
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
        --exclude 'deploy_*.sh' \
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
        --exclude 'deploy_*.sh' \
        --exclude 'deploy_config.sh' \
        ./ "$SSH_TARGET:$DEPLOY_PATH/"
fi

# 部署
echo ""
echo -e "${YELLOW}部署服务...${NC}"
$SSH_CMD "$SSH_TARGET" << ENDSSH
cd $DEPLOY_PATH
source venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
sudo systemctl restart homepage
echo "✓ 服务已重启"
ENDSSH

echo ""
echo -e "${GREEN}部署完成！${NC}"
echo "访问: http://$SERVER_HOST"
