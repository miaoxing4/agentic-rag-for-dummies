from typing import List
from langchain_core.tools import tool
from db.parent_store_manager import ParentStoreManager

_collection = None
_parent_store_manager = ParentStoreManager()

@tool
def search_child_chunks(query: str, limit: int) -> str:
    """Search for the top K most relevant child chunks.
    
    Args:
        query: Search query string
        limit: Maximum number of results to return
    """
    print(f"\n [DEBUG]检索函数被调用了! query='{query}', limit={limit}")
    
    try:
        print(f" [DEBUG] 调用 collection.similarity_search()")
        
        # 先不设阈值，打印所有搜索结果看看
        raw_results = _collection.similarity_search_with_score(query, k=limit)
        
        print(f" [DEBUG] 原始搜索返回 {len(raw_results)} 条结果")
        for idx, (doc, score) in enumerate(raw_results):
            print(f"\n [DEBUG] 结果 #{idx+1}:")
            print(f"  相似度分数: {score}")
            print(f"  页面内容长度: {len(doc.page_content)}")
            print(f"  页面内容前100字符: '{doc.page_content[:100]}'")
            print(f"  Metadata: {doc.metadata}")
        
        # 原逻辑过滤
        results = [doc for doc, score in raw_results if score >= 0.7]
        
        print(f"\n🔍 [DEBUG] 经过0.7阈值过滤后剩余 {len(results)} 条结果")
        
        if not results:
            print(f"🔍 [DEBUG] 返回 NO_RELEVANT_CHUNKS")
            return "NO_RELEVANT_CHUNKS"

        output = "\n\n".join([
            f"Parent ID: {doc.metadata.get('parent_id', '')}\n"
            f"File Name: {doc.metadata.get('source', '')}\n"
            f"Content: {doc.page_content.strip()}"
            for doc in results
        ])
        
        print(f"[DEBUG] 返回检索结果，总长度 {len(output)}")
        return output            

    except Exception as e:
        print(f"[DEBUG] 检索异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"RETRIEVAL_ERROR: {str(e)}"

@tool
def retrieve_many_parent_chunks(parent_ids: List[str]) -> str:
    """Retrieve full parent chunks by their IDs.

    Args:
        parent_ids: List of parent chunk IDs to retrieve
    """
    try:
        ids = [parent_ids] if isinstance(parent_ids, str) else list(parent_ids)
        raw_parents = _parent_store_manager.load_content_many(ids)
        if not raw_parents:
            return "NO_PARENT_DOCUMENTS"

        return "\n\n".join([
            f"Parent ID: {doc.get('parent_id', 'n/a')}\n"
            f"File Name: {doc.get('metadata', {}).get('source', 'unknown')}\n"
            f"Content: {doc.get('content', '').strip()}"
            for doc in raw_parents
        ])            

    except Exception as e:
        return f"PARENT_RETRIEVAL_ERROR: {str(e)}"

@tool
def retrieve_parent_chunks(parent_id: str) -> str:
    """Retrieve full parent chunks by their IDs.

    Args:
        parent_id: Parent chunk ID to retrieve
    """
    try:
        parent = _parent_store_manager.load_content(parent_id)
        if not parent:
            return "NO_PARENT_DOCUMENT"

        return (
            f"Parent ID: {parent.get('parent_id', 'n/a')}\n"
            f"File Name: {parent.get('metadata', {}).get('source', 'unknown')}\n"
            f"Content: {parent.get('content', '').strip()}"
        )          

    except Exception as e:
        return f"PARENT_RETRIEVAL_ERROR: {str(e)}"


class ToolFactory:
    
    def __init__(self, collection):
        global _collection
        _collection = collection
    
    def create_tools(self) -> List:
        """Create and return the list of tools."""
        # 现在直接返回静态声明的工具，LLM可以正确识别Schema
        return [search_child_chunks, retrieve_parent_chunks]
