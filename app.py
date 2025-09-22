import os
import requests
import sqlite3
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# ----------------------------
# Page Configuration
# ----------------------------
st.set_page_config(
    page_title="AI Task Planner",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ----------------------------
# Initialize Groq client
# ----------------------------
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None

# ----------------------------
# Database setup
# ----------------------------
def init_db():
    conn = sqlite3.connect("plans.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS plans
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  goal TEXT,
                  city TEXT,
                  plan TEXT,
                  created_at TEXT)''')
    conn.commit()
    conn.close()

def save_plan(goal, city, plan):
    conn = sqlite3.connect("plans.db")
    c = conn.cursor()
    c.execute("INSERT INTO plans (goal, city, plan, created_at) VALUES (?, ?, ?, ?)",
              (goal, city, plan, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

def load_plans():
    conn = sqlite3.connect("plans.db")
    c = conn.cursor()
    c.execute("SELECT goal, city, plan, created_at FROM plans ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

# ----------------------------
# External API calls
# ----------------------------
def get_weather(city: str):
    if not city or not OPENWEATHER_KEY:
        return "No city provided or weather API key missing."
    try:
        city_clean = city.strip()
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city_clean}&appid={OPENWEATHER_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"{desc}, {temp}°C"
    except Exception as e:
        return f"Weather error: {e}"

def get_search_info(query: str):
    if not SERPAPI_KEY:
        return "Search API key not configured."
    try:
        url = f"https://serpapi.com/search.json?q={query}&api_key={SERPAPI_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        links = []
        if "organic_results" in data:
            for item in data["organic_results"][:3]:
                title = item.get('title', 'No title')
                link = item.get('link', 'No link')
                links.append(f"- {title}: {link}")
        return "\n".join(links) if links else "No related links found."
    except Exception as e:
        return f"Search error: {e}"

# ----------------------------
# AI Plan generation
# ----------------------------
def generate_plan(prompt: str):
    if not groq_client:
        return "[Configuration Error] GROQ_API_KEY not found. Please check your .env file."
    
    models_to_try = [
        "llama3-8b-8192",
        "llama3-70b-8192", 
        "mixtral-8x7b-32768",
        "gemma-7b-it",
        "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile"
    ]
    
    for model in models_to_try:
        try:
            response = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that creates detailed, actionable plans. Be specific and practical in your recommendations."},
                    {"role": "user", "content": prompt}
                ],
                model=model,
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            if "401" in str(e) or "invalid_api_key" in str(e).lower():
                return f"[API Key Error] Invalid Groq API key. Please visit https://console.groq.com/keys to get a valid key."
            continue
    
    return "[Error] Unable to generate plan. Please check your API configuration."

# ----------------------------
# Streamlit UI
# ----------------------------
def main():
    # Header
    st.title("🧠 AI Task Planner")
    st.markdown("*Transform your goals into actionable plans with AI assistance*")
    
    st.divider()
    
    # Input Section
    st.header("📝 Create Your Plan")
    
    goal = st.text_input(
        "What's your goal?", 
        placeholder="e.g., Plan a 3-day trip to Paris"
    )
    
    # Two columns for city and detail level
    col1, col2 = st.columns([2, 1])
    
    with col1:
        city = st.text_input(
            "City (optional)", 
            placeholder="e.g., Paris"
        )
    
    with col2:
        max_tokens = st.selectbox(
            "Detail Level",
            options=[200, 300, 400, 500],
            index=1,
            format_func=lambda x: {200: "Brief", 300: "Detailed", 400: "Comprehensive", 500: "Very Detailed"}[x]
        )
    
    # Generate button
    if st.button("🚀 Generate Plan", type="primary", use_container_width=True):
        if not goal:
            st.error("Please enter a goal to generate your plan.")
        else:
            with st.spinner("Creating your personalized plan..."):
                # Create prompt
                prompt = f"""Create a detailed, step-by-step plan for: {goal}

Please provide:
1. Clear actionable steps
2. Timeline estimates where relevant
3. Important considerations
4. Resources needed

Make it practical and easy to follow."""

                # Generate plan
                plan_text = generate_plan(prompt)
                
                # Get additional info
                weather = get_weather(city.strip()) if city.strip() else ""
                search_info = get_search_info(goal) if goal else ""

                # Save to database
                full_plan = f"{plan_text}"
                if weather and "error" not in weather.lower():
                    full_plan += f"\n\n**Weather Info:** {weather}"
                if search_info and "error" not in search_info.lower():
                    full_plan += f"\n\n**Related Resources:**\n{search_info}"
                
                save_plan(goal, city.strip() if city else "", full_plan)

                # Display success message
                st.success("✅ Plan generated successfully!")
                
                # Display the plan
                st.divider()
                st.header("🎯 Your Generated Plan")
                st.markdown(plan_text)
                
                # Show additional info if available
                if weather and "error" not in weather.lower():
                    with st.expander("🌤️ Weather Information"):
                        st.info(weather)
                
                if search_info and "error" not in search_info.lower():
                    with st.expander("🔗 Related Resources"):
                        st.info(search_info)

    # Previous Plans Section
    st.divider()
    plans = load_plans()
    
    if plans:
        st.header("📚 Previous Plans")
        
        # Show recent plans (limit to 10 for performance)
        for i, (g, c, p, t) in enumerate(plans[:10]):
            # Format timestamp
            try:
                dt = datetime.fromisoformat(t)
                formatted_time = dt.strftime("%B %d, %Y at %I:%M %p")
            except:
                formatted_time = "Recently"
            
            # Create expander for each plan
            location_text = f" • 📍 {c}" if c else ""
            with st.expander(f"**{g}** • 📅 {formatted_time}{location_text}"):
                # Split plan content to show only the main plan (not additional info)
                main_plan = p.split('\n\n**Weather Info:**')[0].split('\n\n**Related Resources:**')[0]
                st.markdown(main_plan)
    else:
        st.info("No previous plans yet. Generate your first plan above!")

    # Footer
    st.divider()
    st.markdown("*Powered by AI • Built with Streamlit*")

# ----------------------------
# Run app
# ----------------------------
if __name__ == "__main__":
    init_db()
    main()