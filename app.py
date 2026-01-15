from flask import Flask, send_from_directory, jsonify, request
from database import db
from datetime import datetime
import os

app = Flask(__name__, static_folder='static', static_url_path='')

# 数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'homepage.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

# 初始化数据库
db.init_app(app)

# 数据模型
class Visitor(db.Model):
    """访客记录"""
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(255))
    visit_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    page = db.Column(db.String(255), default='/')
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'visit_time': self.visit_time.isoformat(),
            'page': self.page
        }

class Message(db.Model):
    """留言板"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }

class BlogPost(db.Model):
    """博客文章"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.String(500))  # 摘要
    content = db.Column(db.Text, nullable=False)  # Markdown内容
    thumbnail = db.Column(db.String(255))  # 缩略图
    author = db.Column(db.String(100), default='江玮陶')
    tags = db.Column(db.String(255))  # 标签，逗号分隔
    is_published = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self, include_content=False):
        data = {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'thumbnail': self.thumbnail,
            'author': self.author,
            'tags': self.tags.split(',') if self.tags else [],
            'is_published': self.is_published,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_content:
            data['content'] = self.content
        return data

# 创建数据库表
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """返回首页"""
    # 记录访客
    try:
        visitor = Visitor(
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            page='/'
        )
        db.session.add(visitor)
        db.session.commit()
    except Exception as e:
        print(f"记录访客失败: {e}")
    
    return send_from_directory('static', 'index.html')

@app.route('/health')
def health():
    """健康检查接口"""
    try:
        # 检查数据库连接
        db.session.execute(db.text('SELECT 1'))
        db_status = 'ok'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return {
        'status': 'ok',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    }, 200

@app.route('/api/visitors')
def get_visitors():
    """获取访客统计"""
    try:
        total = Visitor.query.count()
        recent = Visitor.query.order_by(Visitor.visit_time.desc()).limit(10).all()
        
        return jsonify({
            'total': total,
            'recent': [v.to_dict() for v in recent]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages', methods=['GET', 'POST'])
def messages():
    """留言板接口"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            message = Message(
                name=data.get('name'),
                email=data.get('email'),
                content=data.get('content')
            )
            db.session.add(message)
            db.session.commit()
            
            return jsonify(message.to_dict()), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    else:
        try:
            messages = Message.query.order_by(Message.created_at.desc()).all()
            return jsonify([m.to_dict() for m in messages])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# 注册五子棋蓝图（放在末尾避免循环导入）
from api_gomoku import gomoku_bp
app.register_blueprint(gomoku_bp)

# 注册管理员蓝图
from api_admin import admin_bp
app.register_blueprint(admin_bp)

# 注册博客蓝图
from api_blog import blog_bp
app.register_blueprint(blog_bp)

# 注册预约蓝图
from api_booking import booking_bp
app.register_blueprint(booking_bp)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 443))
    app.run(host='0.0.0.0', port=port, debug=True)
