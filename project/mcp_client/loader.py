"""
MCP工具加载器

负责从配置的MCP服务器加载工具并转换为LangChain工具格式
"""

import asyncio
import nest_asyncio
import logging
from typing import List, Dict, Any
from langchain_core.tools import BaseTool

from mcp_client.client import MCPClient
import config

# 允许嵌套事件循环，避免加载后 loop 被关闭的问题
nest_asyncio.apply()

logger = logging.getLogger(__name__)


class MCPToolLoader:
    """
    MCP工具加载器
    
    负责:
    - 读取配置中的MCP服务器列表
    - 初始化所有MCP客户端
    - 返回合并后的工具列表
    """
    
    def __init__(self):
        """初始化MCP工具加载器"""
        self._clients: Dict[str, MCPClient] = {}
        self._tools: List[BaseTool] = []
        
    def load_tools(self) -> List[BaseTool]:
        """
        加载所有MCP服务器的工具
        
        Returns:
            所有MCP工具的列表
        """
        # 检查是否启用MCP
        if not config.MCP_ENABLED:
            print("MCP is disabled, skipping MCP tool loading")
            return []
        
        mcp_servers = config.MCP_SERVERS
        
        if not mcp_servers:
            print("No MCP servers configured, skipping MCP tool loading")
            return []
        
        print(f"\n{'='*60}")
        print(f" Loading MCP tools from {len(mcp_servers)} server(s)...")
        print(f"{'='*60}")
        
        try:
            # 使用asyncio运行异步加载
            # 注意：不关闭 loop，让 MCP 会话保持活跃
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            self._tools = loop.run_until_complete(self._async_load_tools(mcp_servers))
            # 注意：这里不关闭 loop，让 MCP 连接保持活跃
        except Exception as e:
            logger.error(f"Failed to load MCP tools: {e}")
            print(f"✗ Error loading MCP tools: {e}")
            self._tools = []
        
        print(f"{'='*60}")
        print(f"✓ MCP tools loaded: {len(self._tools)} tools from {len(self._clients)} server(s)")
        if self._tools:
            print(f"  Tools: {', '.join([t.name for t in self._tools])}")
        print(f"{'='*60}\n")
        
        return self._tools
    
    async def _async_load_tools(self, mcp_servers: Dict[str, Dict[str, Any]]) -> List[BaseTool]:
        """
        异步加载MCP工具
        
        Args:
            mcp_servers: MCP服务器配置字典
            
        Returns:
            所有MCP工具的列表
        """
        all_tools = []
        
        for server_name, server_config in mcp_servers.items():
            try:
                print(f"\n  Connecting to MCP server: {server_name}")
                client = MCPClient(server_name, server_config)
                await client.connect()
                self._clients[server_name] = client
                
                tools = client.get_tools()
                all_tools.extend(tools)
                
                print(f"  - {server_name}: {len(tools)} tools loaded")
                
            except Exception as e:
                print(f"  ✗ Failed to connect to {server_name}: {e}")
                logger.warning(f"Failed to load MCP server '{server_name}': {e}")
                continue
        
        return all_tools
    
    async def close_all(self):
        """关闭所有MCP客户端连接"""
        for client in self._clients.values():
            try:
                await client.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting from MCP client: {e}")
        
        self._clients.clear()
        self._tools.clear()
    
    def get_clients(self) -> Dict[str, MCPClient]:
        """获取所有MCP客户端"""
        return self._clients
    
    def get_tools(self) -> List[BaseTool]:
        """获取已加载的工具"""
        return self._tools
    
    @property
    def client_count(self) -> int:
        """已连接的客户端数量"""
        return len(self._clients)
    
    @property
    def tool_count(self) -> int:
        """已加载的工具数量"""
        return len(self._tools)