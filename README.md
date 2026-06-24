# TheResearcher 🔬🤖

Welcome to **TheResearcher**! This is a powerful, multi-agent AI application designed to act as your personal research assistant. Give it a topic, and a dedicated team of AI agents will autonomously gather facts, write a comprehensive report, and cite their sources correctly.

---

## 🌟 How It Works

Under the hood, TheResearcher uses **LangGraph** to coordinate four specialized AI agents powered by **Google Gemini**:

1. **👨‍💼 Supervisor Agent**: The boss. It reads your topic and routes tasks dynamically to the other agents based on what's needed.
2. **🕵️‍♂️ Researcher Agent**: The data gatherer. It uses Tavily to search the web, extracting key facts and keeping track of the exact URLs.
3. **✍️ Writer Agent**: The author. It turns the raw facts into a beautiful, structured Markdown report with proper inline citations (like `[1]`).
4. **🧐 Critic Agent**: The reviewer. It fact-checks the draft against the citations to ensure accuracy, sending it back for revisions if necessary.

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, LangGraph, LangChain, Google Gemini, Tavily Search
- **Frontend**: React, Vite, Plain CSS (modern and clean!)
- **Environment**: Managed using [uv](https://github.com/astral-sh/uv) for blazing fast dependency resolution.

---

## 🚀 Getting Started

Follow these steps to get TheResearcher running locally on your machine.

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- A **Google Gemini API Key** (Get one [here](https://aistudio.google.com/))
- A **Tavily API Key** (Get one [here](https://tavily.com/))
- **uv** (Install it [here](https://github.com/astral-sh/uv))

### 1. Clone the repository
```bash
git clone https://github.com/shikhar0312/TheReseacher.git
cd TheReseacher
```

### 2. Set up the Backend
Navigate to the backend directory, install the dependencies with `uv`, and configure your environment variables.

```bash
cd backend

# Install dependencies using uv
uv sync

# Set up your environment variables
cp .env.example .env
```
👉 *Open the `.env` file and paste in your `GOOGLE_API_KEY` and `TAVILY_API_KEY`.*

```bash
# Start the backend server
uv run python -m app.main
```
*The API will be available at `http://localhost:8000`.*

### 3. Set up the Frontend
Open a new terminal window, navigate to the frontend directory, and start the React app.

```bash
cd frontend

# Install Node modules
npm install

# Start the Vite development server
npm run dev
```
*The frontend will be available at `http://localhost:5173`.*

---

## 💡 Usage

1. Open `http://localhost:5173` in your browser.
2. Type in a research topic (e.g., *"Latest breakthroughs in solid-state batteries"* or *"History of the Roman Empire"*).
3. Watch the Live Agent Activity Log as the Supervisor coordinates the team.
4. Read the final report with clickable inline citations that jump straight to the source links!

---

## 📄 License
This project is open-source and available under the MIT License.
