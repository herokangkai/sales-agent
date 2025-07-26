# Mogine AI Chatbot - Sales Agent

An intelligent chatbot system built for Mogine Technology, featuring LLM-based intent recognition, multi-source data integration, and comprehensive analytics.

## 🚀 Features

- **Real-time LLM Integration**: Doubao API and Alibaba Cloud DashScope
- **Knowledge Base Search**: Vector-based semantic search with ChromaDB
- **Query Analytics**: SQLite-based logging with analytics dashboard
- **Streaming Responses**: Real-time streaming output for better UX
- **Multi-service Architecture**: 4 PM2-managed microservices
- **Production Ready**: Nginx SSL proxy, Google Analytics integration

## 🏗️ Architecture

### Services
- **Knowledge Base Server** - Vector search and company information
- **File Server** - Static file serving for media assets
- **Web Server** - Main application with LLM API proxy
- **Analytics Server** - Query logging and analytics API

### Technology Stack
- **Backend**: Python, FastAPI, ChromaDB, SQLite
- **Frontend**: HTML, JavaScript, CSS
- **Process Management**: PM2
- **Web Server**: Nginx with SSL
- **Analytics**: Google Analytics, Custom dashboard

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js and PM2 (for production)
- Nginx (for production)

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/herokangkai/sales-agent.git
   cd sales-agent
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. Start services:
   ```bash
   ./start_all_servers.sh
   ```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with the following variables:

```bash
# LLM API Configuration
DOUBAO_API_KEY=your-doubao-api-key
DOUBAO_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
DOUBAO_MODEL=doubao-1-5-thinking-vision-pro-250428

DASHSCOPE_API_KEY=your-dashscope-api-key
DASHSCOPE_APP_ID=your-app-id

# Server Configuration (Internal)
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
```

## 🚀 Production Deployment

### Automated Deployment
```bash
./deploy_server.sh
```

This script handles:
- Incremental file synchronization
- Server-side dependency installation
- PM2 service management
- Environment configuration

### Manual PM2 Management
```bash
# Set PATH for PM2
export PATH=/usr/local/node/bin:$PATH

# Check service status
pm2 status

# View logs
pm2 logs

# Restart services
pm2 restart all

# Monitor resources
pm2 monit
```

## 📊 Analytics

### Query Analytics Dashboard
Access the analytics dashboard at `/analytics_dashboard.html` to view:
- Query volume and trends
- Intent distribution analysis
- User engagement metrics
- Performance statistics

### Google Analytics
The system includes Google Analytics integration (GA4) for comprehensive user behavior tracking.

## 🧪 Testing

### Run Tests
```bash
# Unit tests
python -m pytest tests/ -v

# Query logging test
python test_query_logger.py

# Health checks
python -c "import requests; print(requests.get('http://localhost:8739/api/company_info').json())"
```

## 📁 Project Structure

```
mogine-agent/
├── chatbot/                 # Core chatbot modules
│   ├── intent_analyzer.py   # Intent analysis with LLM
│   ├── knowledge_base.py    # Vector search functionality
│   ├── query_logger.py      # SQLite query logging
│   └── ...
├── kb/                      # Knowledge base assets
├── www/                     # Nginx configuration
├── .kiro/                   # Kiro IDE configuration
├── real_llm_chat.html       # Main chat interface
├── analytics_dashboard.html # Analytics dashboard
├── analytics_server.py      # Analytics API server
└── requirements.txt         # Python dependencies
```

## 🔒 Security

- API keys stored in environment variables
- HTTPS-only communication in production
- Input validation and sanitization
- CORS policies implemented
- Query logging without sensitive data

## 📈 Monitoring

### PM2 Monitoring
- Process health monitoring
- Automatic restart on failures
- Resource usage tracking
- Log aggregation

### Analytics
- Real-time query analytics
- Performance metrics
- Error tracking
- User behavior analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is proprietary software developed for Mogine Technology.

## 🆘 Support

For support and questions, please contact the development team or create an issue in the repository.

---

**Mogine Technology** - High-fidelity AI Spatial Computing Digital Twin Expert