"""
421B 时间预约 API
提供查询和创建预约的接口
"""
from flask import Blueprint, request, jsonify
from database import db
from datetime import datetime, time

booking_bp = Blueprint('booking', __name__, url_prefix='/api/booking')

class Booking(db.Model):
    """预约记录"""
    __tablename__ = 'booking'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # 预约人姓名
    dept = db.Column(db.String(100))  # 部门
    date = db.Column(db.Date, nullable=False)  # 预约日期
    start_time = db.Column(db.Time, nullable=False)  # 开始时间
    end_time = db.Column(db.Time, nullable=False)  # 结束时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'dept': self.dept,
            'date': self.date.isoformat(),
            'start': self.start_time.strftime('%H:%M'),
            'end': self.end_time.strftime('%H:%M'),
            'created_at': self.created_at.isoformat()
        }

@booking_bp.route('/slots', methods=['GET'])
def get_slots():
    """
    获取某天的预约情况
    Query参数: date (YYYY-MM-DD格式)
    返回: [{start:'HH:MM', end:'HH:MM', name, dept}, ...]
    """
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({'error': '缺少date参数'}), 400
        
        # 解析日期
        try:
            query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': '日期格式错误，应为YYYY-MM-DD'}), 400
        
        # 查询该日期的所有预约
        bookings = Booking.query.filter_by(date=query_date).order_by(Booking.start_time).all()
        
        # 转换为前端期望的格式
        slots = []
        for booking in bookings:
            slots.append({
                'start': booking.start_time.strftime('%H:%M'),
                'end': booking.end_time.strftime('%H:%M'),
                'name': booking.name,
                'dept': booking.dept or ''
            })
        
        return jsonify(slots), 200
        
    except Exception as e:
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@booking_bp.route('/reserve', methods=['POST'])
def create_reservation():
    """
    创建预约
    请求体: {name, dept, date:'YYYY-MM-DD', start:'HH:MM', end:'HH:MM'}
    返回: {success:true} 或 {success:false, error:'...'}
    """
    try:
        data = request.get_json()
        
        # 验证必填字段
        name = data.get('name', '').strip()
        dept = data.get('dept', '').strip()
        date_str = data.get('date', '').strip()
        start_str = data.get('start', '').strip()
        end_str = data.get('end', '').strip()
        
        if not name:
            return jsonify({'success': False, 'error': '请填写姓名'}), 400
        if not date_str:
            return jsonify({'success': False, 'error': '请选择日期'}), 400
        if not start_str or not end_str:
            return jsonify({'success': False, 'error': '请选择时间范围'}), 400
        
        # 解析日期和时间
        try:
            booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_str, '%H:%M').time()
            end_time = datetime.strptime(end_str, '%H:%M').time()
        except ValueError as e:
            return jsonify({'success': False, 'error': f'日期或时间格式错误: {str(e)}'}), 400
        
        # 验证时间逻辑
        if start_time >= end_time:
            return jsonify({'success': False, 'error': '结束时间必须晚于开始时间'}), 400
        
        # 检查时间冲突（关键：确保没有重叠）
        # 两个时间段重叠的条件：start1 < end2 AND start2 < end1
        conflicting_bookings = Booking.query.filter(
            Booking.date == booking_date,
            Booking.start_time < end_time,
            Booking.end_time > start_time
        ).all()
        
        if conflicting_bookings:
            conflict_info = conflicting_bookings[0]
            return jsonify({
                'success': False,
                'error': f'时间冲突：{conflict_info.start_time.strftime("%H:%M")}-{conflict_info.end_time.strftime("%H:%M")} 已被 {conflict_info.name} 预约'
            }), 409
        
        # 创建预约
        booking = Booking(
            name=name,
            dept=dept,
            date=booking_date,
            start_time=start_time,
            end_time=end_time
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'booking': booking.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500

@booking_bp.route('/reservations', methods=['GET'])
def list_reservations():
    """
    获取所有预约列表（可选，用于管理）
    可选Query参数: start_date, end_date
    """
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        query = Booking.query
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            query = query.filter(Booking.date >= start_date)
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Booking.date <= end_date)
        
        bookings = query.order_by(Booking.date.desc(), Booking.start_time.desc()).all()
        
        return jsonify([b.to_dict() for b in bookings]), 200
        
    except Exception as e:
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@booking_bp.route('/reservations/<int:booking_id>', methods=['DELETE'])
def delete_reservation(booking_id):
    """
    删除预约（可选，用于管理）
    """
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': '预约不存在'}), 404
        
        db.session.delete(booking)
        db.session.commit()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'服务器错误: {str(e)}'}), 500
