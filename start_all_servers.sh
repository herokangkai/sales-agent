#!/bin/bash

# 摩泛AI聊天机器人 - 启动所有服务

echo "🚀 启动摩泛AI聊天机器人系统..."

# 检查环境变量
if [ ! -f .env ]; then
    echo "❌ .env文件不存在，请先配置环境变量"
    exit 1
fi

# 检查Python依赖
python -c "import dotenv, httpx, fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Python依赖缺失，请运行: pip install -r requirements.txt"
    exit 1
fi

# 停止已存在的服务
echo "🛑 停止现有服务..."
pkill -f "simple_server.py" 2>/dev/null
pkill -f "file_server.py" 2>/dev/null  
pkill -f "web_server.py" 2>/dev/null
sleep 2

# 启动知识库服务器
echo "📚 启动知识库服务器 (端口 8739)..."
python simple_server.py &
KB_PID=$!

# 启动文件服务器
echo "📁 启动文件服务器 (端口 8740)..."
python file_server.py &
FILE_PID=$!

# 启动Web服务器
echo "🌐 启动Web服务器 (端口 8741)..."
python web_server.py &
WEB_PID=$!

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo "🔍 检查服务状态..."

if lsof -i :8739 >/dev/null 2>&1; then
    echo "✅ 知识库服务器 (8739) - 运行中"
else
    echo "❌ 知识库服务器 (8739) - 启动失败"
fi

if lsof -i :8740 >/dev/null 2>&1; then
    echo "✅ 文件服务器 (8740) - 运行中"
else
    echo "❌ 文件服务器 (8740) - 启动失败"
fi

if lsof -i :8741 >/dev/null 2>&1; then
    echo "✅ Web服务器 (8741) - 运行中"
else
    echo "❌ Web服务器 (8741) - 启动失败"
fi

echo ""
echo "🎉 系统启动完成！"
echo ""
echo "📱 访问方式："
echo "   聊天界面: http://localhost:8741/real_llm_chat.html"
echo "   知识库API: http://localhost:8739/api/search"
echo "   文件服务: http://localhost:8740/kb/assets/"
echo ""
echo "🔧 管理命令："
echo "   查看日志: tail -f *.log"
echo "   停止服务: ./stop_all_servers.sh"
echo "   重启服务: ./restart_servers.sh"
echo ""
echo "⏹️  按 Ctrl+C 停止所有服务"

# 等待用户中断
trap 'echo -e "\n🛑 正在停止所有服务..."; kill $KB_PID $FILE_PID $WEB_PID 2>/dev/null; exit 0' INT

# 保持脚本运行
wait