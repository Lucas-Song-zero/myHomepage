# 统一导航栏使用指南

## 概述
所有页面的导航栏样式已统一到 `/static/css/global.css` 中，导航栏HTML模板可通过 `/static/js/global.js` 中的函数生成。

## 导航栏类型

### 1. 完整导航栏 (Full Navbar)
适用于：主页、博客列表、项目列表等主要页面

```html
<nav class="navbar">
    <a href="/index.html" class="navbar-brand"></a>
    <ul class="navbar-menu">
        <li><a href="/index.html" title="主页">
            <img src="/static/images/home.png" alt="主页" class="nav-icon">
        </a></li>
        <li><a href="/static/notes/index.html" title="笔记">
            <img src="/static/images/note.png" alt="笔记" class="nav-icon">
        </a></li>
        <li><a href="/blog.html" title="博客">
            <img src="/static/images/blog.png" alt="博客" class="nav-icon">
        </a></li>
        <li><a href="/gomoku.html" title="五子棋">
            <img src="/static/images/game.png" alt="五子棋" class="nav-icon">
        </a></li>
        <li><a href="#links" title="友链">
            <img src="/static/images/friend.png" alt="友链" class="nav-icon">
        </a></li>
        <li><a href="/admin_login.html" title="管理">
            <img src="/static/images/admin.png" alt="管理" class="nav-icon">
        </a></li>
        <li><button class="theme-toggle" onclick="toggleTheme()" title="切换主题">
            <img id="theme-icon" src="/static/images/moon.png" alt="切换主题" class="theme-icon">
        </button></li>
    </ul>
    <div class="navbar-toggle" onclick="toggleMenu()">
        <span></span>
        <span></span>
        <span></span>
    </div>
</nav>
```

### 2. 查看器导航栏 (Viewer Header)
适用于：博客查看器、Markdown查看器、PDF查看器等

```html
<div class="header">
    <a href="/index.html" class="close-btn">🏠 主页</a>
    <a href="/blog.html" class="close-btn">← 返回博客</a>
    <div class="title" id="pageTitle">文章标题</div>
    <button class="theme-toggle" onclick="toggleTheme()" title="切换主题">
        <img id="theme-icon" src="/static/images/moon.png" alt="切换主题" class="theme-icon">
    </button>
</div>
```

### 3. 简单导航栏 (Simple Header)
适用于：管理页面、登录页面等

```html
<div class="header">
    <a href="/index.html" class="close-btn">🏠 主页</a>
    <div class="title">页面标题</div>
    <button class="theme-toggle" onclick="toggleTheme()" title="切换主题">
        <img id="theme-icon" src="/static/images/moon.png" alt="切换主题" class="theme-icon">
    </button>
</div>
```

## JavaScript函数生成（可选）

如果需要动态生成导航栏HTML，可以使用 `global.js` 中的 `createNavbar()` 函数：

```javascript
// 完整导航栏
const fullNavbar = window.createNavbar({ type: 'full' });

// 查看器导航栏
const viewerNavbar = window.createNavbar({
    type: 'viewer',
    title: '文章标题',
    backUrl: '/index.html',
    backText: '🏠 主页',
    secondaryUrl: '/blog.html',
    secondaryText: '← 返回博客'
});

// 简单导航栏
const simpleNavbar = window.createNavbar({
    type: 'simple',
    title: '页面标题',
    backUrl: '/index.html',
    backText: '← 返回'
});

// 将生成的HTML插入页面
document.body.insertAdjacentHTML('afterbegin', viewerNavbar);
```

## 必需的引用

每个页面都需要引入：

```html
<head>
    <!-- 全局样式 -->
    <link rel="stylesheet" href="/static/css/global.css">
</head>
<body>
    <!-- 页面内容 -->
    
    <!-- 全局JavaScript（放在body结束前） -->
    <script src="/static/js/global.js"></script>
</body>
```

## 自动功能

引入 `global.js` 后，以下功能自动启用：

1. **主题切换** - `toggleTheme()` 函数可直接在 onclick 中使用
2. **移动端菜单** - `toggleMenu()` 函数用于汉堡菜单
3. **滚动效果** - 导航栏在滚动时自动添加 `.scrolled` 类
4. **主题持久化** - 用户选择的主题自动保存到 localStorage
5. **Footer注入** - 统一的footer自动添加到页面底部

## 样式自定义

如果需要特殊样式，可以在页面的 `<style>` 标签中覆盖：

```css
/* 页面特定的导航栏调整 */
.header {
    height: 70px; /* 覆盖默认的60px */
}

.navbar-brand {
    font-size: 2rem; /* 覆盖默认的1.5rem */
}
```

## 注意事项

1. 导航栏的图标ID统一使用 `theme-icon`（不是 `themeIcon`）
2. 移动端响应式样式已内置在 `global.css` 中
3. 暗色模式的图标filter效果已统一处理
4. 所有导航栏都使用CSS变量，支持主题切换
