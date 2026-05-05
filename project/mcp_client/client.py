"""
MCP Client - 用于连接MCP服务器并获取工具

该模块将 MCP 服务器作为一个统一的工具暴露给 Agent。
Agent 可以通过 MCP 协议的 list_tools 能力自动发现可用的动作。
"""

import os
import asyncio
import nest_asyncio
from typing import List, Dict, Any, Optional

# 允许在已有事件循环中嵌套运行
nest_asyncio.apply()
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool


class MCPToolInput(BaseModel):
    """MCP 工具调用的输入模式"""
    action: str = Field(description="要执行的 MCP 工具名称")
    params: Dict[str, Any] = Field(default_factory=dict, description="工具参数字典")


class MCPClient:
    """
    MCP 客户端封装类
    
    将整个 MCP 服务器作为一个统一的工具暴露给 Agent。
    Agent 可以通过 MCP 协议的 list_tools 能力自动发现可用的动作。
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        初始化 MCP 客户端
        
        Args:
            name: MCP 服务器名称 (用于标识)
            config: MCP 服务器配置，支持两种格式:
                1. Stdio 模式: {"command": "npx", "args": [...], "env": {}}
                2. SSE 模式: {"url": "https://example.com/mcp", "headers": {}}
        """
        self.name = name
        self.config = config
        
        # Stdio 配置
        self.command = config.get("command", "")
        self.args = config.get("args", [])
        self.env = config.get("env", {})
        
        # SSE 配置
        self.url = config.get("url", "")
        self.headers = config.get("headers", {})
        
        self._session = None
        self._tools = []
        self._available_actions = {}  # 存储可用的动作列表
        self._connection_type = None
        
    def _resolve_env_vars(self) -> Dict[str, str]:
        """解析环境变量，支持 ${VAR} 格式的引用"""
        resolved = {}
        for key, value in self.env.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                var_name = value[2:-1]
                resolved[key] = os.environ.get(var_name, "")
            else:
                resolved[key] = value
        return resolved
    
    async def connect(self):
        """连接到 MCP 服务器"""
        if self.url:
            await self._connect_sse()
        elif self.command:
            await self._connect_stdio()
        else:
            raise ValueError(f"MCP server '{self.name}' config must have either 'url' (for SSE) or 'command' (for Stdio)")
    
    async def _connect_sse(self):
        """通过 SSE 连接到远程 MCP 服务器"""
        try:
            from mcp.client.session import ClientSession
            from mcp.client.sse import sse_client
            
            print(f"\n  Connecting to MCP server via SSE: {self.name}")
            print(f"  URL: {self.url}")
            
            self._sse_client = sse_client(self.url, headers=self.headers)
            self._read, self._write = await self._sse_client.__aenter__()
            
            self._session = ClientSession(self._read, self._write)
            await self._session.__aenter__()
            
            await self._session.initialize()
            await self._discover_tools()
            
            self._connection_type = "sse"
            print(f"✓ MCP client '{self.name}' connected successfully")
            print(f"  - Available actions: {len(self._available_actions)}")
            
        except Exception as e:
            print(f"✗ Failed to connect to MCP server '{self.name}' via SSE: {e}")
            raise
    
    async def _connect_stdio(self):
        """通过 Stdio 连接到 MCP 服务器 (本地进程)"""
        try:
            from mcp.client.session import ClientSession
            from mcp.client.stdio import StdioServerParameters, stdio_client
            
            print(f"\n  Connecting to MCP server via Stdio: {self.name}")
            print(f"  Command: {self.command} {' '.join(self.args)}")
            
            env = os.environ.copy()
            env.update(self._resolve_env_vars())
            
            server_params = StdioServerParameters(
                command=self.command,
                args=self.args,
                env=env
            )
            
            self._stdio_client = stdio_client(server_params)
            self._read, self._write = await self._stdio_client.__aenter__()
            
            self._session = ClientSession(self._read, self._write)
            await self._session.__aenter__()
            
            await self._session.initialize()
            await self._discover_tools()
            
            self._connection_type = "stdio"
            print(f"✓ MCP client '{self.name}' connected successfully")
            print(f"  - Available actions: {len(self._available_actions)}")
            
        except Exception as e:
            print(f"✗ Failed to connect to MCP server '{self.name}': {e}")
            raise
    
    async def _discover_tools(self):
        """从 MCP 服务器发现可用的工具"""
        try:
            tools_response = await self._session.list_tools()
            
            # 构建动作描述
            descriptions = []
            for tool_def in tools_response.tools:
                tool_name = tool_def.name
                tool_description = getattr(tool_def, "description", "")
                self._available_actions[tool_name] = tool_description
                descriptions.append(f"- {tool_name}: {tool_description}")
            
            # 生成工具的描述
            self._tool_description = (
                f"MCP Server: {self.name}\n"
                f"Available actions:\n" + "\n".join(descriptions)
            )
            
        except Exception as e:
            print(f"  Warning: Failed to discover tools from '{self.name}': {e}")
    
    def get_tools(self) -> List:
        """
        获取 LangChain 工具列表
        每个 MCP 服务器作为一个统一的工具返回
        """
        if self._tools:
            return self._tools
        
        # 创建一个包装函数来处理 MCP 调用
        async def call_mcp(action: str, params: Dict[str, Any]) -> str:
            """调用 MCP 服务器的指定动作"""
            if action not in self._available_actions:
                return f"Error: Unknown action '{action}'. Available actions: {list(self._available_actions.keys())}"
            
            try:
                result = await self._session.call_tool(action, params)
                if hasattr(result, 'content'):
                    if isinstance(result.content, list):
                        return "\n".join([str(item) for item in result.content])
                    return str(result.content)
                return str(result)
            except Exception as e:
                return f"Error calling MCP action '{action}': {str(e)}"
        
        # 构建设用的动作列表描述
        available_actions_list = "\n".join([
            f"  - {name}: {desc[:100]}..." if len(desc) > 100 else f"  - {name}: {desc}"
            for name, desc in self._available_actions.items()
        ])
        
        tool_description = (
            f"MCP Server '{self.name}' - A unified tool that provides browser automation capabilities.\n"
            f"Available actions:\n{available_actions_list}\n\n"
            f"Parameters:\n"
            f"  - action: The name of the action to perform (e.g., navigate, screenshot, eval_js)\n"
            f"  - params: A dictionary of parameters for the action"
        )
        
        # 创建一个统一的工具代表整个 MCP 服务器
        # Stdio模式下，每次调用都创建新连接，避免进程状态问题
        async def call_mcp_new_connection(action: str, params: Dict[str, Any]) -> str:
            """每次调用时创建新连接 - 避免持久连接问题"""
            from mcp import StdioServerParameters
            from mcp.client.stdio import stdio_client
            from mcp.client.session import ClientSession
            
            if action not in self._available_actions:
                return f"Error: Unknown action '{action}'. Available actions: {list(self._available_actions.keys())}"
            
            try:
                # 从 config 获取服务器参数
                server_params = StdioServerParameters(
                    command=self.config.get("command", "npx"),
                    args=self.config.get("args", []),
                    env=self.config.get("env", {})
                )
                
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        result = await session.call_tool(action, params)
                        if hasattr(result, 'content'):
                            if isinstance(result.content, list):
                                return "\n".join([str(item) for item in result.content])
                            return str(result.content)
                        return str(result)
            except Exception as e:
                return f"Error calling MCP action '{action}': {str(e)}"
        
        def sync_wrapper(action: str, params: Dict[str, Any]) -> str:
            """同步包装 - 每次调用创建新连接"""
            return asyncio.run(call_mcp_new_connection(action, params))
        
        tool = StructuredTool(
            name=self.name,
            description=tool_description,
            args_schema=MCPToolInput,
            func=sync_wrapper,
            coroutine=call_mcp
        )
        
        self._tools = [tool]
        return self._tools
    
    async def disconnect(self):
        """断开与 MCP 服务器的连接"""
        try:
            if self._session:
                await self._session.__aexit__(None, None, None)
            if hasattr(self, '_stdio_client'):
                await self._stdio_client.__aexit__(None, None, None)
            if hasattr(self, '_sse_client'):
                await self._sse_client.__aexit__(None, None, None)
            print(f"✓ MCP client '{self.name}' disconnected")
        except Exception as e:
            print(f"Warning: Error disconnecting from '{self.name}': {e}")
    
    def __repr__(self):
        return f"MCPClient(name='{self.name}', actions={len(self._available_actions)})"