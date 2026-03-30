import streamlit as st
from groq import Groq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper, DuckDuckGoSearchAPIWrapper

# --- 1. CONFIG & API KEYS ---

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

st.set_page_config(page_title="Sports Pro Bot", page_icon="🏆", layout="centered")


# --- 2. CUSTOM CSS STYLING ---

st.title(" Sports Pro Bot")
st.markdown("---")


# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Settings ⚙️")
    if st.button("Clear Chat History 🗑️"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.info("I am a specialized AI focused only on sports news, scores, and history.")

# --- 4. INITIALIZE TOOLS & AI ---
client = Groq(api_key=GROQ_API_KEY)
search_tool = DuckDuckGoSearchRun()
wiki_wrapper = WikipediaAPIWrapper()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. STRICT AI SPORTS GATEKEEPER ---
def is_sports_strictly(query):
    sports_keywords = [
        "sport", "match", "team", "player", "score", "goal",
        "cricket", "football", "soccer", "nba", "fifa",
        "world cup", "tennis", "olympics", "athlete"
    ]
    
    query_lower = query.lower()
    
   
    if any(word in query_lower for word in sports_keywords):
        return True
    
  
    try:
        check = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Answer ONLY TRUE or FALSE. Is this about sports?"},
                {"role": "user", "content": query}
            ],
            model="llama-3.1-8b-instant",
        )
        return "TRUE" in check.choices[0].message.content.upper()
    except:
        return True

# --- 6. THE AI REWRITER ENGINE ---
def generate_ai_answer(user_query, raw_data):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert sports commentator. Rewrite search results into a clean, friendly summary. Do NOT show URLs or raw dates."},
                {"role": "user", "content": f"Search Results: {raw_data}\n\nQuestion: {user_query}"}
            ],
            model="llama-3.1-8b-instant", 
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

# --- 7. MAIN LOGIC FLOW ---
def get_final_answer(user_input):
    if not is_sports_strictly(user_input):
        return "🚫 I am a sports-only assistant. Please ask me about matches, athletes, or sports news!"
    
    if any(word in user_input.lower() for word in ["who is", "history", "biography"]):
        try:
            raw_info = wiki_wrapper.run(user_input)
        except:
            raw_info = "Historical data not found."
    else:
        try:
            raw_info = search_tool.run(f"latest sports news: {user_input}")
        except:
            raw_info = "Could not find live updates right now."
    
    return generate_ai_answer(user_input, raw_info)

# --- 8. UI CHAT INTERFACE ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about any sport..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing sports data..."):
            response = get_final_answer(prompt)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
