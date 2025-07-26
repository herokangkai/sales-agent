// 真实LLM聊天机器人 - JavaScript部分

// 确保配置已加载
if (typeof AppConfig === 'undefined') {
    console.error('配置文件未加载，请确保config.js已正确引入');
}

// 豆包API配置 - 从配置文件获取
const DOUBAO_CONFIG = AppConfig ? AppConfig.getDoubaoConfig() : {
    apiKey: 'your-doubao-api-key',
    baseUrl: 'https://ark.cn-beijing.volces.com/api/v3',
    model: 'doubao-1-5-thinking-vision-pro-250428'
};

// DashScope配置
const DASHSCOPE_CONFIG = AppConfig ? AppConfig.getDashScopeConfig() : {
    apiKey: 'your-dashscope-api-key',
    baseUrl: 'https://dashscope.aliyuncs.com/api/v1/apps/your-app-id/completion'
};

// 服务器配置
const SERVER_CONFIG = AppConfig ? AppConfig.getServerConfig() : {
    kbServer: 'http://localhost:8739',
    fileServer: 'http://localhost:8740',
    mainServer: 'http://localhost:8741'
};

// DOM元素
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const typingIndicator = document.getElementById('typingIndicator');
const statusDiv = document.getElementById('status');
const scrollToBottomBtn = document.getElementById('scrollToBottom');

// 添加消息到聊天界面
function addMessage(content, isUser = false, mediaFiles = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // 创建文本容器
    const textContainer = document.createElement('div');
    textContainer.className = 'text-content';
    textContainer.innerHTML = content.replace(/\n/g, '<br>');
    contentDiv.appendChild(textContainer);
    
    // 添加媒体文件展示
    if (mediaFiles && mediaFiles.length > 0) {
        const mediaGallery = document.createElement('div');
        mediaGallery.className = 'media-gallery';
        
        mediaFiles.forEach(media => {
            const mediaItem = document.createElement('div');
            mediaItem.className = 'media-item';
            
            if (media.type === 'image') {
                const img = document.createElement('img');
                img.src = media.path;
                img.alt = media.caption;
                img.onclick = () => openModal(media.path);
                img.onerror = function() {
                    console.error('图片加载失败:', media.path);
                };
                img.onload = function() {
                    console.log('图片加载成功:', media.path);
                };
                mediaItem.appendChild(img);
            } else if (media.type === 'video') {
                const video = document.createElement('video');
                video.src = media.path;
                video.controls = true;
                video.muted = true;
                video.onerror = function() {
                    console.error('视频加载失败:', media.path);
                };
                video.onloadeddata = function() {
                    console.log('视频加载成功:', media.path);
                };
                mediaItem.appendChild(video);
            }
            
            if (media.caption) {
                const caption = document.createElement('div');
                caption.className = 'media-caption';
                caption.textContent = media.caption;
                mediaItem.appendChild(caption);
            }
            
            mediaGallery.appendChild(mediaItem);
        });
        
        contentDiv.appendChild(mediaGallery);
    }
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    
    // 平滑滚动到底部
    setTimeout(() => {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 50);

    return textContainer; // 返回文本容器，用于流式输出
}

// 图片预览模态框
function openModal(imageSrc) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    modal.style.display = 'block';
    modalImg.src = imageSrc;
}

function closeModal() {
    document.getElementById('imageModal').style.display = 'none';
}

// 显示/隐藏打字指示器
function showTyping(show = true) {
    typingIndicator.style.display = show ? 'block' : 'none';
    if (show) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// 更新状态
function updateStatus(message, type = 'normal') {
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
}

// 查询知识库
async function queryKnowledgeBase(query) {
    try {
        const response = await fetch(`${SERVER_CONFIG.kbServer}/api/search?q=${encodeURIComponent(query)}&top_k=3`);
        if (!response.ok) {
            throw new Error('知识库API请求失败');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('知识库查询错误:', error);
        return {
            success: false,
            error: error.message,
            results: []
        };
    }
}

// 调用豆包API
async function callDoubaoAPI(messages, stream = false) {
    try {
        const response = await fetch(`${DOUBAO_CONFIG.baseUrl}/chat/completions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${DOUBAO_CONFIG.apiKey}`
            },
            body: JSON.stringify({
                model: DOUBAO_CONFIG.model,
                messages: messages,
                temperature: 0.7,
                max_tokens: 1000,
                stream: stream
            })
        });

        if (!response.ok) {
            throw new Error(`豆包API请求失败: ${response.status}`);
        }

        if (stream) {
            return response;
        } else {
            const data = await response.json();
            return data.choices[0].message.content;
        }
    } catch (error) {
        console.error('豆包API调用错误:', error);
        throw error;
    }
}

