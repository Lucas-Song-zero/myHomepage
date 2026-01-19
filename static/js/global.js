// global.js — 统一 navbar/footer 注入 + 主题与导航行为
(function(){
    'use strict';

    // 统一导航栏HTML生成函数
    // type: 'full' (完整导航), 'simple' (简单返回按钮), 'viewer' (查看器样式)
    function createNavbar(options = {}) {
        const type = options.type || 'full';
        const title = options.title || '';
        const backUrl = options.backUrl || '/index.html';
        const backText = options.backText || '🏠 主页';
        
        if (type === 'full') {
            // 完整导航栏（用于主页、博客列表等）
            return `
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
    </nav>`;
        } else if (type === 'viewer') {
            // 查看器样式（用于博客查看器、Markdown查看器等）
            const secondaryBtn = options.secondaryUrl ? 
                `<a href="${options.secondaryUrl}" class="close-btn">${options.secondaryText || '← 返回'}</a>` : '';
            return `
    <div class="header">
        <a href="${backUrl}" class="close-btn">${backText}</a>
        ${secondaryBtn}
        <div class="title" id="pageTitle">${title}</div>
        <button class="theme-toggle" onclick="toggleTheme()" title="切换主题">
            <img id="theme-icon" src="/static/images/moon.png" alt="切换主题" class="theme-icon">
        </button>
    </div>`;
        } else {
            // simple - 简单的返回按钮
            return `
    <div class="header">
        <a href="${backUrl}" class="close-btn">${backText}</a>
        ${title ? `<div class="title">${title}</div>` : ''}
        <button class="theme-toggle" onclick="toggleTheme()" title="切换主题">
            <img id="theme-icon" src="/static/images/moon.png" alt="切换主题" class="theme-icon">
        </button>
    </div>`;
        }
    }

    // 自动注入导航栏（如果页面有data-navbar属性）
    function ensureNavbar() {
        try {
            const body = document.body;
            const navbarType = body.getAttribute('data-navbar');
            if (!navbarType) return; // 如果没有指定，不自动注入
            
            // 检查是否已经有导航栏
            if (document.querySelector('.navbar') || document.querySelector('.header')) {
                return; // 已有导航栏，不重复注入
            }
            
            const options = {
                type: navbarType,
                title: body.getAttribute('data-navbar-title') || '',
                backUrl: body.getAttribute('data-navbar-back-url') || '/index.html',
                backText: body.getAttribute('data-navbar-back-text') || '🏠 主页',
                secondaryUrl: body.getAttribute('data-navbar-secondary-url') || '',
                secondaryText: body.getAttribute('data-navbar-secondary-text') || ''
            };
            
            const navbarHTML = createNavbar(options);
            body.insertAdjacentHTML('afterbegin', navbarHTML);
        } catch (e) {
            console.warn('ensureNavbar error', e);
        }
    }

    // 统一 footer HTML（按用户要求使用 inline style）
    const FOOTER_HTML = `
    <footer style="display:flex;justify-content:center;padding:10px 16px;">
        <div style="display:inline-flex;align-items:center;gap:12px">
            <span>&copy; 2025 江玮陶. All rights reserved. | <a href="https://github.com/CBDT-JWT/Home" target="_blank" rel="noopener noreferrer" title="GitHub">GitHub</a> | <a href="mailto:wjiang0415@outlook.com" target="_blank" rel="noopener noreferrer" title="Mail">Mail</a> | <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" style="text-decoration:none;">京ICP备2025155858号-1</a>｜<a href="https://beian.mps.gov.cn/#/query/webSearch?code=11010802047067" rel="noreferrer" target="_blank" style="display:inline-flex;align-items:center;gap:8px;color:inherit;text-decoration:none;margin-left:8px">
                <img src="/static/images/police.png" alt="police" style="height:18px;display:inline-block">京公网安备11010802047067号 </a></span>
        </div>
    </footer>`;

    function ensureFooter() {
        try {
            // 如果已有 footer，替换之；否则插入到 body 末尾
            const existing = document.querySelectorAll('footer');
            if (existing && existing.length) {
                existing.forEach(el => el.outerHTML = FOOTER_HTML);
            } else {
                document.body.insertAdjacentHTML('beforeend', FOOTER_HTML);
            }
        } catch (e) {
            // fail silently
            console.warn('ensureFooter error', e);
        }
    }

    // 主题切换：暴露 toggleTheme 全局函数供页面 onclick 使用
    function toggleTheme() {
        const body = document.body;
        const themeIcon = document.getElementById('theme-icon');
        if (body.classList.contains('dark-mode')) {
            body.classList.remove('dark-mode');
            if (themeIcon) { themeIcon.src = '/static/images/moon.png'; themeIcon.alt = '切换到暗色模式'; }
            localStorage.setItem('theme', 'light');
        } else {
            body.classList.add('dark-mode');
            if (themeIcon) { themeIcon.src = '/static/images/sun.png'; themeIcon.alt = '切换到亮色模式'; }
            localStorage.setItem('theme', 'dark');
        }
    }

    function applySavedTheme() {
        try {
            const saved = localStorage.getItem('theme');
            const themeIcon = document.getElementById('theme-icon');
            if (saved === 'dark') {
                document.body.classList.add('dark-mode');
                if (themeIcon) { themeIcon.src = '/static/images/sun.png'; themeIcon.alt = '切换到亮色模式'; }
            } else {
                if (themeIcon) { themeIcon.src = '/static/images/moon.png'; themeIcon.alt = '切换到暗色模式'; }
            }
        } catch (e) { /* ignore */ }
    }

    // 导航栏滚动效果
    function setupNavbarScroll() {
        try {
            window.addEventListener('scroll', function() {
                const navbar = document.querySelector('.navbar') || document.querySelector('.header');
                if (!navbar) return;
                if (window.scrollY > 50) navbar.classList.add('scrolled'); else navbar.classList.remove('scrolled');
            });
        } catch (e) {}
    }

    // 移动端菜单切换
    function toggleMenu() {
        const menu = document.querySelector('.navbar-menu');
        if (menu) menu.classList.toggle('active');
    }

    // 绑定菜单项点击自动关闭（对于移动端）
    function setupMenuAutoClose() {
        try {
            document.querySelectorAll('.navbar-menu a').forEach(link => {
                link.addEventListener('click', function() {
                    const menu = document.querySelector('.navbar-menu');
                    if (menu) menu.classList.remove('active');
                });
            });
        } catch (e) {}
    }

    // 将需要的函数暴露到全局（onclick 可以直接使用）
    window.toggleTheme = toggleTheme;
    window.toggleMenu = toggleMenu;

    // 初始化
    document.addEventListener('DOMContentLoaded', function() {
        ensureNavbar(); // 首先注入导航栏（如果需要）
        applySavedTheme();
        ensureFooter();
        setupNavbarScroll();
        setupMenuAutoClose();
    });

    // 暴露创建导航栏的函数，供需要的页面手动调用
    window.createNavbar = createNavbar;

})();
/**
 * 全局JavaScript文件
 * 用于所有页面的通用功能
 */

