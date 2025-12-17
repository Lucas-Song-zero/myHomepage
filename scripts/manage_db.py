#!/usr/bin/env python3
"""数据库管理工具"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, Visitor, Message
from datetime import datetime, timedelta

def show_stats():
    """显示统计信息"""
    with app.app_context():
        total_visitors = Visitor.query.count()
        total_messages = Message.query.count()
        
        print(f"\n📊 数据库统计")
        print(f"{'='*50}")
        print(f"总访客数: {total_visitors}")
        print(f"总留言数: {total_messages}")
        
        # 最近访客
        recent_visitors = Visitor.query.order_by(Visitor.visit_time.desc()).limit(5).all()
        print(f"\n最近5位访客:")
        for v in recent_visitors:
            print(f"  - {v.ip_address} | {v.visit_time.strftime('%Y-%m-%d %H:%M:%S')} | {v.page}")
        
        # 最近留言
        recent_messages = Message.query.order_by(Message.created_at.desc()).limit(5).all()
        print(f"\n最近5条留言:")
        for m in recent_messages:
            print(f"  - {m.name}: {m.content[:50]}...")

def clear_old_visitors(days=30):
    """清理旧访客记录"""
    with app.app_context():
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_visitors = Visitor.query.filter(Visitor.visit_time < cutoff_date).delete()
        db.session.commit()
        print(f"✓ 已清理 {old_visitors} 条 {days} 天前的访客记录")

def export_data():
    """导出数据"""
    with app.app_context():
        import json
        
        visitors = [v.to_dict() for v in Visitor.query.all()]
        messages = [m.to_dict() for m in Message.query.all()]
        
        data = {
            'visitors': visitors,
            'messages': messages,
            'exported_at': datetime.utcnow().isoformat()
        }
        
        filename = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 数据已导出到 {filename}")

def show_help():
    """显示帮助信息"""
    print("""
数据库管理工具

用法:
  python manage_db.py stats              显示统计信息
  python manage_db.py clear [days]       清理指定天数前的访客记录（默认30天）
  python manage_db.py export             导出数据到JSON文件
  python manage_db.py help               显示此帮助信息
    """)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'stats':
        show_stats()
    elif command == 'clear':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        clear_old_visitors(days)
    elif command == 'export':
        export_data()
    elif command == 'help':
        show_help()
    else:
        print(f"未知命令: {command}")
        show_help()
        sys.exit(1)
