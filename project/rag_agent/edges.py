from typing import Literal
from langgraph.types import Send
from .graph_state import State, AgentState
from config import MAX_ITERATIONS, MAX_TOOL_CALLS

def route_after_rewrite(state: State) -> Literal["request_clarification", "agent"]:
    print(f"\n\n🛣️ [ROUTE DEBUG] route_after_rewrite 被调用了!")
    print(f"   questionIsClear = {state.get('questionIsClear', False)}")
    print(f"   rewrittenQuestions = {state.get('rewrittenQuestions', [])}")
    
    if not state.get("questionIsClear", False):
        print(f"   🚏 路由到: request_clarification")
        return "request_clarification"
    else:
        print(f"   🚏 路由到: 启动 {len(state['rewrittenQuestions'])} 个并行Agent")
        for idx, query in enumerate(state["rewrittenQuestions"]):
            print(f"      [{idx+1}] {query}")
            
        return [
                Send("agent", {"question": query, "question_index": idx, "messages": []})
                for idx, query in enumerate(state["rewrittenQuestions"])
            ]
    
def route_after_input_check(state: State) -> Literal["request_clarification", "agent"]:
    print(f"\n\n🛣️ [ROUTE DEBUG] route_after_input_check 被调用了!")
    print(f"   error_log = {state.get('error_log', False)}")
    print(f"   issue_des = {state.get('issue_des', [])}")
    
    if not state.get("valid", False):
        print(f"   🚏 路由到: request_clarification")
        return "request_clarification"
    else:
        print(f"   🚏 路由到: 启动 2 个并行Agent,分别处理日志和描述")
        return [
                Send("agent", {"question": state.get('error_log', False), "question_index": 0, "messages": []}),
                Send("agent", {"question": state.get('issue_des', []), "question_index": 0, "messages": []})
            ]
    
def route_after_orchestrator_call(state: AgentState) -> Literal["tool", "fallback_response", "collect_answer"]:
    iteration = state.get("iteration_count", 0)
    tool_count = state.get("tool_call_count", 0)

    if iteration >= MAX_ITERATIONS or tool_count > MAX_TOOL_CALLS:
        return "fallback_response"

    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", None) or []

    if not tool_calls:
        return "collect_answer"
    
    return "tools"