#!/bin/bash

# 摩泛AI聊天机器人快速设置脚本

echo "🚀 开始设置摩泛AI聊天机器人..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 创建虚拟环境（可选）
read -p "是否创建Python虚拟环境？(y/n): " create_venv
if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 安装依赖
echo "📥 安装Python依赖..."
pip install -r requirements.txt

# 复制环境变量模板
if [ ! -f .env ]; then
    echo "📋 复制环境变量模板..."
    cp .env.example .env
    echo "✅ 已创建.env文件"
else
    echo "ℹ️  .env文件已存在，跳过复制"
fi

# 提示用户配置API密钥
echo ""
echo "🔑 请配置你的API密钥："
echo "1. 编辑 .env 文件"
echo "2. 替换以下占位符为真实的API密钥："
echo "   - DOUBAO_API_KEY=your-doubao-api-key"
echo "   - DASHSCOPE_API_KEY=your-dashscope-api-key"
echo "   - DASHSCOPE_APP_ID=your-app-id"
echo ""

# 询问是否现在配置
read -p "是否现在打开.env文件进行配置？(y/n): " edit_env
if [[ $edit_env == "y" || $edit_env == "Y" ]]; then
    if command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    elif command -v code &> /dev/null; then
        code .env
    else
        echo "请手动编辑.env文件"
    fi
fi

echo ""
echo "🎉 设置完成！"
echo ""
echo "📚 启动说明："
echo "1. 启动知识库服务器：python simple_server.py"
echo "2. 启动文件服务器：python file_server.py"
echo "3. 打开浏览器访问：real_llm_chat.html"
echo ""
echo "📖 更多信息请查看："
echo "- README.md - 项目说明"
echo "- SECURITY.md - 安全配置说明"
echo ""
echo "⚠️  重要：请确保已正确配置.env文件中的API密钥！"