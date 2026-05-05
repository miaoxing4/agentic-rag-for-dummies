import uuid
import os
from langchain_ollama import ChatOllama
import config
from db.vector_db_manager import VectorDbManager
from db.parent_store_manager import ParentStoreManager
from document_chunker import DocumentChuncker
from rag_agent.tools import ToolFactory
from rag_agent.graph import create_agent_graph
from core.observability import Observability

class RAGSystem:

    def __init__(self, collection_name=config.CHILD_COLLECTION):
        self.collection_name = collection_name
        self.vector_db = VectorDbManager()
        self.parent_store = ParentStoreManager()
        self.chunker = DocumentChuncker()
        self.observability = Observability()
        self.agent_graph = None
        self.thread_id = str(uuid.uuid4())
        self.recursion_limit = config.GRAPH_RECURSION_LIMIT

    def initialize(self):
        self.vector_db.create_collection(self.collection_name)
        collection = self.vector_db.get_collection(self.collection_name)

        # Load active configuration
        active_config = config.LLM_CONFIGS[config.ACTIVE_LLM_CONFIG]
        model = active_config["model"]
        temperature = active_config.get("temperature", 0)

        if config.ACTIVE_LLM_CONFIG == "ollama":
            from langchain_ollama import ChatOllama
            llm = ChatOllama(model=model, temperature=temperature, base_url=active_config["url"])
            
        elif config.ACTIVE_LLM_CONFIG == "openai":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model=model, temperature=temperature)
            
        elif config.ACTIVE_LLM_CONFIG == "anthropic":
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(model=model, temperature=temperature)
            
        elif config.ACTIVE_LLM_CONFIG == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)
        
        elif config.ACTIVE_LLM_CONFIG == "openai_compatible":
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                base_url=active_config.get("base_url"), 
                api_key=active_config.get("api_key")
            )
            
        else:
            raise ValueError(f"Unsupported LLM provider: {config.ACTIVE_LLM_CONFIG}")
        
        # 创建基础RAG工具
        base_tools = ToolFactory(collection).create_tools()
        
        # 加载MCP工具
        from mcp_client.loader import MCPToolLoader
        mcp_loader = MCPToolLoader()
        mcp_tools = mcp_loader.load_tools()
        
        # 合并工具列表
        all_tools = base_tools + mcp_tools
        
        # 保存MCP加载器引用以便后续关闭连接
        self._mcp_loader = mcp_loader
        
        self.agent_graph = create_agent_graph(llm, all_tools)

    def get_config(self):
        cfg = {"configurable": {"thread_id": self.thread_id}, "recursion_limit": self.recursion_limit}
        handler = self.observability.get_handler()
        if handler:
            cfg["callbacks"] = [handler]
        return cfg

    def reset_thread(self):
        try:
            self.agent_graph.checkpointer.delete_thread(self.thread_id)
        except Exception as e:
            print(f"Warning: Could not delete thread {self.thread_id}: {e}")
        self.thread_id = str(uuid.uuid4())