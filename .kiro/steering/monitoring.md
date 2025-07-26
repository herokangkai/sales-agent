---
inclusion: fileMatch
fileMatchPattern: '*monitor*|*log*|*pm2*|*nginx*|*health*'
---

# Production Monitoring Guidelines

## Service Monitoring

### PM2 Process Management
- **Location**: `/usr/local/node/bin/pm2`
- **Services**: 4 managed processes
- **Auto-restart**: Enabled with memory limits (1GB)
- **Logging**: Individual log files per service

### PM2 Commands
```bash
# Set PATH for PM2
export PATH=/usr/local/node/bin:$PATH

# Check service status
pm2 status

# View logs
pm2 logs
pm2 logs mogine-web-server
pm2 logs mogine-kb-server

# Restart services
pm2 restart all
pm2 restart mogine-web-server

# Monitor resources
pm2 monit

# Save configuration
pm2 save
```

### Service Health Checks
- **Knowledge Base**: `GET /api/company_info`
- **Analytics**: `GET /api/analytics/health`
- **Web Server**: `GET /` (HTML response)
- **File Server**: `GET /kb/assets/` (directory listing)

## Log Management

### PM2 Logs
Located in PM2's log directory:
- `mogine-kb-server-error.log`
- `mogine-file-server-error.log`
- `mogine-web-server-error.log`
- `mogine-analytics-server-error.log`

### Nginx Logs
Located in `/www/wwwlogs/`:
- `mogine_*_access.log` - API access logs
- `mogine_*_error.log` - Error logs
- `wingsai.cn.access.log` - General access
- `wingsai.cn.error.log` - General errors

### Application Logs
- Query logging in SQLite database
- Error tracking in analytics system
- Performance metrics collection

## Performance Monitoring

### System Resources
Monitor via PM2 and system tools:
- CPU usage per service
- Memory consumption (1GB limit per service)
- Disk usage for database and logs
- Network I/O for API calls

### Application Metrics
- API response times (logged in analytics)
- Query processing times
- Error rates by endpoint
- User engagement metrics

### Database Performance
- SQLite query performance
- Database file size growth
- Index effectiveness
- Cleanup operation efficiency

## Alerting and Notifications

### Critical Alerts
- Service crashes or failures
- High error rates (>5%)
- Memory limit exceeded
- SSL certificate expiration
- API key expiration or quota exceeded

### Performance Alerts
- Slow response times (>5s)
- High CPU usage (>80%)
- Disk space low (<10%)
- Database size growth anomalies

### Monitoring Commands
```bash
# Check service status
pm2 status

# Monitor resource usage
pm2 monit

# Check recent errors
tail -f /www/wwwlogs/mogine_*_error.log

# Test API endpoints
curl https://wingsai.cn/~temp/mogine_agent/api/analytics/health
curl https://wingsai.cn/~temp/mogine_agent/api/company_info

# Check database size
ls -lh data/query_logs.db

# Check disk usage
df -h
```

## Analytics and Reporting

### Google Analytics
- **Tracking ID**: G-2495KLY5EC
- **Events**: Chat interactions, page views, user engagement
- **Real-time**: User activity monitoring
- **Reports**: Daily/weekly usage reports

### Query Analytics Dashboard
- **URL**: `/analytics_dashboard.html`
- **Metrics**: Query volume, intent distribution, trends
- **Refresh**: Auto-refresh every 5 minutes
- **Export**: JSON/CSV data export capability

### Key Metrics to Track
- Daily active users
- Query volume and trends
- Intent recognition accuracy
- Response times and performance
- Error rates and types
- User engagement patterns

## Maintenance Procedures

### Daily Checks
- Verify all services are running (`pm2 status`)
- Check error logs for issues
- Monitor resource usage
- Review analytics dashboard

### Weekly Maintenance
- Review performance trends
- Check log file sizes and rotate if needed
- Update analytics reports
- Review security logs

### Monthly Tasks
- Database cleanup (old query logs)
- Performance optimization review
- Security updates and patches
- Backup verification
- API usage and cost review

## Troubleshooting Guide

### Service Not Starting
1. Check PM2 status: `pm2 status`
2. View error logs: `pm2 logs [service-name]`
3. Check port availability: `lsof -i :[port]`
4. Verify environment variables in `.env`
5. Check Python dependencies

### API Errors
1. Test endpoint directly: `curl [endpoint]`
2. Check Nginx error logs
3. Verify API keys in `.env`
4. Check service logs for errors
5. Test internal service communication

### Performance Issues
1. Check resource usage: `pm2 monit`
2. Review slow query logs
3. Check database performance
4. Monitor network latency
5. Review API response times

### Database Issues
1. Check database file permissions
2. Verify SQLite integrity: `sqlite3 data/query_logs.db "PRAGMA integrity_check;"`
3. Review query performance
4. Check disk space availability
5. Consider database optimization

## Security Monitoring

### Access Monitoring
- Monitor Nginx access logs for unusual patterns
- Track failed authentication attempts
- Monitor API usage for abuse patterns
- Review CORS policy effectiveness

### Security Checks
- SSL certificate validity
- API key security and rotation
- Input validation effectiveness
- Error message information disclosure
- Log file access permissions

### Incident Response
1. Identify and isolate the issue
2. Check service status and logs
3. Implement immediate fixes
4. Document the incident
5. Review and improve monitoring

## Backup and Recovery

### Automated Backups
- Database: Daily backup of `data/query_logs.db`
- Configuration: Weekly backup of `.env` and nginx configs
- Code: Git repository with regular commits
- PM2 configuration: `pm2 save` after changes

### Recovery Procedures
1. Service recovery: `pm2 restart all`
2. Database recovery: Restore from backup
3. Configuration recovery: Restore config files
4. Full system recovery: Redeploy from Git

### Backup Verification
- Test backup integrity monthly
- Verify recovery procedures
- Document recovery time objectives
- Maintain offsite backup copies

## Monitoring Tools Integration

### External Monitoring
Consider integrating with:
- Uptime monitoring services
- Performance monitoring tools
- Log aggregation services
- Alert notification systems

### Custom Monitoring Scripts
Create scripts for:
- Automated health checks
- Performance data collection
- Alert generation
- Report generation

### Dashboard Integration
- Integrate with existing monitoring dashboards
- Create custom Grafana/Prometheus setup
- Use PM2 web interface for monitoring
- Implement custom monitoring endpoints