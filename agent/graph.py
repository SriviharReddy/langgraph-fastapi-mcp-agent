from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode
from .tools import get_mcp_tools
from .nodes import agent_node


async def create_agent(checkpointer=None):

    tools = await get_mcp_tools()
    mcp_tools = ToolNode(tools)

    builder = StateGraph(MessagesState)

    builder.add_node("agent_node", agent_node)
    builder.add_node("mcp_tools", mcp_tools)

    builder.add_edge(START, "agent_node")
    builder.add_edge("mcp_tools", "agent_node")

    graph = builder.compile(checkpointer)

    return graph
