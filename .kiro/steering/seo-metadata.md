---
inclusion: fileMatch
fileMatchPattern: '*.html|*seo*|*meta*|*sitemap*|*robots*'
---

# SEO和Meta Data指导原则

## HTML Meta Tags标准

### 基础Meta信息
- 始终包含charset、viewport、title、description
- title长度控制在50-60字符
- description长度控制在150-160字符
- 使用相关关键词但避免关键词堆砌

### Open Graph标签
- 为社交媒体分享优化
- 包含og:title, og:description, og:image, og:url
- 图片尺寸建议1200x630像素
- 确保图片路径正确且可访问

### Twitter Card标签
- 使用summary_large_image类型
- 包含twitter:title, twitter:description, twitter:image
- 与Open Graph保持一致

### 移动端优化
- 设置theme-color和msapplication-TileColor
- 配置apple-mobile-web-app相关标签
- 确保响应式设计

## 结构化数据

### JSON-LD格式
- 使用Schema.org标准
- 为应用程序使用SoftwareApplication类型
- 包含创建者、功能列表、价格信息

### 组织信息
- 包含公司名称、网址、logo
- 使用Organization类型
- 提供联系信息

## PWA支持

### Manifest文件
- 包含应用名称、图标、主题色
- 设置display为standalone
- 提供多种尺寸的图标
- 包含screenshots和shortcuts

### Service Worker
- 实现离线功能
- 缓存关键资源
- 提供推送通知支持

## 性能优化

### 资源预加载
- 使用dns-prefetch预解析域名
- 使用preconnect预连接关键资源
- 合理使用prefetch和preload

### 图片优化
- 使用WebP格式
- 提供多种尺寸
- 实现懒加载

### 缓存策略
- 设置合适的Cache-Control头
- 使用ETags进行缓存验证
- 实现资源版本控制

## 安全性

### Content Security Policy
- 限制资源加载来源
- 防止XSS攻击
- 允许必要的内联脚本和样式

### 其他安全头
- X-Content-Type-Options: nosniff
- X-Frame-Options: SAMEORIGIN
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin

## 可访问性

### ARIA标签
- 为动态内容添加aria-live
- 使用适当的role属性
- 提供alt文本和标题

### 键盘导航
- 确保所有交互元素可通过键盘访问
- 提供清晰的焦点指示器
- 实现合理的tab顺序

## 国际化

### 语言设置
- 在html标签中设置lang属性
- 使用hreflang标签指定语言版本
- 提供语言切换功能

### 字符编码
- 使用UTF-8编码
- 在HTTP头和HTML中声明编码
- 确保特殊字符正确显示