---
inclusion: fileMatch
fileMatchPattern: '*test*|*spec*|*mock*|*analytics*'
---

# Testing Guidelines for Mogine AI Chatbot

## Production Testing Strategy

### Service Health Testing
Test all production services individually:
```bash
# Knowledge Base API
curl "https://wingsai.cn/~temp/mogine_agent/api/search?q=test"
curl "https://wingsai.cn/~temp/mogine_agent/api/company_info"

# LLM APIs
curl -X POST "https://wingsai.cn/~temp/mogine_agent/api/llm/doubao" \
  -H "Content-Type: application/json" \
  -d '{"model":"doubao-1-5-thinking-vision-pro-250428","messages":[{"role":"user","content":"hello"}]}'

# Analytics API
curl "https://wingsai.cn/~temp/mogine_agent/api/analytics/health"
curl "https://wingsai.cn/~temp/mogine_agent/api/analytics/statistics?days=7"

# File Server
curl -I "https://wingsai.cn/~temp/mogine_agent/kb/assets/"
```

### Query Logging Testing
Use the test script to verify query logging:
```bash
python test_query_logger.py
```

This tests:
- SQLite database creation
- Query logging functionality
- Intent analysis integration
- Statistics generation
- Data retrieval

## Unit Testing

### Python Component Tests
```python
import pytest
import asyncio
from unittest.mock import Mock, patch
from chatbot.query_logger import QueryLogger
from chatbot.intent_analyzer import IntentAnalyzer

@pytest.mark.asyncio
async def test_intent_analyzer_with_logging():
    analyzer = IntentAnalyzer()
    
    with patch('chatbot.doubao_client.DoubaoClient.chat_completion') as mock_api:
        mock_api.return_value = {
            "choices": [{
                "message": {
                    "content": '{"summary": "test intent", "confidence": 0.9}'
                }
            }]
        }
        
        result = await analyzer.analyze_intent(
            "test query", 
            user_id="test_user", 
            session_id="test_session"
        )
        
        assert result.summary == "test intent"
        assert result.confidence == 0.9

def test_query_logger():
    logger = QueryLogger("test.db")
    
    query_id = logger.log_query(
        query_text="test query",
        user_id="test_user",
        intent_category="test_intent",
        intent_confidence=0.9
    )
    
    assert query_id is not None
    
    queries = logger.get_queries(limit=1)
    assert len(queries) == 1
    assert queries[0]['query_text'] == "test query"
```

### Analytics API Testing
```python
def test_analytics_endpoints():
    import requests
    
    base_url = "https://wingsai.cn/~temp/mogine_agent/api/analytics"
    
    # Test health endpoint
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    
    # Test statistics endpoint
    response = requests.get(f"{base_url}/statistics?days=7")
    assert response.status_code == 200
    data = response.json()
    assert "total_queries" in data
    assert "intent_distribution" in data
```

## Integration Testing

### End-to-End Chat Flow
```javascript
// Test complete chat interaction
describe('Chat Integration', () => {
    test('should complete full chat flow', async () => {
        // 1. Send user message
        const userMessage = "What is Mogine Technology?";
        
        // 2. Test knowledge base query
        const kbResponse = await fetch('/api/search?q=' + encodeURIComponent(userMessage));
        expect(kbResponse.ok).toBe(true);
        
        // 3. Test LLM API call
        const llmResponse = await fetch('/api/llm/doubao', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                model: 'doubao-1-5-thinking-vision-pro-250428',
                messages: [{ role: 'user', content: userMessage }]
            })
        });
        expect(llmResponse.ok).toBe(true);
        
        // 4. Verify query logging
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for logging
        const analyticsResponse = await fetch('/api/analytics/queries?limit=1');
        const analytics = await analyticsResponse.json();
        expect(analytics.queries.length).toBeGreaterThan(0);
    });
});
```

### PM2 Service Testing
```bash
#!/bin/bash
# Test PM2 service management

export PATH=/usr/local/node/bin:$PATH

echo "Testing PM2 services..."

# Check all services are running
pm2 status | grep -q "online" || exit 1

# Test service restart
pm2 restart mogine-web-server
sleep 5

# Verify service is back online
pm2 status | grep "mogine-web-server" | grep -q "online" || exit 1

echo "PM2 services test passed"
```

## Performance Testing

### Database Performance Testing
```python
import time
from chatbot.query_logger import QueryLogger

def test_database_performance():
    logger = QueryLogger()
    
    # Test bulk insert performance
    start_time = time.time()
    
    for i in range(100):
        logger.log_query(
            query_text=f"test query {i}",
            user_id=f"user_{i % 10}",
            intent_category="performance_test",
            intent_confidence=0.8
        )
    
    insert_time = time.time() - start_time
    print(f"100 inserts took {insert_time:.2f} seconds")
    
    # Test query performance
    start_time = time.time()
    queries = logger.get_queries(limit=50)
    query_time = time.time() - start_time
    print(f"Query took {query_time:.2f} seconds")
    
    assert len(queries) >= 50
    assert insert_time < 5.0  # Should complete in under 5 seconds
    assert query_time < 1.0   # Should complete in under 1 second
```

## Mock Data and Fixtures

### API Response Mocks
```python
MOCK_DOUBAO_RESPONSE = {
    "choices": [{
        "finish_reason": "stop",
        "message": {
            "content": "Hello! How can I help you today?",
            "role": "assistant"
        }
    }],
    "usage": {
        "completion_tokens": 10,
        "prompt_tokens": 5,
        "total_tokens": 15
    }
}

MOCK_KNOWLEDGE_BASE_RESPONSE = {
    "success": True,
    "query": "test query",
    "results": [{
        "title": "Test Document",
        "content": "Test content about Mogine Technology",
        "relevance_score": 0.95,
        "source": "knowledge_base"
    }],
    "total_found": 1
}
```

## Manual Testing Procedures

### User Acceptance Testing
1. **Chat Interface Testing**
   - Open `https://wingsai.cn/~temp/mogine_agent/real_llm_chat.html`
   - Test various query types
   - Verify streaming responses
   - Test quick action buttons
   - Verify contact modal functionality

2. **Analytics Dashboard Testing**
   - Open `https://wingsai.cn/~temp/mogine_agent/analytics_dashboard.html`
   - Verify data loading
   - Test time range filters
   - Check chart rendering
   - Test data refresh functionality

### Health Check Automation
```python
import requests

def test_service_health():
    endpoints = [
        "https://wingsai.cn/~temp/mogine_agent/api/company_info",
        "https://wingsai.cn/~temp/mogine_agent/api/analytics/health",
        "https://wingsai.cn/~temp/mogine_agent/real_llm_chat.html"
    ]
    
    for endpoint in endpoints:
        response = requests.get(endpoint, timeout=10)
        assert response.status_code == 200, f"Health check failed for {endpoint}"
        print(f"✅ {endpoint} - OK")

if __name__ == "__main__":
    test_service_health()
    print("All health checks passed!")
```

## Pre-deployment Testing
```bash
#!/bin/bash
# Pre-deployment test script

echo "Running pre-deployment tests..."

# 1. Unit tests
python -m pytest tests/ -v || exit 1

# 2. Query logger test
python test_query_logger.py || exit 1

# 3. Configuration validation
python -c "from dotenv import load_dotenv; load_dotenv(); import os; assert os.getenv('DOUBAO_API_KEY')" || exit 1

# 4. Syntax check
python -m py_compile *.py chatbot/*.py || exit 1

echo "All pre-deployment tests passed"
```