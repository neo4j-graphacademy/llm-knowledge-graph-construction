#✅ Kullanıcının sorusunu analiz edip,
#✅ En uygun aracı (vektör arama, Cypher sorgusu, genel sohbet) seçmek,
#✅ Neo4j veritabanından bilgi çekmek,
#✅ Konuşma geçmişini yönetmek ve yanıtı üretmektir.


# llm: ChatOpenAI nesnesi. llm.py dosyasından import ediliyor.
from llm import llm

# graph: Neo4j bağlantısı. graph.py dosyasından geliyor.
from graph import graph

# LangChain ile sohbet promptları tanımlamak için kullanılıyor.
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate

# LLM yanıtını string olarak almak için parser.
from langchain.schema import StrOutputParser

# Tool nesnesi tanımlamak için kullanılıyor.
from langchain.tools import Tool

# Konuşma geçmişini Neo4j'de saklamak için.
from langchain_neo4j import Neo4jChatMessageHistory

# ReAct tarzı (reasoning + action) ajan oluşturmak için kullanılıyor.
from langchain.agents import AgentExecutor, create_react_agent

# Ajana konuşma geçmişi bağlamak için yardımcı sınıf.
from langchain_core.runnables.history import RunnableWithMessageHistory

# Ortak prompt'ları almak için LangChain Hub.
from langchain import hub

# Oturum kimliğini almak için yardımcı fonksiyon.
from utils import get_session_id

# Vektör tabanlı arama yapan tool
from solutions.tools.vector import find_chunk

# Cypher sorgularını çalıştıran tool
from solutions.tools.cypher import run_cypher


# Basit bir sistem prompt'u tanımlanıyor. LLM'e nasıl davranması gerektiği belirtiliyor.
chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI expert providing information about Neo4j and Knowledge Graphs. You answer questions based on maritime news."),
        ("human", "{input}"),   
    ]
)

# Bu prompt, LLM ve string parser ile zincirleniyor.
kg_chat = chat_prompt | llm | StrOutputParser()


# LangChain "Tool" API'si ile üç adet araç tanımlanıyor:
tools = [
    Tool.from_function(
        name="General Chat",
        description="For general knowledge graph chat not covered by other tools",
        func=kg_chat.invoke,  # Genel amaçlı bilgi veren zincir
    ), 
    Tool.from_function(
        name="Maritime News Search",
        description="Use this tool when you need to search information from maritime news",
        func=find_chunk,  # Daha önce vektör indeksinden bilgi çeken zincir
    ),
    Tool.from_function(
        name="Knowledge Graph information",
        description="For when you need to find information about the entities, nodes and relationship in the knowledge graph",
        func=run_cypher,  # Cypher sorgusu çalıştıran tool. 
    )
]

# Her oturum için Neo4j'de mesaj geçmişi saklamak üzere memory tanımı
def get_memory(session_id):
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)


# Ajanın davranış kurallarını anlatan özel ReAct tarzı prompt. 
# Ajan, her zaman bir "tool" kullanmalı ve formatlara uymalı.
agent_prompt = PromptTemplate.from_template("""
You are an expert in maritime knowledge graphs, Neo4j, Cypher, and generative AI.
You are working with a knowledge graph constructed from 100 maritime news articles (PDFs), using LLM-assisted extraction and modeling.

Your job is to provide accurate and comprehensive answers by querying this maritime knowledge graph using appropriate tools.

You must ONLY answer questions related to maritime topics (ships, ports, crew, voyages, accidents, marine zones, AIS data, etc.), Neo4j, Cypher queries, knowledge graphs, or generative AI.

Always use a tool and only use the information provided in the context (i.e., the knowledge graph or tools results). Do NOT use your own knowledge or make assumptions.
    
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


# Yukarıda tanımlanan LLM, araçlar ve prompt ile ReAct ajanı oluşturuluyor
agent = create_react_agent(llm, tools, agent_prompt)

# Bu ajan bir AgentExecutor'a sarılıyor. Hataları yakalayabiliyor ve ayrıntılı log veriyor.
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,
    verbose=True
    )

# Ajan, konuşma geçmişiyle birlikte çalışabilir hale getiriliyor.
chat_agent = RunnableWithMessageHistory(
    agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)



# Arayüzde kullanıcı sorgusu geldiğinde çağrılacak ana fonksiyon.
def generate_response(user_input):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """

    response = chat_agent.invoke(
        {"input": user_input},
        {"configurable": {"session_id": get_session_id()}},  # Oturum kimliği atanıyor
    )
    # print("session_id:", get_session_id())  # Oturum kimliği konsola yazdırılıyor

    return response['output']  # Ajanın oluşturduğu yanıt döndürülüyor
