---
inclusion: fileMatch
fileMatchPattern: '*api*|*client*|*external*|*integration*|*proxy*'
---

# API Integration Guidelines

## Production API Architecture

### Web Server Proxy (`web_server.py`)
The production system uses a web server proxy to handle LLM API calls:
- **Port**: 8741
- **Endpoints**: `/api/llm/doubao`, `/api/llm/dashscope`
- **Features**: Error handling, JSON responses, CORS support

### Nginx Reverse Proxy
Nginx proxies external API calls to the web server:
```nginx
location ^~ /~temp/mogine_agent/api/llm/ {
    proxy_pass http://127.0.0.1:8741/api/llm/;
    proxy_buffering off;
    proxy_request_buffering off;
    # Streaming response configuration
}
```

## LLM API Integration

### Doubao API Configuration
```python
class DoubaoClient:
    def __init__(self):
        self.api_key = os.getenv("DOUBAO_API_KEY")
        self.base_url = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        self.model = os.getenv("DOUBAO_MODEL", "doubao-1-5-thinking-vision-pro-250428")
```

**Production Values**:
- API Key: `7bb276d0-0211-4498-ba54-1a58ca84bf8f`
- Base URL: `https://ark.cn-beijing.volces.com/api/v3`
- Model: `doubao-1-5-thinking-vision-pro-250428`

### DashScope API Configuration
```python
class DashScopeClient:
    def __init__(self):
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.app_id = os.getenv("DASHSCOPE_APP_ID")
        self.base_url = f"https://dashscope.aliyuncs.com/api/v1/apps/{self.app_id}/completion"
```

**Production Values**:
- API Key: `sk-634cc060c35b4c41800887b3a9d70bc2`
- App ID: `28bf0fe498ef4fcd8d94e610ce7ea9d5`

## Knowledge Base API

### Internal API Server (`simple_server.py`)
- **Port**: 8739
- **Endpoints**: `/api/search`, `/api/company_info`
- **Features**: ChromaDB integration, vector search

### API Usage
```javascript
// Frontend API call
const response = await fetch(`${SERVER_CONFIG.kbServer}/api/search?q=${query}&top_k=3`);
const data = await response.json();
```

## Analytics API

### Analytics Server (`analytics_server.py`)
- **Port**: 8742
- **Endpoints**: Statistics, queries, export, cleanup
- **Database**: SQLite for query logging

### Key Endpoints
- `GET /api/analytics/health` - Health check
- `GET /api/analytics/statistics?days=30` - Query statistics
- `GET /api/analytics/queries?limit=100` - Query records
- `POST /api/analytics/cleanup` - Data cleanup

## Error Handling

### JSON Error Responses
All APIs return consistent JSON error format:
```json
{
    "error": {
        "message": "API proxy error: Client error '401 Unauthorized'",
        "type": "proxy_error",
        "code": 500
    }
}
```

### Web Server Error Handling
```python
except Exception as e:
    self.send_response(500)
    self.send_header('Content-Type', 'application/json')
    self.end_headers()
    error_response = {
        "error": {
            "message": f"API proxy error: {str(e)}",
            "type": "proxy_error",
            "code": 500
        }
    }
    self.wfile.write(json.dumps(error_response).encode('utf-8'))
```

## Authentication

### API Key Management
- All API keys stored in `.env` file
- Server-side proxy handles authentication
- Frontend never exposes API keys
- Keys rotated regularly for security

### Request Headers
```python
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
    "User-Agent": "Mogine-AI-Chatbot/1.0"
}
```

## Streaming Responses

### LLM Streaming Implementation
```python
async def stream_llm_response(self, messages):
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", url, headers=headers, json=data) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    yield line + "\n\n"
```

### Frontend Streaming Consumption
```javascript
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    // Process streaming data
}
```

## Testing and Monitoring

### API Testing
```bash
# Test knowledge base API
curl "https://wingsai.cn/~temp/mogine_agent/api/search?q=test"

# Test LLM API
curl -X POST "https://wingsai.cn/~temp/mogine_agent/api/llm/doubao" \
  -H "Content-Type: application/json" \
  -d '{"model":"doubao-1-5-thinking-vision-pro-250428","messages":[{"role":"user","content":"hello"}]}'

# Test analytics API
curl "https://wingsai.cn/~temp/mogine_agent/api/analytics/health"
```

### Production Monitoring
- PM2 monitoring: `pm2 monit`
- Service logs: `pm2 logs [service-name]`
- Nginx logs: `/www/wwwlogs/mogine_*_error.log`
- Analytics dashboard for query metrics

## Security Considerations

### API Security
- HTTPS-only communication
- API keys never exposed to frontend
- Input validation and sanitization
- Rate limiting to prevent abuse

### Network Security
- Nginx SSL termination
- Internal service communication on localhost
- Firewall configuration for required ports
- Regular security updates