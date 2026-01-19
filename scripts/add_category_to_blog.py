#!/usr/bin/env python3
"""
为博客表添加分类（category）字段
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db

def add_category_column():
    """添加category列到blog_post表"""
    with app.app_context():
        try:
            # 检查列是否已存在
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('blog_post')]
            
            if 'category' in columns:
                print("✓ category列已存在")
                return
            
            # 添加列
            print("正在添加category列...")
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE blog_post ADD COLUMN category VARCHAR(100)'))
                conn.commit()
            print("✓ category列添加成功")
            
        except Exception as e:
            print(f"✗ 错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    add_category_column()
