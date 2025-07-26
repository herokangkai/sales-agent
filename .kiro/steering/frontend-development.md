---
inclusion: fileMatch
fileMatchPattern: '*.html|*.js|*.css'
---

# Frontend Development Guidelines

## HTML Structure

### Semantic HTML
- Use appropriate semantic elements
- Implement proper accessibility attributes
- Ensure responsive design principles

### Chat Interface Components
- Message container with proper scrolling
- Input area with send button
- Typing indicator for better UX
- Status display for system feedback

## JavaScript Best Practices

### Configuration Management
- Use centralized configuration object
- Support environment-specific settings
- Implement fallback values for missing config

```javascript
const CONFIG = AppConfig ? AppConfig.getDoubaoConfig() : {
    apiKey: 'fallback-key',
    baseUrl: 'default-url'
};
```

### Event Handling
- Use event delegation for dynamic content
- Implement proper cleanup for event listeners
- Handle keyboard shortcuts (Enter to send)

### Streaming Response UI
- Update UI incrementally during streaming
- Show typing indicators during processing
- Handle connection interruptions gracefully

```javascript
async function handleStreamingResponse(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            // Process and display chunk
            updateMessageDisplay(chunk);
        }
    } catch (error) {
        handleStreamingError(error);
    }
}
```

## CSS Styling

### Design System
- Use consistent color scheme
- Implement proper spacing and typography
- Ensure mobile responsiveness

### Chat Interface Styling
- Distinguish user vs bot messages clearly
- Implement smooth animations for new messages
- Use proper contrast ratios for accessibility

### Media Display
- Support image and video preview
- Implement modal dialogs for media viewing
- Handle different aspect ratios gracefully

## Error Handling

### User Feedback
- Show clear error messages to users
- Implement retry mechanisms for failed requests
- Provide loading states during operations

### Network Issues
- Handle offline scenarios
- Implement connection status indicators
- Cache messages locally when possible

## Performance Optimization

### Resource Loading
- Minimize initial page load time
- Lazy load non-critical resources
- Optimize images and media files

### Memory Management
- Clean up event listeners
- Limit message history in DOM
- Implement virtual scrolling for long conversations