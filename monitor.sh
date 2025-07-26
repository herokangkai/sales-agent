#!/bin/bash

# Mogine AI Chatbot - 服务监控脚本
# 用于监控生产环境服务状态

echo "📊 摩泛AI聊天机器人服务监控"
echo "================================"

# 检查端口状态
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -i :$port >/dev/null 2>&1; then
        echo "✅ $service_name ($port) - 运行中"
        return 0
    else
        echo "❌ $service_name ($port) - 未运行"
        return 1
    fi
}

# 检查API响应
check_api() {
    local url=$1
    local api_name=$2
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" --connect-timeout 5)
    if [ "$response" = "200" ]; then
        echo "✅ $api_name - 响应正常 ($response)"
        return 0
    else
        echo "❌ $api_name - 响应异常 ($response)"
        return 1
    fi
}

# 检查服务状态
echo "🔍 检查服务端口状态..."
services_ok=0
check_port 8739 "知识库服务器" && ((services_ok++))
check_port 8740 "文件服务器" && ((services_ok++))
check_port 8741 "Web服务器" && ((services_ok++))

echo ""
echo "🌐 检查API响应状态..."
apis_ok=0
check_api "http://localhost:8739/api/company_info" "知识库API" && ((apis_ok++))
check_api "http://localhost:8740/kb/assets/" "文件服务API" && ((apis_ok++))

echo ""
echo "📈 系统资源使用情况..."

# CPU使用率
cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
echo "💻 CPU使用率: ${cpu_usage}%"

# 内存使用情况
memory_info=$(vm_stat | grep "Pages free\|Pages active\|Pages inactive\|Pages speculative\|Pages wired down")
echo "🧠 内存状态:"
echo "$memory_info" | while read line; do
    echo "   $line"
done

# 磁盘使用情况
echo "💾 磁盘使用情况:"
df -h / | tail -1 | awk '{print "   根目录: " $3 " / " $2 " (" $5 " 已使用)"}'

echo ""
echo "📋 进程状态..."
echo "Python进程:"
ps aux | grep python | grep -E "(simple_server|file_server|web_server)" | grep -v grep | while read line; do
    echo "   $line"
done

echo ""
echo "📊 网络连接状态..."
echo "活跃连接数:"
netstat -an | grep -E ":8739|:8740|:8741" | wc -l | awk '{print "   总连接数: " $1}'

echo ""
echo "📝 最近日志 (最后10行)..."
if [ -f "/www/wwwlogs/mogine_agent_access.log" ]; then
    echo "访问日志:"
    tail -5 /www/wwwlogs/mogine_agent_access.log | while read line; do
        echo "   $line"
    done
fi

if [ -f "/www/wwwlogs/mogine_agent_error.log" ]; then
    echo "错误日志:"
    tail -5 /www/wwwlogs/mogine_agent_error.log | while read line; do
        echo "   $line"
    done
fi

echo ""
echo "📊 监控总结..."
echo "服务状态: $services_ok/3 正常"
echo "API状态: $apis_ok/2 正常"

if [ $services_ok -eq 3 ] && [ $apis_ok -eq 2 ]; then
    echo "🎉 所有服务运行正常！"
    exit 0
else
    echo "⚠️  部分服务异常，请检查！"
    exit 1
fi