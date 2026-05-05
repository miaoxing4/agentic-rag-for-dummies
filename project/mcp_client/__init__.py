"""
MCP (Model Context Protocol) Client Module

This module provides functionality to connect to MCP servers and load their tools
into the RAG agent, enabling extended capabilities through MCP tools.

Usage:
    Configure MCP servers in environment variable MCP_SERVERS (JSON format)
    or point to a config file with @/path/to/config.json
    
    The RAG agent will automatically load and bind MCP tools at startup.
"""

from .client import MCPClient
from .loader import MCPToolLoader

__all__ = ["MCPClient", "MCPToolLoader"]
