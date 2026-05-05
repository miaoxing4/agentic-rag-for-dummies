import gradio as gr
from core.chat_interface import ChatInterface
from core.document_manager import DocumentManager
from core.rag_system import RAGSystem
import os

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

def create_gradio_ui():
    rag_system = RAGSystem()
    rag_system.initialize()
    
    doc_manager = DocumentManager(rag_system)
    chat_interface = ChatInterface(rag_system)
    
    def format_file_list():
        files = doc_manager.get_markdown_files()
        if not files:
            return "📭 No documents available in the knowledge base"
        return "\n".join([f"{f}" for f in files])
    
    def upload_handler(files, progress=gr.Progress()):
        if not files:
            return None, format_file_list()
            
        added, skipped = doc_manager.add_documents(
            files, 
            progress_callback=lambda p, desc: progress(p, desc=desc)
        )
        
        gr.Info(f"✅ Added: {added} | Skipped: {skipped}")
        return None, format_file_list()
    
    def clear_handler():
        doc_manager.clear_all()
        gr.Info(f"🗑️ Removed all documents")
        return format_file_list()
    
    def chat_handler(msg, hist):
        for chunk in chat_interface.chat(msg, hist):
            yield chunk
    
    def clear_chat_handler():
        chat_interface.clear_session()
    
    with gr.Blocks(title="Agentic RAG", fill_height=True) as demo:
        
        with gr.Tab("Documents", elem_id="doc-management-tab"):
            gr.Markdown("## Add New Documents")
            gr.Markdown("Upload PDF or Markdown files. Duplicates will be automatically skipped.")
            
            files_input = gr.File(
                label="Drop PDF or Markdown files here",
                file_count="multiple",
                type="filepath",
                height=200,
                show_label=False
            )
            
            add_btn = gr.Button("Add Documents", variant="primary", size="md")
            
            gr.Markdown("## Current Documents in the Knowledge Base")
            file_list = gr.Textbox(
                value=format_file_list(),
                interactive=False,
                lines = 7,
                max_lines=10,
                elem_id="file-list-box",
                show_label=False
            )
            
            with gr.Row():
                refresh_btn = gr.Button("Refresh", size="md")
                clear_btn = gr.Button("Clear All", variant="stop", size="md")
            
            add_btn.click(upload_handler, [files_input], [files_input, file_list], show_progress="corner")
            refresh_btn.click(format_file_list, None, file_list)
            clear_btn.click(clear_handler, None, file_list)
        
        with gr.Tab("Chat", elem_id="chat-tab"):
            chatbot = gr.Chatbot(
                height=720, 
                placeholder="""🔍 欢迎来到O-RAN L1问题诊断助手

请描述您遇到的问题，需包含：

【必填】制式        LTE / NR SA / NR NSA / NB-IoT
【必填】PHY相关日志    L1问题相关L1打印原文
【必填】业务现象    问题发生时的业务阶段或现象描述
 我将尽力为您提供定位参考！

──────────────────────────────
示例一（有明确错误打印）：
  制式：NR SA
  PHY相关日志：[PHY] MSG3 retransmission exhausted, ue_id=0x12, attempt=4
  现象：UE无法完成Attach，收不到测量消息
──────────────────────────────
⚠️ 仅凭现象描述（如"UE掉线"）无法定位问题，请务必提供错误信息。""",
                show_label=False,
                avatar_images=(None, os.path.join(ASSETS_DIR, "chatbot_avatar.png")),
                layout="bubble",
                elem_id="rag-chatbot"
            )
            chatbot.clear(clear_chat_handler)

            chat_input = gr.Textbox(
                placeholder="Type a message...",
                show_label=False,
                lines=1,
                max_lines=8,
                container=False,
                elem_id="rag-chat-input"
            )

            gr.ChatInterface(
                fn=chat_handler,
                chatbot=chatbot,
                textbox=chat_input,
                fill_height=True,
                show_progress="minimal"
            )
    
    return demo