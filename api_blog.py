from flask import Blueprint, jsonify, request, session
from functools import wraps
import os
from werkzeug.utils import secure_filename
from datetime import datetime

blog_bp = Blueprint('blog', __name__, url_prefix='/api/blog')

UPLOAD_FOLDER = 'static/uploads/blog'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'error': '未登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

# 在函数内部导入，避免循环导入
def get_db_models():
    from app import db, BlogPost
    return db, BlogPost

# 公开接口

@blog_bp.route('/posts', methods=['GET'])
def get_posts():
    """获取博客文章列表（分页）"""
    try:
        db, BlogPost = get_db_models()
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 只返回已发布的文章
        query = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'posts': [post.to_dict() for post in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@blog_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """获取单篇博客文章详情"""
    try:
        db, BlogPost = get_db_models()
        post = BlogPost.query.get_or_404(post_id)
        
        # 增加浏览量
        post.view_count += 1
        db.session.commit()
        
        return jsonify(post.to_dict(include_content=True))
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# 管理员接口

@blog_bp.route('/admin/posts', methods=['GET'])
@login_required
def admin_get_posts():
    """管理员获取所有文章（包括未发布的）"""
    try:
        db, BlogPost = get_db_models()
        posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
        return jsonify({
            'posts': [post.to_dict(include_content=True) for post in posts]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@blog_bp.route('/admin/posts', methods=['POST'])
@login_required
def create_post():
    """创建新博客文章"""
    try:
        db, BlogPost = get_db_models()
        data = request.get_json()
        
        post = BlogPost(
            title=data.get('title'),
            summary=data.get('summary'),
            content=data.get('content'),
            thumbnail=data.get('thumbnail'),
            author=data.get('author', '江玮陶'),
            tags=','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags', ''),
            is_published=data.get('is_published', True)
        )
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify(post.to_dict(include_content=True)), 201
    except Exception as e:
        db, _ = get_db_models()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@blog_bp.route('/admin/posts/<int:post_id>', methods=['PUT'])
@login_required
def update_post(post_id):
    """更新博客文章"""
    try:
        db, BlogPost = get_db_models()
        post = BlogPost.query.get_or_404(post_id)
        data = request.get_json()
        
        post.title = data.get('title', post.title)
        post.summary = data.get('summary', post.summary)
        post.content = data.get('content', post.content)
        post.thumbnail = data.get('thumbnail', post.thumbnail)
        post.author = data.get('author', post.author)
        post.tags = ','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags', post.tags)
        post.is_published = data.get('is_published', post.is_published)
        post.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(post.to_dict(include_content=True))
    except Exception as e:
        db, _ = get_db_models()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@blog_bp.route('/admin/posts/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    """删除博客文章"""
    try:
        db, BlogPost = get_db_models()
        post = BlogPost.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': '删除成功'})
    except Exception as e:
        db, _ = get_db_models()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@blog_bp.route('/admin/upload-image', methods=['POST'])
@login_required
def upload_image():
    """上传博客图片"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['image']
        
        if file.filename == '' or file.filename is None:
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            # 生成唯一文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # 返回相对URL
            url = f'/static/uploads/blog/{filename}'
            
            return jsonify({
                'url': url,
                'filename': filename
            })
        else:
            return jsonify({'error': '不支持的文件类型'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
