---
inclusion: fileMatch
fileMatchPattern: '*analytics*|*query*|*log*|*dashboard*'
---

# Analytics and Query Logging Guidelines

## Overview
The Mogine AI Chatbot includes comprehensive analytics and query logging capabilities to track user behavior, analyze intent patterns, and optimize system performance.

## Architecture

### Query Logger (`chatbot/query_logger.py`)
- **Database**: SQLite (`data/query_logs.db`)
- **Tables**: 
  - `user_queries` - Main query records
  - `intent_analysis` - Detailed intent analysis results
  - `query_statistics` - Daily aggregated statistics

### Analytics Server (`analytics_server.py`)
- **Port**: 8742
- **API Endpoints**: RESTful API for analytics data
- **Features**: Statistics, export, cleanup

### Analytics Dashboard (`analytics_dashboard.html`)
- **URL**: `/analytics_dashboard.html`
- **Features**: Real-time visualization, trends, intent distribution

## Data Collection

### Automatic Logging
All user queries are automatically logged with:
- Query text and metadata
- User ID and session ID
- Intent analysis results
- Processing time and performance metrics
- Response sources (knowledge base, external agents)
- Timestamp and user agent information

### Intent Analysis Logging
Detailed intent analysis includes:
- Intent type and confidence score
- Extracted keywords and entities
- Sentiment analysis results
- Query complexity assessment

### Privacy Considerations
- No sensitive personal information stored
- Query text anonymized where possible
- Configurable data retention policies
- GDPR-compliant data handling

## Analytics API

### Health Check
```bash
GET /api/analytics/health
```

### Query Statistics
```bash
GET /api/analytics/statistics?days=30
```
Returns:
- Total queries count
- Average query length
- Intent distribution
- Query trends by date

### Query Records
```bash
GET /api/analytics/queries?limit=100&offset=0
```
Supports filtering by:
- User ID
- Intent category
- Date range
- Session ID

### Intent Distribution
```bash
GET /api/analytics/intent-distribution?days=7
```

### Data Export
```bash
GET /api/analytics/export?format=json
```
Supports JSON and CSV formats

### Data Cleanup
```bash
POST /api/analytics/cleanup
Content-Type: application/json
{"days": 90}
```

## Dashboard Features

### Real-time Statistics
- Total queries counter
- Average query length
- Most popular intents
- Daily query averages

### Trend Visualization
- Query volume over time
- Intent popularity trends
- User engagement patterns

### Query Analysis
- Recent query history
- Intent confidence scores
- Processing time metrics
- Response source analysis

## Google Analytics Integration

### Tracking ID
- **GA4 Property**: G-2495KLY5EC
- **Implementation**: gtag.js

### Custom Events
- `chat_message_sent` - User sends message
- `chat_completed` - Chat round completed
- `quick_button_click` - Quick question button used
- `contact_modal_open` - Contact modal opened
- `page_loaded` - Page initialization
- `dashboard_loaded` - Analytics dashboard viewed
- `data_refresh` - Manual data refresh

### Event Parameters
- `event_category` - Chat, UI, Analytics, etc.
- `event_label` - Specific action description
- `value` - Numeric value (message length, round number)

## Performance Monitoring

### Query Performance
- Processing time tracking
- API response times
- Error rate monitoring
- Success/failure ratios

### System Metrics
- Memory usage per service
- CPU utilization
- Database query performance
- Network latency

### Alerting
- High error rates
- Slow response times
- Service failures
- Unusual query patterns

## Data Analysis

### Intent Analysis
- Most common user intents
- Intent confidence trends
- Failed intent recognition patterns
- Query complexity distribution

### User Behavior
- Session duration analysis
- Query frequency patterns
- Feature usage statistics
- User engagement metrics

### System Optimization
- Identify slow queries
- Optimize knowledge base searches
- Improve intent recognition accuracy
- Enhance response quality

## Maintenance

### Database Management
- Regular cleanup of old records (90+ days)
- Database optimization and indexing
- Backup and recovery procedures
- Performance monitoring

### Analytics Server
- Log rotation and management
- API rate limiting
- Error handling and recovery
- Security updates

### Dashboard Updates
- Real-time data refresh (5-minute intervals)
- Chart and visualization updates
- Performance optimization
- User interface improvements

## Security and Privacy

### Data Protection
- Encrypted data transmission
- Secure API endpoints
- Access control and authentication
- Audit logging

### Compliance
- GDPR data handling
- User consent management
- Data retention policies
- Right to deletion

### Monitoring
- Unauthorized access detection
- Data breach prevention
- Security audit trails
- Compliance reporting

## Best Practices

### Query Logging
- Log all user interactions
- Include relevant context
- Avoid logging sensitive data
- Implement proper error handling

### Analytics Implementation
- Use consistent event naming
- Include meaningful parameters
- Track user journey stages
- Monitor conversion funnels

### Performance
- Optimize database queries
- Implement caching strategies
- Use efficient data structures
- Monitor resource usage

### Maintenance
- Regular data cleanup
- Performance monitoring
- Security updates
- Documentation updates