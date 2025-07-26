---
inclusion: always
---

# Security Guidelines

## API Key Management

### Environment Variables
- Store all API keys in `.env` file
- Never hardcode API keys in source code
- Use different keys for development and production
- Rotate API keys regularly (every 3-6 months)

### Key Validation
```python
def validate_api_keys():
    required_keys = ["DOUBAO_API_KEY", "DASHSCOPE_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        raise ValueError(f"Missing required API keys: {missing_keys}")
```

### Access Control
- Limit API key permissions to minimum required
- Monitor API usage for anomalies
- Implement rate limiting to prevent abuse
- Set up alerts for unusual API activity

## Input Validation

### User Input Sanitization
- Validate all user inputs before processing
- Prevent injection attacks
- Limit input length and complexity
- Sanitize special characters

```python
def sanitize_user_input(user_input: str) -> str:
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', user_input)
    # Limit length
    return sanitized[:1000]
```

### API Response Validation
- Validate API response structure
- Handle malformed responses gracefully
- Never expose internal error details to users
- Log security-relevant events

## Network Security

### CORS Configuration
- Configure proper CORS headers
- Restrict origins in production
- Use HTTPS in production environment

```python
# Proper CORS setup
self.send_header('Access-Control-Allow-Origin', 'https://yourdomain.com')
self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
```

### Request Limits
- Implement rate limiting per IP/user
- Set maximum request size limits
- Timeout long-running requests
- Monitor for DDoS patterns

## Data Protection

### Sensitive Data Handling
- Never log API keys or sensitive data
- Encrypt sensitive data at rest
- Use secure communication channels
- Implement proper session management

### User Privacy
- Minimize data collection
- Implement data retention policies
- Provide user data deletion capabilities
- Comply with privacy regulations

## Error Handling

### Secure Error Messages
- Never expose internal system details
- Provide generic error messages to users
- Log detailed errors securely for debugging
- Implement proper exception handling

```python
try:
    result = await api_call()
except APIException as e:
    logger.error(f"API call failed: {e}", exc_info=True)
    return {"error": "Service temporarily unavailable"}
```

## Security Monitoring

### Logging
- Log all authentication attempts
- Monitor API usage patterns
- Track failed requests and errors
- Implement security event alerting

### Regular Security Reviews
- Review code for security vulnerabilities
- Update dependencies regularly
- Conduct security audits
- Test for common vulnerabilities (OWASP Top 10)