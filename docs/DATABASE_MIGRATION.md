# 数据库迁移指南

## 自动迁移系统

项目使用自动数据库迁移系统，在每次部署时自动检查并修复数据库结构。

### 工作原理

1. **检查脚本**: `scripts/check_and_migrate_db.py`
   - 定义了所有表的期望结构
   - 自动检测缺失的列
   - 自动添加缺失的列

2. **部署集成**:
   - `deploy.sh`: 本地部署脚本
   - `.github/workflows/deploy-self-hosted.yml`: GitHub Actions工作流
   - 两者都会在重启服务前运行数据库检查

### 如何添加新列

#### 步骤 1: 更新模型定义

在 `app.py` 中的数据库模型添加新字段：

```python
class BlogPost(db.Model):
    """博客文章"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))  # 新增字段
    # ... 其他字段
```

#### 步骤 2: 更新迁移脚本

在 `scripts/check_and_migrate_db.py` 的 `EXPECTED_SCHEMA` 中添加新列：

```python
EXPECTED_SCHEMA = {
    'blog_post': {
        'id': 'INTEGER',
        'title': 'VARCHAR(200)',
        'category': 'VARCHAR(100)',  # 新增列定义
        # ... 其他列
    }
}
```

#### 步骤 3: 更新 to_dict 方法

在模型的 `to_dict` 方法中包含新字段：

```python
def to_dict(self, include_content=False):
    data = {
        'id': self.id,
        'title': self.title,
        'category': self.category,  # 添加到返回数据
        # ... 其他字段
    }
    return data
```

#### 步骤 4: 更新 API

在 `api_blog.py` 中的创建和更新方法中处理新字段：

```python
# 创建时
post = BlogPost(
    title=data.get('title'),
    category=data.get('category'),  # 处理新字段
    # ... 其他字段
)

# 更新时
post.category = data.get('category', post.category)
```

#### 步骤 5: 部署

提交代码并推送到 master 分支：

```bash
git add .
git commit -m "Add category field to blog posts"
git push origin master
```

部署脚本会自动：
1. 拉取最新代码
2. 检查数据库结构
3. 添加缺失的 `category` 列
4. 重启服务

### 支持的数据类型

迁移脚本支持以下 SQLite 数据类型：

- `INTEGER` - 整数（默认值：0）
- `VARCHAR(n)` - 可变长字符串
- `TEXT` - 长文本
- `BOOLEAN` - 布尔值（默认值：1/True）
- `DATETIME` - 日期时间

### 手动运行迁移

如果需要手动检查或迁移数据库：

```bash
# 激活环境
conda activate web

# 运行迁移脚本
python scripts/check_and_migrate_db.py
```

### 输出示例

**首次添加列时：**
```
==================================================
数据库完整性检查
==================================================

检查表: blog_post
  发现 1 个缺失的列:
    ✓ 添加列: category (VARCHAR(100))

==================================================
✓ 数据库迁移完成
==================================================
```

**数据库完整时：**
```
==================================================
数据库完整性检查
==================================================

检查表: blog_post
  ✓ 所有列完整

==================================================
✓ 数据库结构完整，无需迁移
==================================================
```

## 注意事项

1. **只添加，不删除**: 迁移脚本只会添加缺失的列，不会删除多余的列
2. **默认值**: 新列会根据类型自动设置默认值
3. **无需停机**: 添加列操作不会影响正在运行的服务
4. **幂等性**: 可以多次运行迁移脚本，不会重复添加列

## 故障排除

### 问题：迁移失败

**原因**: 可能是数据类型不兼容或权限问题

**解决**: 
1. 检查错误日志
2. 手动运行迁移脚本查看详细错误
3. 如果需要，手动执行 SQL 命令

### 问题：列已存在但报错

**原因**: 可能是 SQLite 的列名大小写问题

**解决**: 
1. 检查 `EXPECTED_SCHEMA` 中的列名拼写
2. 确保与模型定义一致

## 扩展功能

如果需要添加其他表的迁移，只需在 `EXPECTED_SCHEMA` 中添加新表定义：

```python
EXPECTED_SCHEMA = {
    'blog_post': {
        # ... blog_post 的列定义
    },
    'new_table': {
        'id': 'INTEGER',
        'name': 'VARCHAR(100)',
        # ... 其他列
    }
}
```
