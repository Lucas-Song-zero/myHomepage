#!/usr/bin/env python3
"""数据库初始化脚本"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, Visitor, Message
from datetime import datetime

def init_database():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✓ 数据库表创建成功")
        
        # 添加示例数据（可选）
        if Visitor.query.count() == 0:
            sample_visitor = Visitor(
                ip_address='127.0.0.1',
                user_agent='Sample User Agent',
                page='/',
                visit_time=datetime.utcnow()
            )
            db.session.add(sample_visitor)
            print("✓ 添加示例访客记录")
        
        if Message.query.count() == 0:
            sample_message = Message(
                name='系统管理员',
                email='admin@weitao-jiang.cn',
                content='欢迎访问我的个人主页！',
                created_at=datetime.utcnow()
            )
            db.session.add(sample_message)
            print("✓ 添加示例留言")
        
        db.session.commit()
        print("✓ 数据库初始化完成")

if __name__ == '__main__':
    init_database()
