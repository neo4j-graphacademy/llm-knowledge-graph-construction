from llm import llm
from graph import graph
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.tools import Tool
from langchain_neo4j import Neo4jChatMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain import hub
from utils import get_session_id

from tools.vector import find_chunk
from tools.cypher import run_cypher

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI expert providing information about Neo4j and Knowledge Graphs."),
        ("human", "{input}"),
    ]
)

kg_chat = chat_prompt | llm | StrOutputParser()

tools = [
    Tool.from_function(
        name="General Chat",
        description="For general knowledge graph chat not covered by other tools",
        func=kg_chat.invoke,
    ), 
    Tool.from_function(
        name="Lesson content search",
        description="For when you need to find information in the lesson content",
        func=find_chunk, 
    ),
    Tool.from_function(
        name="Knowledge Graph information",
        description="For when you need to find information about the entities and relationship in the knowledge graph",
        func = run_cypher,
    )
]

def get_memory(session_id):
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)

agent_prompt = PromptTemplate.from_template("""
You are a Neo4j, Knowledge graph, and generative AI expert.
Be as helpful as possible and return as much information as possible.
Only answer questions that relate to Neo4j, graphs, cypher, generative AI, or associated subjects.
        
Always use a tool and only use the information provided in the context.

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
""")

agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,
    verbose=True
    )

chat_agent = RunnableWithMessageHistory(
    agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)

def generate_response(user_input):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """

    response = chat_agent.invoke(
        {"input": user_input},
        {"configurable": {"session_id": get_session_id()}},)

    return response['output']
