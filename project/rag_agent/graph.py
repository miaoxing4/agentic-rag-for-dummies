from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode
from functools import partial

from .graph_state import State
from .nodes import *
from .edges import *

def create_agent_graph(llm, tools_list):
    print(f"\n\n{'='*80}")
    print(f" [GRAPH DEBUG] 收到的工具列表:")
    for idx, tool in enumerate(tools_list):
        print(f"   [{idx+1}] 工具名: {tool.name}")
        print(f"        参数: {list(tool.args.keys())}")
        print(f"        描述: {tool.description[:80]}...")
    print(f"{'='*80}\n")

    llm_with_tools = llm.bind_tools(tools_list)
    
    #  DEBUG: 验证绑定后的工具
    # print(f"\n [GRAPH DEBUG] bind_tools 之后的工具:")
    # if hasattr(llm_with_tools, 'tools'):
    #     for idx, tool in enumerate(llm_with_tools.tools):
    #         print(f"   [{idx+1}] 工具名: {tool.name}")
    # else:
    #     print(f" llm_with_tools 没有tools属性！")
    tool_node = ToolNode(tools_list)

    checkpointer = InMemorySaver()

    print("Compiling agent graph...")
    agent_builder = StateGraph(AgentState)
    agent_builder.add_node("orchestrator", partial(orchestrator, llm_with_tools=orchestrator))
    agent_builder.add_node("tools", tool_node)
    agent_builder.add_node("compress_context", partial(compress_context, llm=llm))
    agent_builder.add_node("fallback_response", partial(fallback_response, llm=llm))
    agent_builder.add_node(should_compress_context)
    agent_builder.add_node(collect_answer)

    agent_builder.set_entry_point("orchestrator")
    agent_builder.add_conditional_edges("orchestrator", route_after_orchestrator_call, {"tools": "tools", "fallback_response": "fallback_response", "collect_answer": "collect_answer"})
    agent_builder.add_edge("tools", "should_compress_context")
    agent_builder.add_edge("compress_context", "orchestrator")
    agent_builder.add_edge("fallback_response", "collect_answer")
    agent_builder.add_edge("collect_answer", END)

    agent_subgraph = agent_builder.compile()

    graph_builder = StateGraph(State)
    graph_builder.add_node("summarize_history", partial(summarize_history, llm=llm))
    graph_builder.add_node("diag_input_check", partial(diag_input_check, llm=llm))
    graph_builder.add_node("rewrite_query", partial(rewrite_query, llm=llm))
    graph_builder.add_node(request_clarification)
    graph_builder.add_node("agent", agent_subgraph)
    graph_builder.add_node("aggregate_answers", partial(aggregate_answers, llm=llm))

    graph_builder.add_edge(START, "summarize_history")
    # graph_builder.add_edge("summarize_history", "rewrite_query")
    # graph_builder.add_conditional_edges("rewrite_query", route_after_rewrite)
    # graph_builder.add_edge("request_clarification", "rewrite_query")
    graph_builder.add_edge("summarize_history", "diag_input_check")
    graph_builder.add_conditional_edges("diag_input_check", route_after_input_check)
    graph_builder.add_edge("request_clarification", "diag_input_check")
    graph_builder.add_edge(["agent"], "aggregate_answers")
    graph_builder.add_edge("aggregate_answers", END)

    agent_graph = graph_builder.compile(checkpointer=checkpointer, interrupt_before=["request_clarification"])

    print("✓ Agent graph compiled successfully.")
    return agent_graph