"""
管理员和项目管理 API
"""
from flask import Blueprint, jsonify, request, session
from database import db
from functools import wraps
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'pdf', 'md', 'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'error': '未登录'}), 401
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login', methods=['POST'])
def login():
    """管理员登录"""
    from models_admin import Admin
    
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': '用户名和密码不能为空'}), 400
        
        admin = Admin.query.filter_by(username=username).first()
        if not admin or not admin.check_password(password):
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 设置 session
        session['admin_id'] = admin.id
        session['admin_username'] = admin.username
        
        return jsonify({
            'message': '登录成功',
            'admin': admin.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/logout', methods=['POST'])
def logout():
    """管理员登出"""
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    return jsonify({'message': '登出成功'}), 200


@admin_bp.route('/check', methods=['GET'])
def check_login():
    """检查登录状态"""
    if 'admin_id' in session:
        return jsonify({
            'logged_in': True,
            'username': session.get('admin_username')
        }), 200
    return jsonify({'logged_in': False}), 200


@admin_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """获取管理员统计数据"""
    from models_admin import Project
    from datetime import datetime, timedelta
    
    try:
        # 导入Visitor模型
        from app import Visitor
        
        # 总访问量
        total_visitors = Visitor.query.count()
        
        # 首页访问量
        home_visitors = Visitor.query.filter_by(page='/').count()
        
        # 今日访问量（最近24小时）
        yesterday = datetime.utcnow() - timedelta(days=1)
        today_visitors = Visitor.query.filter(Visitor.visit_time >= yesterday).count()
        
        # 项目总数
        total_projects = Project.query.count()
        
        return jsonify({
            'total_visitors': total_visitors,
            'home_visitors': home_visitors,
            'today_visitors': today_visitors,
            'total_projects': total_projects
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密码"""
    from models_admin import Admin
    import logging
    
    try:
        data = request.get_json()
        if not data:
            logging.error('修改密码: 未收到JSON数据')
            return jsonify({'error': '请求数据格式错误'}), 400
            
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        logging.info(f'修改密码请求: 旧密码长度={len(old_password)}, 新密码长度={len(new_password)}')
        
        if not old_password or not new_password:
            return jsonify({'error': '旧密码和新密码不能为空'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': '新密码长度不能少于6位'}), 400
        
        # 获取当前管理员
        admin_id = session.get('admin_id')
        logging.info(f'当前管理员ID: {admin_id}')
        
        admin = Admin.query.get(admin_id)
        
        if not admin:
            logging.error(f'管理员不存在: admin_id={admin_id}')
            return jsonify({'error': '管理员不存在'}), 404
        
        # 验证旧密码
        if not admin.check_password(old_password):
            logging.warning(f'旧密码验证失败: admin_id={admin_id}')
            return jsonify({'error': '旧密码错误'}), 401
        
        # 设置新密码
        admin.set_password(new_password)
        db.session.commit()
        
        logging.info(f'密码修改成功: admin_id={admin_id}, username={admin.username}')
        return jsonify({'message': '密码修改成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f'修改密码异常: {str(e)}', exc_info=True)
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500


@admin_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """上传文件"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型'}), 400
        
        # 确保上传目录存在
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # 保存文件
        filename = secure_filename(file.filename)
        # 添加时间戳避免重名
        import time
        timestamp = str(int(time.time()))
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # 返回 /static/ 路径（兼容两种访问方式）
        relative_path = f"/static/uploads/{filename}"
        
        return jsonify({
            'message': '上传成功',
            'path': relative_path,
            'filename': filename
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/projects', methods=['GET'])
def get_projects():
    """获取所有项目（管理员可见所有，普通用户只看可见的）"""
    from models_admin import Project
    from flask import make_response
    
    try:
        is_admin = 'admin_id' in session
        
        if is_admin:
            projects = Project.query.order_by(Project.order_index.desc(), Project.created_at.desc()).all()
        else:
            projects = Project.query.filter_by(is_visible=True)\
                .order_by(Project.order_index.desc(), Project.created_at.desc()).all()
        
        response = make_response(jsonify({
            'projects': [p.to_dict() for p in projects]
        }), 200)
        
        # 添加缓存头（公开项目缓存60秒，管理员不缓存）
        if not is_admin:
            response.headers['Cache-Control'] = 'public, max-age=60'
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/projects', methods=['POST'])
@login_required
def create_project():
    """创建项目"""
    from models_admin import Project
    
    try:
        data = request.get_json()
        
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        thumbnail = data.get('thumbnail', '')
        content_type = data.get('content_type', '')
        content_path = data.get('content_path', '')
        
        if not title:
            return jsonify({'error': '项目标题不能为空'}), 400
        
        if content_type not in ['pdf', 'markdown', 'link']:
            return jsonify({'error': '内容类型必须是 pdf, markdown 或 link'}), 400
        
        if not content_path:
            return jsonify({'error': '内容路径/链接不能为空'}), 400
        
        project = Project(
            title=title,
            description=description,
            thumbnail=thumbnail,
            content_type=content_type,
            content_path=content_path,
            order_index=data.get('order_index', 0),
            is_visible=data.get('is_visible', True)
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'message': '项目创建成功',
            'project': project.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/projects/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    """更新项目"""
    from models_admin import Project
    
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        data = request.get_json()
        
        if 'title' in data:
            project.title = data['title'].strip()
        if 'description' in data:
            project.description = data['description'].strip()
        if 'thumbnail' in data:
            project.thumbnail = data['thumbnail']
        if 'content_type' in data:
            project.content_type = data['content_type']
        if 'content_path' in data:
            project.content_path = data['content_path']
        if 'order_index' in data:
            project.order_index = data['order_index']
        if 'is_visible' in data:
            project.is_visible = data['is_visible']
        
        db.session.commit()
        
        return jsonify({
            'message': '项目更新成功',
            'project': project.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """删除项目"""
    from models_admin import Project
    
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': '项目不存在'}), 404
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'message': '项目删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
