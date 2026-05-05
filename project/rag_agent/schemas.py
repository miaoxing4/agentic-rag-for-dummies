from typing import List
from pydantic import BaseModel, Field

class QueryAnalysis(BaseModel):
    is_clear: bool = Field(
        description="Indicates if the user's question is clear and answerable."
    )
    questions: List[str] = Field(
        description="List of rewritten, self-contained questions."
    )
    clarification_needed: str = Field(
        description="Explanation if the question is unclear."
    )

class InputCheck(BaseModel):
    valid: bool = Field(
        description="是否所有必须内容都已经填写"
    )
    mode: str = Field(
        description="制式类型: LTE/NR/nbiot (仅当valid=True时有效)"
    )
    error_log: str = Field(
        description="错误打印原文，无则为空字符串"
    )
    issue_des: str = Field(
        description="问题描述原文，无则为空字符串"
    )
