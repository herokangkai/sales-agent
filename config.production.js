// 生产环境配置文件 - 用于服务器部署
// 注意：在生产环境中，敏感信息不应该暴露在前端代码中

class ProductionConfig {
    constructor() {
        // 从URL参数或localStorage获取配置，或使用生产环境默认值
        this.config = {
            // 豆包API配置 - 生产环境通过代理访问
            doubao: {
                apiKey: 'handled-by-server', // 由服务器端处理
                baseUrl: '/~temp/mogine_agent/api/llm/doubao', // 通过Nginx代理
                model: this.getConfig('DOUBAO_MODEL', 'doubao-1-5-thinking-vision-pro-250428')
            },
            
            // 阿里云DashScope配置 - 生产环境通过代理访问
            dashscope: {
                apiKey: 'handled-by-server', // 由服务器端处理
                appId: 'handled-by-server', // 由服务器端处理
                baseUrl: '/~temp/mogine_agent/api/llm/dashscope' // 通过Nginx代理
            },
            
            // 服务器配置 - 生产环境使用相对路径
            servers: {
                kbServer: '/~temp/mogine_agent/api',
                fileServer: '/~temp/mogine_agent/kb/assets',
                mainServer: '/~temp/mogine_agent'
            },
            
            // 公司信息
            company: {
                website: this.getConfig('COMPANY_WEBSITE', 'https://www.shmofine.com'),
                name: this.getConfig('COMPANY_NAME', '上海摩泛科技有限公司'),
                nameEn: this.getConfig('COMPANY_NAME_EN', 'Shanghai MoFine Technology Co., Ltd.')
            }
        };
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
    
    // 设置配置（保存到localStorage）
    setConfig(key, value) {
        localStorage.setItem(key, value);
        // 重新初始化配置
        this.__init__();
    }
}

// 创建全局配置实例
window.AppConfig = new ProductionConfig();

// 导出配置（用于模块化）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProductionConfig;
}