# Gdrive-RAG-agent
![Python](https://img.shields.io/badge/Python-3670A0?style=flat&logo=python&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white) ![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=flat&logo=googlecloud&logoColor=white)

A chat agent with a Google Drive file RAG.

## 🔧 Installation

Clone the repository
```shell
git clone https://github.com/Oscaro92/Gdrive-RAG-agent.git
cd Gdrive-RAG-agent
```

Create a virtual environment
```shell
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

Install dependencies
```shell
pip install -r requirements.txt
```

## ⚙️ Configuration

### Gmail

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com)
2. Enable the Gmail API
3. Create OAuth 2.0 credentials
4. Copy the `credentials.json` file to the project folder
5. Create a `.env` file with the following variables:
```
GOOGLE_ACCOUNT=you@gmail.com
OPENAI_API_KEY=sk-proj-...
```

## 🚀 Usage

Load & save documents from Google drive  
```python
from agent import AgentGDrive

# init agent
agent = AgentGDrive()

# load docs
docs = agent.load('your_path')
# save docs
agent.saveDoc(docs)
```

Run chat bot
```shell
streamlit run chat.py
```

## 📁 Project Structure

```
mail-agent/
├── agent.py            # Agent 
├── chat.py             # Chat
├── gdrive.py           # Google drive tools
├── Chroma              # Database (RAG)
│   └── ...
├── requirements.txt    # Dependencies
├── .env                # Environment variables
└── README.md           # Documentation
```

## 📝 License

This project is licensed under the MIT License.