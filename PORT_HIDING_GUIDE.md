# 端口隐藏最佳实践指南

## 当前实现状态 ✅

你的项目已经成功隐藏了所有内部端口：

### 用户看到的 URL
```
https://wingsai.cn/~temp/mogine_agent/                    # 主应用
https://wingsai.cn/~temp/mogine_agent/analytics_dashboard.html  # 分析面板
https://wingsai.cn/~temp/mogine_agent/api/analytics/statistics  # API接口
```

### 实际内部端口（用户看不到）
```
127.0.0.1:8739  # 知识库服务
127.0.0.1:8740  # 文件服务  
127.0.0.1:8741  # Web服务
127.0.0.1:8742  # 分析服务
```

## 隐藏端口的方法

### 1. Nginx 反向代理（推荐 ⭐）
- **优点**: 完全隐藏端口，支持SSL，负载均衡，缓存
- **缺点**: 需要配置Nginx
- **适用**: 生产环境

### 2. 域名子路径映射
```nginx
location /api/analytics/ {
    proxy_pass http://127.0.0.1:8742/api/analytics/;
}
```

### 3. 子域名映射
```nginx
server {
    server_name analytics.yourdomain.com;
    location / {
        proxy_pass http://127.0.0.1:8742/;
    }
}
```

### 4. API Gateway
- 使用 Kong, Traefik 等API网关
- 统一入口，路由到不同服务

## 安全加固建议

### 1. 防火墙配置
```bash
# 只开放必要端口
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 22/tcp    # SSH

# 禁止直接访问内部端口
sudo ufw deny 8739:8742/tcp
```

### 2. 绑定本地地址
确保服务只监听本地地址：
```python
# 好的做法
app.run(host='127.0.0.1', port=8739)

# 避免这样做
app.run(host='0.0.0.0', port=8739)  # 暴露给外网
```

### 3. Nginx 访问控制
```nginx
# 限制特定API的访问
location /~temp/mogine_agent/api/analytics/ {
    # 只允许特定IP访问
    allow 192.168.1.0/24;
    deny all;
    
    proxy_pass http://127.0.0.1:8742/api/analytics/;
}
```

## 监控和维护

### 1. 端口监控
```bash
# 检查端口监听状态
netstat -tlnp | grep :8739
ss -tlnp | grep :8740

# 确保只监听本地地址
lsof -i :8741
```

### 2. Nginx 日志监控
```bash
# 监控访问日志
tail -f /www/wwwlogs/mogine_*_access.log

# 监控错误日志
tail -f /www/wwwlogs/mogine_*_error.log
```

### 3. 自动化检查脚本
```bash
#!/bin/bash
# 检查端口隐藏状态
echo "检查端口隐藏状态..."

# 检查外网是否能直接访问内部端口
for port in 8739 8740 8741 8742; do
    if curl -s --connect-timeout 5 "http://外网IP:$port" > /dev/null; then
        echo "⚠️  端口 $port 可能暴露给外网"
    else
        echo "✅ 端口 $port 已正确隐藏"
    fi
done
```

## 故障排除

### 1. 代理不工作
```bash
# 检查 Nginx 配置
nginx -t

# 重载配置
nginx -s reload

# 检查上游服务状态
curl http://127.0.0.1:8741/health
```

### 2. 端口冲突
```bash
# 查找占用端口的进程
lsof -i :8741
netstat -tlnp | grep :8741

# 杀死占用进程
kill -9 <PID>
```

### 3. SSL 证书问题
```bash
# 检查证书有效性
openssl x509 -in /path/to/cert.crt -text -noout

# 测试 SSL 连接
openssl s_client -connect wingsai.cn:443
```

## 最佳实践总结

1. ✅ **使用反向代理**: Nginx/Apache 隐藏内部端口
2. ✅ **本地绑定**: 服务只监听 127.0.0.1
3. ✅ **防火墙保护**: 只开放必要端口
4. ✅ **SSL 加密**: 使用 HTTPS 保护数据传输
5. ✅ **访问控制**: 限制敏感API的访问
6. ✅ **监控日志**: 定期检查访问和错误日志
7. ✅ **定期更新**: 保持系统和依赖的最新版本

你的项目已经很好地实现了这些最佳实践！🎉