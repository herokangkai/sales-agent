# 安全配置说明

## 🔐 API密钥管理

本项目使用环境变量来管理敏感信息，确保API密钥不会被意外提交到版本控制系统。

### 必需的API密钥

1. **豆包API密钥**
   - 环境变量：`DOUBAO_API_KEY`
   - 获取方式：从豆包开放平台获取
   - 格式：`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

2. **阿里云DashScope API密钥**
   - 环境变量：`DASHSCOPE_API_KEY`
   - 获取方式：从阿里云DashScope控制台获取
   - 格式：`sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

3. **DashScope应用ID**
   - 环境变量：`DASHSCOPE_APP_ID`
   - 获取方式：从阿里云DashScope应用管理页面获取
   - 格式：`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 配置步骤

1. **复制环境变量模板**
   ```bash
   cp .env.example .env
   ```

2. **编辑.env文件**
   ```bash
   # 替换为你的真实API密钥
   DOUBAO_API_KEY=your-actual-doubao-api-key
   DASHSCOPE_API_KEY=your-actual-dashscope-api-key
   DASHSCOPE_APP_ID=your-actual-app-id
   ```

3. **验证配置**
   ```bash
   python -c "from config import Config; print('配置验证:', Config.validate_config())"
   ```

### 安全最佳实践

1. **永远不要提交.env文件到Git**
   - .env文件已添加到.gitignore
   - 只提交.env.example作为模板

2. **定期轮换API密钥**
   - 建议每3-6个月更换一次API密钥
   - 在密钥泄露时立即更换

3. **限制API密钥权限**
   - 只授予必要的API权限
   - 设置适当的调用频率限制

4. **监控API使用情况**
   - 定期检查API调用日志
   - 设置异常使用告警

### 环境变量说明

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| DOUBAO_API_KEY | ✅ | - | 豆包API密钥 |
| DOUBAO_BASE_URL | ❌ | https://ark.cn-beijing.volces.com/api/v3 | 豆包API基础URL |
| DOUBAO_MODEL | ❌ | doubao-1-5-thinking-vision-pro-250428 | 豆包模型名称 |
| DASHSCOPE_API_KEY | ✅ | - | DashScope API密钥 |
| DASHSCOPE_APP_ID | ✅ | - | DashScope应用ID |
| KB_SERVER_PORT | ❌ | 8739 | 知识库服务器端口 |
| FILE_SERVER_PORT | ❌ | 8740 | 文件服务器端口 |
| MAIN_SERVER_PORT | ❌ | 8741 | 主服务器端口 |

### 故障排除

1. **API密钥无效**
   - 检查密钥格式是否正确
   - 确认密钥是否已激活
   - 验证密钥权限设置

2. **环境变量未加载**
   - 确认.env文件存在
   - 检查python-dotenv是否已安装
   - 验证load_dotenv()是否被调用

3. **CORS错误**
   - 检查服务器配置
   - 确认端口设置正确
   - 验证防火墙设置

### 联系支持

如果遇到安全相关问题，请联系：
- 技术支持：tech-support@example.com
- 安全团队：security@example.com

---

⚠️ **重要提醒**：请妥善保管你的API密钥，不要在公共场所或不安全的环境中使用。