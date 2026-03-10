import dotenv

dotenv.load_dotenv()
from openai import OpenAI
import asyncio
import base64
import streamlit as st
from agents import Agent, Runner, SQLiteSession, WebSearchTool, FileSearchTool,  ImageGenerationTool, agent

client = OpenAI()

VECTOR_STORE_ID = "vs_69a7a8afe2a48191ab5b382ac50fe789"


if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession("life-coach-history", "life-coach-memory.db")

session = st.session_state["session"]



def update_status(status_container, event):

    status_messages = {
        "response.web_search_call.completed": ("✅ Web search completed.", "complete"),
        "response.web_search_call.in_progress": ("🔍 Starting web search...", "running"),
        "response.web_search_call.searching": ("🔍 Web search in progress...", "running"),
        "response.file_search_call.completed": ("✅ File search completed.", "complete"),
        "response.file_search_call.in_progress": ("📂 Starting file search...", "running"),
        "response.file_search_call.searching": ("📂 File search in progress...", "running"),
        "response.image_generation_call.generating": ("🎨 Drawing image...","running"),
        "response.image_generation_call.in_progress": ("🎨 Drawing image...","running"),        
        "response.completed": (" ", "complete"),
    }

    if event in status_messages:
        label, state = status_messages[event]
        status_container.update(label=label, state=state)


async def paint_history():
    messages = await session.get_items()

    for message in messages:
        if "role" in message:                
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    content = message["content"]
                    if isinstance(content, str):
                        st.write(content)
                    elif isinstance(content, list):
                        for part in content:
                            if "image_url" in part:
                                st.image(part["image_url"])

                else:
                    if message["type"] == "message":
                        st.write(message["content"][0]["text"].replace("$", r"\$"))

        if "type" in message:
            message_type = message["type"]
            if message_type == "web_search_call":  
                with st.chat_message("ai"):
                    st.write("🔍 Web searching ..")
            elif message_type == "file_search_call":  
                with st.chat_message("ai"):
                    st.write("📂 File searching ..")                         
            elif message_type == "image_generation_call":
                image = base64.b64decode(message["result"])
                with st.chat_message("ai"):
                    st.image(image)


asyncio.run(paint_history())

async def run_agent(message):
    agent = Agent(
        name="Life Coach Assistant",
        model="gpt-4o-mini",
        instructions="""
        You are a helpful assistant for life coach.

        You have access to the followign tools:
            - Web Search Tool: Use this when the user asks a questions that isn't in your training data. 
              Use this tool when the users asks about life coaching topics, when you think you don't know the answer, 
              try searching for it in the web first. If answer is not in your training data nor in the files,  
              try searching for it in the web first.
            - File Search Tool: Use this tool when the user asks a question about life coaching related to themselves. Or when they ask questions about specific files.

        Strategy:
        - Use BOTH tools together when appropriate to provide comprehensive answers
        - Use Web Search Tool for current trends, new information, and general life coaching advice
        - Use File Search Tool for personal context and uploaded documents
        - Combine results from both tools to give the best answer
        """,
        tools=[
            WebSearchTool(),
            FileSearchTool(
                vector_store_ids=[VECTOR_STORE_ID],
                max_num_results=3,
            ),
            ImageGenerationTool(
                tool_config={
                    "type": "image_generation",
                    "quality": "high",
                    "output_format": "jpeg",
                    "partial_images": 1,
                }
        ),
        ]
    )

    st.write(f"Using model: {agent.model}") 

    with st.chat_message("ai"):
        status_container = st.status("⏳", expanded=False)
        image_placeholder = st.empty()
        text_placeholder = st.empty()
        response = ""
            
        st.session_state["image_placeholder"] = image_placeholder
        st.session_state["text_placeholder"] = text_placeholder

        stream = Runner.run_streamed(
                    agent, 
                    message, 
                    session = session
                )
        
        async for event in stream.stream_events():
            if event.type == "raw_response_event":

                update_status(status_container, event.data.type)

                if event.data.type == "response.output_text.delta":
                    response += event.data.delta
                    text_placeholder.write(response.replace("$", r"\$") )

                if event.data.type == "response.image_generation_call.partial_image":
                        image = base64.b64decode(event.data.partial_image_b64)
                        image_placeholder.image(image)


    
prompt = st.chat_input("Write a message for your assistant:"
                       ,accept_file=True
                       ,file_type=["pdf","txt","jpg","jpeg","png","md"])

if prompt:

    if "image_placeholder" in st.session_state:
        st.session_state["image_placeholder"].empty()
    if "text_placeholder" in st.session_state:
        st.session_state["text_placeholder"].empty()

    for file in prompt.files:
        if file.type.startswith("text/") or file.type == "application/pdf":
            with st.chat_message("ai"):
                with st.status("⏳ Uploading file...") as status:
                    uploaded_file = client.files.create(
                        file=(file.name, file.getvalue()),
                        purpose="user_data",
                    )
                    status.update(label="⏳ Attaching file ... ")
                    client.vector_stores.files.create(
                        vector_store_id=VECTOR_STORE_ID,
                        file_id=uploaded_file.id,
                    )
                    status.update(label="✅ File uploaded", state="complete")
        elif file.type.startswith("image/"):
            with st.status("⏳ Uploading image...") as status:
                file_bites = file.getvalue()
                base64_data = base64.b64encode(file_bites).decode("utf-8")
                data_uri = f"data:{file.type};base64,{base64_data}"
                asyncio.run(
                    session.add_item(
                        [
                            {"role": "user", 
                             "content": [
                                 {"type": "input_image",
                                  "detail":"auto",
                                  "image_url": data_uri
                                  }
                                ],
                            }
                        ]
                    )
                )
                status.update(label="✅ Image uploaded", state="complete")
            with st.chat_message("user"):
                st.image(data_uri)

    if prompt.text:
        with st.chat_message("user"):
            st.write(prompt.text)
        asyncio.run(run_agent(prompt.text))

with st.sidebar:
    reset = st.button("Reset memory")
    if reset:
        asyncio.run(session.clear_session())
    st.write(asyncio.run(session.get_items()))
             

    