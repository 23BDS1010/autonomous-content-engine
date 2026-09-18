import time
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

def get_text(msg_content):
    if isinstance(msg_content, list):
        return msg_content[0].get("text", "")
    return str(msg_content)

def researcher_node(state: AgentState):
    print("\n[NODE: Researcher] Gathering historical facts...")
    time.sleep(1)
    return {"messages": [AIMessage(content="Fact: Built by the Pallava dynasty.")]}

def scriptwriter_node(state: AgentState):
    print("\n[NODE: Scriptwriter] Drafting the script...")
    time.sleep(1)
    
    turn_count = len(state["messages"])
    
    if turn_count <= 2:
        print("-> (Simulating that we need more research...)")
        return {"messages": [AIMessage(content="NEED_RESEARCH: Need more details.")]}
    else:
        script_output = "* [SCENE 1] - (0:03)\n* ACTION: Roblox R6 blocky character.\n* VO: 'Look at this!'\n* OST: Temple vibes 🏛️"
        return {"messages": [AIMessage(content=script_output)]}

def routing_logic(state: AgentState):
    last_message = get_text(state["messages"][-1].content)
    
    if "NEED_RESEARCH" in last_message:
        print("-> ROUTER: Looping back to Researcher.")
        return "researcher"
        
    print("-> ROUTER: Script is complete. Ending graph successfully!")
    return END

workflow = StateGraph(AgentState)
workflow.add_node("researcher", researcher_node)
workflow.add_node("scriptwriter", scriptwriter_node)

workflow.add_edge(START, "researcher")
workflow.add_edge("researcher", "scriptwriter")

workflow.add_conditional_edges(
    "scriptwriter",
    routing_logic,
    {"researcher": "researcher", END: END}
)

app = workflow.compile()

if __name__ == "__main__":
    initial_input = {"messages": [HumanMessage(content="Create a video script about the Mahabalipuram temple.")]}
    print("Starting Multi-Agent Workflow...")
    
    for event in app.stream(initial_input, config={"recursion_limit": 6}):
        for key, value in event.items():
            print(f"\n--- Output from {key.upper()} ---")
            print(get_text(value['messages'][0].content))
            print("-----------------------------------")