// 真实流式输出
async function streamLLMResponse(messages, targetElement, mediaFiles = []) {
    try {
        const response = await callDoubaoAPI(messages, true);
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        let content = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') return;
                    
                    try {
                        const parsed = JSON.parse(data);
                        if (parsed.choices && parsed.choices[0].delta && parsed.choices[0].delta.content) {
                            content += parsed.choices[0].delta.content;
                            targetElement.innerHTML = content.replace(/\n/g, '<br>');
                            messagesContainer.scrollTop = messagesContainer.scrollHeight;
                        }
                    } catch (e) {
                        // 忽略JSON解析错误
                    }
                }
            }
        }
        
        // 流式输出完成后，添加媒体文件
        if (mediaFiles && mediaFiles.length > 0) {
            const mediaGallery = document.createElement('div');
            mediaGallery.className = 'media-gallery';
            
            mediaFiles.forEach(media => {
                const mediaItem = document.createElement('div');
                mediaItem.className = 'media-item';
                
                if (media.type === 'image') {
                    const img = document.createElement('img');
                    img.src = media.path;
                    img.alt = media.caption;
                    img.onclick = () => openModal(media.path);
                    mediaItem.appendChild(img);
                } else if (media.type === 'video') {
                    const video = document.createElement('video');
                    video.src = media.path;
                    video.controls = true;
                    video.muted = true;
                    mediaItem.appendChild(video);
                }
                
                if (media.caption) {
                    const caption = document.createElement('div');
                    caption.className = 'media-caption';
                    caption.textContent = media.caption;
                    mediaItem.appendChild(caption);
                }
                
                mediaGallery.appendChild(mediaItem);
            });
            
            targetElement.parentElement.appendChild(mediaGallery);
        }
        
    } catch (error) {
        targetElement.innerHTML = `抱歉，LLM调用出现错误：${error.message}`;
    }
}

// 处理消息发送 - 真实LLM版本
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    // 禁用输入
    messageInput.disabled = true;
    sendButton.disabled = true;
    messageInput.value = '';

    // 添加用户消息
    addMessage(message, true);
    
    // 显示处理状态
    showTyping(true);
    updateStatus('正在查询知识库...', 'normal');

    try {
        // 1. 查询知识库
        const kbResult = await queryKnowledgeBase(message);
        await new Promise(resolve => setTimeout(resolve, 300));

        updateStatus('正在调用豆包API...', 'normal');

        // 2. 构建LLM提示
        let systemPrompt = `你是摩泛科技的AI助手小摩。请基于提供的知识库信息回答用户问题。

摩泛科技是一家深耕高保真空间数字孪生的科技公司，专注于AI、IoT、LLM等技术。

如果知识库中有相关信息，请优先使用；如果没有，请基于你的知识回答，但要说明这不是来自摩泛科技的官方信息。

在回答中，如果有相关的图片或视频，请提及它们，我会在回答后展示这些媒体文件。`;

        let userPrompt = `用户问题：${message}\n\n`;
        
        let mediaFiles = [];
        
        if (kbResult.success && kbResult.results.length > 0) {
            userPrompt += `知识库信息：\n`;
            kbResult.results.forEach((result, index) => {
                userPrompt += `${index + 1}. ${result.title}: ${result.content}\n`;
                if (result.solution) {
                    userPrompt += `   解决方案: ${result.solution}\n`;
                }
                if (result.media_files && result.media_files.length > 0) {
                    userPrompt += `   相关媒体文件:\n`;
                    result.media_files.forEach(media => {
                        const mediaType = media.type === 'image' ? '图片' : '视频';
                        userPrompt += `     - ${mediaType}: ${media.caption}\n`;
                        mediaFiles.push({
                            type: media.type,
                            path: `${SERVER_CONFIG.fileServer}/${media.path}`,
                            caption: media.caption
                        });
                    });
                }
                userPrompt += `\n`;
            });
        } else {
            userPrompt += `知识库中未找到相关信息，请基于你的通用知识回答。\n`;
        }

        // 3. 调用LLM并流式输出
        showTyping(false);
        updateStatus('正在生成回答...', 'normal');

        const textContainer = addMessage('', false);
        
        const messages = [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt }
        ];

        await streamLLMResponse(messages, textContainer, mediaFiles);

        updateStatus('回答完成 - 真实LLM响应', 'success');

    } catch (error) {
        showTyping(false);
        addMessage(`抱歉，处理过程中出现错误：${error.message}`, false);
        updateStatus('处理出错', 'error');
    } finally {
        // 恢复输入
        messageInput.disabled = false;
        sendButton.disabled = false;
        messageInput.focus();
    }
}

// 滚动到底部功能
function scrollToBottom() {
    messagesContainer.scrollTo({
        top: messagesContainer.scrollHeight,
        behavior: 'smooth'
    });
}

// 监听滚动事件
messagesContainer.addEventListener('scroll', function() {
    const scrollTop = messagesContainer.scrollTop;
    const scrollHeight = messagesContainer.scrollHeight;
    const clientHeight = messagesContainer.clientHeight;
    
    if (scrollHeight - scrollTop - clientHeight > 100) {
        scrollToBottomBtn.classList.add('show');
    } else {
        scrollToBottomBtn.classList.remove('show');
    }
});

// 测试问题快捷按钮
function testQuestion(question) {
    messageInput.value = question;
    sendMessage();
}

// 键盘事件处理
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// 点击模态框外部关闭
window.onclick = function (event) {
    const modal = document.getElementById('imageModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', function () {
    messageInput.focus();
    updateStatus('真实LLM版本已就绪 - 每次回答都是实时生成', 'success');
});