#!/usr/bin/env python3
"""
数据库完整性检查和自动迁移脚本
在部署时运行，自动检查并添加缺失的列
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import inspect

# 定义所有表的期望列结构
EXPECTED_SCHEMA = {
    'blog_post': {
        'id': 'INTEGER',
        'title': 'VARCHAR(200)',
        'category': 'VARCHAR(100)',
        'summary': 'VARCHAR(500)',
        'content': 'TEXT',
        'thumbnail': 'VARCHAR(255)',
        'author': 'VARCHAR(100)',
        'tags': 'VARCHAR(255)',
        'is_published': 'BOOLEAN',
        'view_count': 'INTEGER',
        'created_at': 'DATETIME',
        'updated_at': 'DATETIME',
    }
}

def check_and_migrate():
    """检查数据库完整性并进行必要的迁移"""
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print("=" * 50)
            print("数据库完整性检查")
            print("=" * 50)
            
            migration_needed = False
            
            for table_name, expected_columns in EXPECTED_SCHEMA.items():
                if table_name not in tables:
                    print(f"\n⚠️  表 '{table_name}' 不存在，跳过检查")
                    continue
                
                print(f"\n检查表: {table_name}")
                
                # 获取现有列
                existing_columns = {col['name']: col for col in inspector.get_columns(table_name)}
                
                # 检查缺失的列
                missing_columns = []
                for col_name, col_type in expected_columns.items():
                    if col_name not in existing_columns:
                        missing_columns.append((col_name, col_type))
                
                if missing_columns:
                    migration_needed = True
                    print(f"  发现 {len(missing_columns)} 个缺失的列:")
                    
                    # 添加缺失的列
                    with db.engine.connect() as conn:
                        for col_name, col_type in missing_columns:
                            try:
                                # 构建 ALTER TABLE 语句
                                # 为某些类型添加默认值
                                default_clause = ""
                                if col_type == 'INTEGER':
                                    default_clause = " DEFAULT 0"
                                elif col_type == 'BOOLEAN':
                                    default_clause = " DEFAULT 1"
                                
                                sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}{default_clause}"
                                conn.execute(db.text(sql))
                                conn.commit()
                                print(f"    ✓ 添加列: {col_name} ({col_type})")
                            except Exception as e:
                                print(f"    ✗ 添加列 {col_name} 失败: {e}")
                else:
                    print(f"  ✓ 所有列完整")
            
            print("\n" + "=" * 50)
            if migration_needed:
                print("✓ 数据库迁移完成")
            else:
                print("✓ 数据库结构完整，无需迁移")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            print(f"\n✗ 检查失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = check_and_migrate()
    sys.exit(0 if success else 1)
