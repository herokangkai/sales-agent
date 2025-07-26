#!/bin/bash

# 摩泛AI聊天机器人 - 停止所有服务

echo "🛑 停止摩泛AI聊天机器人系统..."

# 停止所有相关服务
echo "📚 停止知识库服务器..."
pkill -f "simple_server.py" 2>/dev/null

echo "📁 停止文件服务器..."
pkill -f "file_server.py" 2>/dev/null

echo "🌐 停止Web服务器..."
pkill -f "web_server.py" 2>/dev/null

# 等待进程完全停止
sleep 3

# 检查端口是否已释放
echo "🔍 检查端口状态..."

if lsof -i :8739 >/dev/null 2>&1; then
    echo "⚠️  端口 8739 仍被占用"
else
    echo "✅ 端口 8739 已释放"
fi

if lsof -i :8740 >/dev/null 2>&1; then
    echo "⚠️  端口 8740 仍被占用"
else
    echo "✅ 端口 8740 已释放"
fi

if lsof -i :8741 >/dev/null 2>&1; then
    echo "⚠️  端口 8741 仍被占用"
else
    echo "✅ 端口 8741 已释放"
fi

echo ""
echo "🎉 所有服务已停止！"