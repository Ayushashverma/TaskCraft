# TaskCraft 🧠

**AI-powered Task & Trip Planner**  
Turn your goals into actionable, step-by-step plans enriched with weather information and related web resources.

---

## 🌟 Features

- Enter a natural language goal (e.g., "Plan a 3-day trip to Jaipur").
- AI generates a **step-by-step day-by-day plan**.
- Weather information for specified cities (powered by OpenWeather API).
- Related resources & links from web search (powered by SerpAPI).
- Save all generated plans in a local **SQLite database**.
- View previous plans in a clean, expandable interface.
- Lightweight and interactive **Streamlit web interface**.

---

## 🛠️ Tech Stack

- **Python**  
- **Streamlit** for UI  
- **SQLite** for plan storage  
- **Groq API / HuggingFace API** for AI plan generation  
- **OpenWeather API** for weather data  
- **SerpAPI** for web search enrichment  

---

## 🚀 Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/Ayushashverma/TaskCraft.git
cd TaskCraft
Create a virtual environment (optional but recommended)

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate


Install dependencies

pip install -r requirements.txt


Create a .env file in the project root with your API keys:

OPENWEATHER_KEY=your_openweather_api_key
SERPAPI_KEY=your_serpapi_key
GROQ_API_KEY=your_groq_api_key
HF_KEY=your_huggingface_api_key
HF_MODEL=gpt2
HF_MODE=api


Run the Streamlit app

streamlit run app.py

🎯 How It Works

User enters a goal in the input field.

AI generates a detailed plan using the configured LLM (Groq or HuggingFace).

Weather API fetches current weather for the city.

Web search API fetches relevant links/resources for the goal.

Full plan is saved in SQLite and displayed on the interface.

Previous plans can be browsed in the history section.

📂 Project Structure
TaskCraft/
│
├─ app.py               # Main Streamlit app
├─ database.py          # SQLite database handling
├─ external_apis.py     # Weather & Web search APIs
├─ planner.py           # AI plan generation & enrichment
├─ plans.db             # Local SQLite database (ignored in Git)
├─ .env                 # API keys (ignored in Git)
├─ requirements.txt     # Python dependencies
├─ README.md            # Project documentation
└─ .gitignore

🧪 Example Goals

"Plan a 2-day vegetarian food tour in Hyderabad"

"Organize a 5-step daily study routine for learning Python"

"Create a weekend plan in Vizag with beach, hiking, and seafood"

⚡ Notes

.env contains your API keys and should never be pushed to GitHub.

The database plans.db stores all generated plans locally.

Streamlit UI is responsive and allows interactive exploration of past plans.

📹 Demo

Enter a goal → AI generates plan → View plan in UI → Browse history of plans.

(You can record a 2-3 min screen demo for submission)

🔗 References

Streamlit Docs

OpenWeather API

SerpAPI

Groq API

HuggingFace API

📝 License

MIT License


---