// ========== 主题切换功能 ==========
function toggleTheme() {
    const body = document.body;
    const themeIcon = document.getElementById('theme-icon');
    
    if (body.classList.contains('dark-mode')) {
        body.classList.remove('dark-mode');
        themeIcon.src = '/static/images/moon.png';
        themeIcon.alt = '切换到暗色模式';
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.add('dark-mode');
        themeIcon.src = '/static/images/sun.png';
        themeIcon.alt = '切换到亮色模式';
        localStorage.setItem('theme', 'dark');
    }
}

// ========== 初始化主题 ==========
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const themeIcon = document.getElementById('theme-icon');
    
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        if (themeIcon) {
            themeIcon.src = '/static/images/sun.png';
            themeIcon.alt = '切换到亮色模式';
        }
    } else {
        if (themeIcon) {
            themeIcon.src = '/static/images/moon.png';
            themeIcon.alt = '切换到暗色模式';
        }
    }
}

// ========== 导航栏滚动效果 ==========
function initNavbarScroll() {
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }
    });
}

// ========== 移动端菜单切换 ==========
function toggleMenu() {
    const menu = document.querySelector('.navbar-menu');
    if (menu) {
        menu.classList.toggle('active');
    }
}

// ========== 渲染统一的Footer ==========
function renderFooter() {
    const footerHTML = `
        <footer style="display:flex;justify-content:center;padding:10px 16px;">
            <div style="display:inline-flex;align-items:center;gap:12px">
                <span>&copy; 2025 江玮陶. All rights reserved. | 
                    <a href="https://github.com/CBDT-JWT/Home" target="_blank" rel="noopener noreferrer" title="GitHub">GitHub</a> | 
                    <a href="mailto:wjiang0415@outlook.com" target="_blank" rel="noopener noreferrer" title="Mail">Mail</a> | 
                    <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" style="text-decoration:none;">京ICP备2025155858号-1</a>｜
                    <a href="https://beian.mps.gov.cn/#/query/webSearch?code=11010802047067" rel="noreferrer" target="_blank" style="display:inline-flex;align-items:center;gap:8px;color:inherit;text-decoration:none;margin-left:8px">
                        <img src="/static/images/police.png" alt="police" style="height:18px;display:inline-block">京公网安备11010802047067号
                    </a>
                </span>
            </div>
        </footer>
    `;
    
    // 查找footer元素并替换
    const existingFooter = document.querySelector('footer');
    if (existingFooter) {
        existingFooter.outerHTML = footerHTML;
    } else {
        // 如果没有footer，添加到body末尾
        document.body.insertAdjacentHTML('beforeend', footerHTML);
    }
}

// ========== 页面初始化 ==========
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    initNavbarScroll();
    renderFooter();
});

// ========== 如果DOM已经就绪，立即执行（针对缓存页面） ==========
if (document.readyState === 'interactive' || document.readyState === 'complete') {
    initTheme();
    initNavbarScroll();
    renderFooter();
}
