// 安全配置文件 - 隐藏内部端口信息
// 生产环境配置文件 - 用于服务器部署

class SecureConfig {
    constructor() {
        // 从环境变量或安全存储获取配置
        this.config = {
            // 豆包API配置 - 生产环境通过代理访问
            doubao: {
                apiKey: 'handled-by-server', // 由服务器端处理
                baseUrl: this.getSecureEndpoint('llm', 'doubao'),
                model: this.getConfig('DOUBAO_MODEL', 'doubao-1-5-thinking-vision-pro-250428')
            },
            
            // 阿里云DashScope配置 - 生产环境通过代理访问
            dashscope: {
                apiKey: 'handled-by-server', // 由服务器端处理
                appId: 'handled-by-server', // 由服务器端处理
                baseUrl: this.getSecureEndpoint('llm', 'dashscope')
            },
            
            // 服务器配置 - 使用相对路径，隐藏内部端口
            servers: {
                kbServer: this.getSecureEndpoint('api'),
                fileServer: this.getSecureEndpoint('kb', 'assets'),
                mainServer: this.getSecureEndpoint(),
                analyticsServer: this.getSecureEndpoint('api', 'analytics')
            },
            
            // 公司信息
            company: {
                website: this.getConfig('COMPANY_WEBSITE', 'https://www.shmofine.com'),
                name: this.getConfig('COMPANY_NAME', '上海摩泛科技有限公司'),
                nameEn: this.getConfig('COMPANY_NAME_EN', 'Shanghai MoFine Technology Co., Ltd.')
            }
        };
    }
    
    getSecureEndpoint(...paths) {
        // 生产环境使用相对路径，隐藏内部端口
        const basePath = window.location.pathname.includes('mogine_agent') 
            ? '/~temp/mogine_agent' 
            : '';
        
        if (paths.length === 0) {
            return basePath;
        }
        
        return basePath + '/' + paths.join('/');
    }
    
    getConfig(key, defaultValue) {
        // 优先级：URL参数 > localStorage > 默认值
        const urlParams = new URLSearchParams(window.location.search);
        const urlValue = urlParams.get(key);
        if (urlValue) return urlValue;
        
        const storageValue = localStorage.getItem(key);
        if (storageValue) return storageValue;
        
        return defaultValue;
    }
    
    // 获取豆包配置
    getDoubaoConfig() {
        return this.config.doubao;
    }
    
    // 获取DashScope配置
    getDashScopeConfig() {
        return this.config.dashscope;
    }
    
    // 获取服务器配置
    getServerConfig() {
        return this.config.servers;
    }
    
    // 获取公司信息
    getCompanyConfig() {
        return this.config.company;
    }
}

// 创建全局配置实例
window.AppConfig = new SecureConfig();

// 导出配置（用于模块化）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SecureConfig;
}