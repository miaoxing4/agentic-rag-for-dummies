custom_css = """
    /* ============================================
       MAIN CONTAINER
       ============================================ */
    .progress-text { 
        display: none !important;
    }
    
    .gradio-container { 
        max-width: 1000px !important;
        width: 100% !important;
        margin: 0 auto !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        background: #0f0f0f !important;
    }
    
    /* ============================================
       TABS
       ============================================ */
    button[role="tab"] {
        color: #a3a3a3 !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0 !important;
        transition: all 0.2s ease !important;
        background: transparent !important;
    }
    
    button[role="tab"]:hover {
        color: #e5e5e5 !important;
    }
    
    button[role="tab"][aria-selected="true"] {
        color: #ffffff !important;
        border-bottom: 2px solid #ffffff !important;
        border-radius: 0 !important;
        background: transparent !important;
    }
    
    .tabs {
        border-bottom: none !important;
        border-radius: 0 !important;
    }
    
    .tab-nav {
        border-bottom: 1px solid #3f3f3f !important;
        border-radius: 0 !important;
    }
    
    button[role="tab"]::before,
    button[role="tab"]::after,
    .tabs::before,
    .tabs::after,
    .tab-nav::before,
    .tab-nav::after {
        display: none !important;
        content: none !important;
        border-radius: 0 !important;
    }
    
    #doc-management-tab {
        max-width: 500px !important;
        margin: 0 auto !important;
    }
    
    /* ============================================
       BUTTONS
       ============================================ */
    button {
        border-radius: 8px !important;
        border: none !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
    }
    
    .primary {
        background: #3b82f6 !important;
        color: white !important;
    }
    
    .primary:hover {
        background: #2563eb !important;
        transform: translateY(-1px) !important;
    }
    
    .stop {
        background: #ef4444 !important;
        color: white !important;
    }
    
    .stop:hover {
        background: #dc2626 !important;
        transform: translateY(-1px) !important;
    }
    
    /* ============================================
       CHAT INPUT BOX
       ============================================ */
    #chat-tab #rag-chat-input textarea,
    #chat-tab textarea[data-testid="textbox"]:not([disabled]) {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    #chat-tab #rag-chat-input textarea:focus,
    #chat-tab textarea[data-testid="textbox"]:not([disabled]):focus {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    #chat-tab #rag-chat-input,
    #chat-tab form:has(#rag-chat-input) > div,
    #chat-tab form:has(textarea[data-testid="textbox"]:not([disabled])) > div {
        background: transparent !important;
        border: none !important;
        gap: 12px !important;
    }
    
    #chat-tab form:has(#rag-chat-input) button,
    #chat-tab form:has(textarea[data-testid="textbox"]:not([disabled])) button {
        background: transparent !important;
        border: none !important;
        padding: 8px !important;
    }
    
    #chat-tab form:has(#rag-chat-input) button:hover,
    #chat-tab form:has(textarea[data-testid="textbox"]:not([disabled])) button:hover {
        background: rgba(59, 130, 246, 0.1) !important;
    }
    
    #chat-tab form:has(#rag-chat-input),
    #chat-tab form:has(textarea[data-testid="textbox"]:not([disabled])) {
        gap: 12px !important;
        display: flex !important;
    }
    
    /* ============================================
       FILE UPLOAD
       ============================================ */
    .file-preview, 
    [data-testid="file-upload"] {
        background: #1a1a1a !important;
        border: 1px solid #3f3f3f !important;
        border-radius: 5px !important;
        color: #ffffff !important;
        min-height: 200px !important;
    }
    
    .file-preview:hover, 
    [data-testid="file-upload"]:hover {
        border-color: #3b82f6 !important;
        background: #1f1f1f !important;
    }
    
    .file-preview *,
    [data-testid="file-upload"] * {
        color: #ffffff !important;
    }
    
    .file-preview .label,
    [data-testid="file-upload"] .label {
        display: none !important;
    }
    
    /* ============================================
       INPUTS & TEXTAREAS
       ============================================ */
    input, 
    textarea {
        background: #1a1a1a !important;
        border: 1px solid #3f3f3f !important;
        border-radius: 10px !important;
        color: #e5e5e5 !important;
        transition: border-color 0.2s ease !important;
    }
    
    input:focus, 
    textarea:focus {
        border-color: #3b82f6 !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    textarea[readonly] {
        background: #1a1a1a !important;
        color: #a3a3a3 !important;
    }
    
    /* ============================================
       FILE LIST BOX
       ============================================ */
    #file-list-box {
        background: #1a1a1a !important;
        border: 1px solid #3f3f3f !important;
        border-radius: 5px !important;
        padding: 10px !important;
    }
    
    #file-list-box textarea {
        background: transparent !important;
        border: none !important;
        color: #e5e5e5 !important;
        padding: 0 !important;
    }
    
    /* ============================================
       CHATBOT CONTAINER
       ============================================ */
    #rag-chatbot,
    #rag-chatbot .bubble-wrap,
    #chat-tab [aria-label="chatbot conversation"] {
        border-radius: 5px !important;
        background: #1a1a1a !important;
        border: none !important;
    }

    #rag-chatbot .message-wrap,
    #chat-tab [aria-label="chatbot conversation"] .message-wrap,
    #rag-chatbot > div {
        gap: 8px !important;
        padding: 12px !important;
    }

    /* ============================================
       MESSAGE BUBBLES
       ============================================ */
    .message {
        border-radius: 10px !important;
    }

    #chat-tab .user-row .message,
    #chat-tab [data-testid="user"] {
        background: #3b82f6 !important;
        color: white !important;
    }
    
    #chat-tab .bot-row .message,
    #chat-tab .assistant-row .message,
    #chat-tab [data-testid="bot"],
    #chat-tab [data-testid="assistant"] {
        background: #1f1f1f !important;
        color: #e5e5e5 !important;
        border: 1px solid #3f3f3f !important;
        width: fit-content !important;
        max-width: 90% !important;
    }
    
    .message-row img {
        margin: 0px !important;
    }

    .avatar-container img {
        padding: 0px !important;
    }

    /* ============================================
       PROGRESS BAR
       ============================================ */
    .progress-bar-wrap {
        border-radius: 10px !important;
        overflow: hidden !important;
        background: #1a1a1a !important;
    }

    .progress-bar {
        border-radius: 10px !important;
        background: #3b82f6 !important;
    }
    
    /* ============================================
       TYPOGRAPHY
       ============================================ */
    h1, h2, h3, h4, h5, h6 {
        color: #e5e5e5 !important;
    }
    
    /* ============================================
       GLOBAL OVERRIDES
       ============================================ */
    * {
        box-shadow: none !important;
    }
    
    footer {
        visibility: hidden;
    }
    /* ============================================
       EMERGENCY INPUT FIXES (追加部分)
       ============================================ */
    
    /* 1. 确保所有输入框文字在深色背景下为白色/浅灰色 */
    #rag-chat-input textarea, 
    #file-list-box textarea,
    textarea[data-testid="textbox"],
    input[type="text"] {
        color: #f3f4f6 !important; /* 浅灰色文字 */
        -webkit-text-fill-color: #f3f4f6 !important; /* 适配部分浏览器 */
    }

    /* 2. 修复输入框占位符颜色，防止它看起来像空白 */
    ::placeholder {
        color: #6b7280 !important; /* 暗灰色占位符 */
        opacity: 1; 
    }

    /* 3. 强制 Chat 输入框容器背景为深色，防止透明导致背景色透出问题 */
    #rag-chat-input {
        background: #1a1a1a !important;
        border: 1px solid #3f3f3f !important;
    }

    /* 4. 修复 Gradio 4.x+ 版本的内层容器背景 */
    .gradio-container .tab-item {
        background: #0f0f0f !important;
    }
"""