from .tools import get_mcp_tools
from config import settings
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import MessagesState
from langgraph.types import Command
from typing import Literal

llm = ChatDeepSeek(
    api_key=settings.deepseek_api_key,
    model=settings.deepseek_model,
    extra_body=settings.deepseek_extra_body,
)


async def agent_node(state: MessagesState) -> Command[Literal["mcp_tools", "__end__"]]:

    tools = await get_mcp_tools()
    llm_with_tools = llm.bind_tools(tools)

    result = await llm_with_tools.ainvoke(state["messages"])

    if result.tool_calls:
        goto_node = "mcp_tools"
    else:
        goto_node = "__end__"

    return Command(update={"messages": [result]}, goto=goto_node)
