---
inclusion: always
---

# Coding Standards for Mogine AI Chatbot

## Python Code Standards

### Async/Await Patterns
- Always use `async def` for functions that make API calls
- Use `await` for all asynchronous operations
- Implement proper exception handling in async functions

```python
async def query_api(self, query: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            return response.json()
    except Exception as e:
        logger.error(f"API call failed: {e}")
        raise
```

### Error Handling
- Use specific exception types when possible
- Log errors with appropriate context
- Return meaningful error messages to users
- Never expose internal errors to the frontend

### Configuration Management
- Use `os.getenv()` for environment variables
- Provide sensible defaults where appropriate
- Validate required configuration on startup

```python
API_KEY = os.getenv("DOUBAO_API_KEY")
if not API_KEY:
    raise ValueError("DOUBAO_API_KEY environment variable is required")
```

## JavaScript Standards

### API Integration
- Use `fetch()` for HTTP requests
- Implement proper error handling for network calls
- Use async/await for cleaner code

```javascript
async function callAPI(endpoint, data) {
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`API call failed: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}
```

### Streaming Response Handling
- Use Server-Sent Events for streaming
- Implement proper cleanup for event listeners
- Handle connection errors gracefully

## File Organization
- Keep related functionality in the same module
- Use clear, descriptive file names
- Maintain consistent directory structure
- Separate configuration from business logic