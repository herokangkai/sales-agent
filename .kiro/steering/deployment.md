---
inclusion: fileMatch
fileMatchPattern: '*deploy*|*server*|*main*|docker*|requirements*'
---

# Deployment Guidelines

## Production Deployment Process

### Prerequisites
- Python 3.8+ installed with venv
- Node.js and PM2 installed at `/usr/local/node/bin/`
- Nginx configured with SSL certificates
- Environment variables configured in `.env`
- SSH access to production server (124.222.44.62)

### Production Architecture
- **Server**: 124.222.44.62
- **Directory**: /home/kk/public_temp/mogine_agent
- **Process Manager**: PM2
- **Web Server**: Nginx with SSL
- **Domain**: https://wingsai.cn/~temp/mogine_agent/

### Deployment Steps

1. **Automated Deployment**
   ```bash
   ./deploy_server.sh
   ```
   This script handles:
   - Incremental file sync (only modified files)
   - Server-side dependency installation
   - PM2 service management
   - Environment configuration

2. **Manual Service Management**
   ```bash
   # SSH to server
   ssh -i ~/.ssh/kkmacair.pem kk@124.222.44.62
   
   # PM2 commands (set PATH first)
   export PATH=/usr/local/node/bin:$PATH
   pm2 status
   pm2 restart all
   pm2 logs
   pm2 monit
   ```

### Service Architecture
- **mogine-kb-server** (Port 8739) - Knowledge base API
- **mogine-file-server** (Port 8740) - Static file serving
- **mogine-web-server** (Port 8741) - Main web server with LLM proxy
- **mogine-analytics-server** (Port 8742) - Query analytics API

### Nginx Configuration
Located at `/www/server/nginx/conf/vhost/temp_mogine_agent.conf`:
- SSL termination with proper certificates
- Reverse proxy to internal services on ports 8739-8742
- CORS headers for API access
- Static file serving optimization
- Error page handling

### Environment Variables
Required in `.env` file:
```bash
# LLM API Configuration
DOUBAO_API_KEY=7bb276d0-0211-4498-ba54-1a58ca84bf8f
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=doubao-1-5-thinking-vision-pro-250428

DASHSCOPE_API_KEY=sk-634cc060c35b4c41800887b3a9d70bc2
DASHSCOPE_APP_ID=28bf0fe498ef4fcd8d94e610ce7ea9d5
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/api/v1/apps/28bf0fe498ef4fcd8d94e610ce7ea9d5/completion

# Server Configuration
KB_SERVER_HOST=localhost
KB_SERVER_PORT=8739
FILE_SERVER_HOST=localhost
FILE_SERVER_PORT=8740
MAIN_SERVER_HOST=localhost
MAIN_SERVER_PORT=8741
ANALYTICS_SERVER_HOST=127.0.0.1
ANALYTICS_SERVER_PORT=8742

# Company Information
COMPANY_WEBSITE=https://www.shmofine.com
COMPANY_NAME=上海摩泛科技有限公司
COMPANY_NAME_EN=Shanghai MoFine Technology Co., Ltd.

# Development Settings
DEBUG=false
LOG_LEVEL=INFO
```

### Monitoring and Maintenance
- **PM2 Monitoring**: Process monitoring and auto-restart
- **Nginx Logs**: Access/error logs in `/www/wwwlogs/`
- **Service Logs**: View via `pm2 logs [service-name]`
- **Query Analytics**: Dashboard at `/analytics_dashboard.html`
- **Google Analytics**: Tracking ID G-2495KLY5EC

### API Endpoints
- **Knowledge Base**: `/api/search`, `/api/company_info`
- **LLM Proxy**: `/api/llm/doubao`, `/api/llm/dashscope`
- **Analytics**: `/api/analytics/health`, `/api/analytics/statistics`
- **File Server**: `/kb/assets/`

### Database Management
- **Query Logs**: SQLite database at `data/query_logs.db`
- **Analytics Data**: Automatic cleanup of old records
- **Export**: JSON/CSV export via analytics API

### Backup and Recovery
- **Database**: `data/query_logs.db` (SQLite)
- **Configuration**: `.env`, nginx configs
- **Code**: Git version control
- **PM2 State**: `pm2 save` for process list

### Troubleshooting
1. **Check PM2 Status**
   ```bash
   export PATH=/usr/local/node/bin:$PATH
   pm2 status
   ```

2. **View Service Logs**
   ```bash
   pm2 logs mogine-web-server
   pm2 logs mogine-kb-server
   ```

3. **Test API Endpoints**
   ```bash
   curl https://wingsai.cn/~temp/mogine_agent/api/company_info
   curl https://wingsai.cn/~temp/mogine_agent/api/analytics/health
   ```

4. **Check Nginx Logs**
   ```bash
   tail -f /www/wwwlogs/mogine_*_error.log
   ```

### Security Considerations
- SSL certificates properly configured
- API keys stored securely in `.env`
- CORS policies implemented
- Input validation and sanitization
- Query logging without sensitive data
- PM2 process isolation

### Performance Optimization
- Nginx caching for static files
- PM2 auto-restart on memory limits
- Streaming responses for LLM APIs
- Incremental deployment (only changed files)
- Query analytics for performance monitoring