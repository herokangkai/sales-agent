---
inclusion: always
---

# Mogine AI Chatbot Project Overview

## Project Description
This is a production-ready intelligent chatbot system built for Mogine Technology, featuring:
- LLM-based intent recognition and decomposition
- Multi-source data integration (knowledge base + external agents)
- Real-time streaming response output
- Vector-based knowledge base using ChromaDB
- Web-based chat interface with analytics
- Query logging and analytics dashboard
- PM2 process management for production deployment

## Technology Stack
- **Backend**: Python, FastAPI, ChromaDB, SQLite
- **Frontend**: HTML, JavaScript, CSS
- **LLM APIs**: Doubao API, Alibaba Cloud DashScope
- **Knowledge Base**: Vector embeddings with semantic search
- **Process Management**: PM2
- **Web Server**: Nginx with SSL
- **Analytics**: Google Analytics (G-2495KLY5EC)
- **Database**: SQLite for query logging

## Production Architecture
- **4 PM2-managed services**:
  1. Knowledge Base Server (Port 8739)
  2. File Server (Port 8740) 
  3. Web Server (Port 8741)
  4. Analytics Server (Port 8742)
- **Nginx reverse proxy** with SSL termination
- **Production URL**: https://wingsai.cn/~temp/mogine_agent/

## Key Components
1. **Intent Analyzer** (`chatbot/intent_analyzer.py`) - Analyzes user intent with logging
2. **Knowledge Base** (`chatbot/knowledge_base.py`) - Vector storage and search
3. **External Agent** (`chatbot/external_agent.py`) - External service integration
4. **Response Integrator** (`chatbot/response_integrator.py`) - Response generation
5. **Query Logger** (`chatbot/query_logger.py`) - SQLite-based query logging
6. **Web Interface** (`real_llm_chat.html`) - User chat interface
7. **Analytics Dashboard** (`analytics_dashboard.html`) - Query analytics
8. **Analytics Server** (`analytics_server.py`) - Analytics API server

## Production Features
- **Real-time streaming responses** from LLM APIs
- **Query logging and analytics** for user behavior analysis
- **PM2 process management** with auto-restart and monitoring
- **Nginx SSL proxy** for secure HTTPS access
- **Google Analytics integration** for user tracking
- **Error handling** with JSON API responses
- **CORS configuration** for cross-origin requests

## Development Guidelines
- Use environment variables for API keys and sensitive data
- Follow async/await patterns for API calls
- Implement proper error handling and logging
- Maintain clean separation between components
- Use streaming responses for better UX
- Log all user queries for analytics
- Use PM2 for process management in production

## Security Considerations
- All API keys stored in `.env` file (not in version control)
- Nginx SSL termination with proper certificates
- CORS configuration for web interface security
- Input validation and sanitization
- Query logging without sensitive data exposure
- PM2 process isolation and monitoring