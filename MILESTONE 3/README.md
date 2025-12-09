# 🔍 AI Research Assistant

A comprehensive academic research assistant powered by **LangGraph**, **Groq AI**, and multiple academic APIs. Features a modern ChatGPT-like web interface for searching academic papers, uploading research documents for analysis, and generating detailed research reports with proper citations.

## ✨ Key Features

### 🌐 **Modern Web Interface**
- ChatGPT-inspired design with dark/light mode
- Chat history with rename, delete, and search
- Compact, aesthetic user interface
- Real-time markdown rendering
- Responsive mobile-friendly layout

### 📚 **Academic Paper Search**
- **Semantic Scholar** integration for computer science papers
- **arXiv** integration for preprints and research papers
- Intelligent paper relevance ranking
- Automatic citation extraction and formatting
- APA-style reference generation

### 📄 **Document Upload & Analysis**
- Upload research papers (PDF, DOCX, TXT)
- Automatic text extraction and processing
- AI-powered summarization
- Topic extraction
- Reference/citation extraction
- Document authenticity verification (genuineness score)
- Ask questions about uploaded documents

### 🤖 **LangGraph Multi-Agent Workflow**
- **Planner Agent**: Breaks down research queries into sub-tasks
- **Searcher Agent**: Searches academic databases and synthesizes findings
- **Writer Agent**: Creates comprehensive, well-cited reports
- **Conversational Memory**: Context-aware follow-up questions

### 💬 **Advanced Chat Features**
- Persistent conversation history
- Multi-turn context awareness
- Markdown-formatted responses
- Copy and download reports
- Auto-rename chats based on content

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key (free tier available)
- Internet connection

### 1. Installation

```bash
cd "MILESTONE 3"
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

**Get your Groq API key**: https://console.groq.com/keys

### 3. Run the Application

```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

---

## 📁 Project Structure

```
MILESTONE 3/
├── app.py                          # Flask web server & API endpoints
├── database.py                     # SQLite database operations
├── document_processor.py           # Document upload & processing
├── academic_orchestrator.py        # LangGraph workflow coordinator
├── workflow.py                     # LangGraph state graph definition
├── models.py                       # Pydantic data models
│
├── planner_agent/
│   ├── agent.py                   # Research planning agent
│   └── prompts.py                 # Planning prompts
│
├── searcher_agent/
│   ├── academic_agent.py          # Academic paper search
│   ├── agent.py                   # Web search agent
│   └── prompts.py                 # Search prompts
│
├── writer_agent/
│   ├── agent.py                   # Report writing agent
│   └── prompts.py                 # Writing prompts
│
├── templates/
│   └── index_v2.html              # Web interface
│
├── static/
│   ├── style_v2.css               # Styling
│   └── script_v2.js               # Frontend logic
│
├── uploads/                        # Uploaded documents (auto-created)
├── research.db                     # SQLite database (auto-created)
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (create this)
└── README.md                      # This file
```

---

## 🎯 How It Works

### Academic Paper Search Mode

When **no documents** are uploaded:

```
User Query
    ↓
┌─────────────────────────┐
│  Planner Agent          │ → Breaks query into 3 research sub-tasks
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│  Academic Searcher      │ → Searches Semantic Scholar & arXiv
│  (runs for each task)   │   Ranks papers by relevance
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│  Writer Agent           │ → Synthesizes findings into report
│                         │   Adds proper citations
└─────────────────────────┘
    ↓
Comprehensive Research Report (Markdown)
```

### Document Analysis Mode

When documents **are uploaded**:

```
User uploads PDF/DOCX
    ↓
┌─────────────────────────┐
│  Document Processor     │ → Extracts text
│                         │   Generates summary
│                         │   Verifies genuineness
└─────────────────────────┘
    ↓
User asks question
    ↓
┌─────────────────────────┐
│  Direct Analysis        │ → Analyzes uploaded document
│  (Groq LLM)             │   Answers from document content
└─────────────────────────┘
    ↓
Document-based Answer
```

---

## 💻 Usage Examples

### Web Interface

1. **Start the server**: `python app.py`
2. **Open browser**: http://localhost:5000
3. **Ask a question**: "What are the latest developments in quantum computing?"
4. **Upload a document**: Click 📎 → Select PDF/DOCX → Ask questions about it
5. **View chat history**: Sidebar shows all your research sessions

### Programmatic Usage

```python
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from academic_orchestrator import AcademicResearchOrchestrator
import os

load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Create orchestrator
orchestrator = AcademicResearchOrchestrator(llm)

# Perform research
report, papers = orchestrator.research(
    "What are transformer models in NLP?",
    verbose=True
)

print(f"Found {len(papers)} papers")
print(report)
```

### Document Processing

```python
from document_processor import DocumentProcessor
from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.3-70b-versatile")
processor = DocumentProcessor(llm)

# Process a document
result = processor.process_document("path/to/paper.pdf")

print(f"Summary: {result['summary']}")
print(f"Word count: {result['word_count']}")
print(f"Genuineness score: {result['genuineness']['score']}/10")
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | **Yes** | Groq API key for LLM inference |

### Supported File Types

- **PDF**: Research papers, articles
- **DOCX**: Microsoft Word documents
- **TXT**: Plain text files

**Maximum file size**: 20MB

---

## 📊 API Endpoints

### Chat Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/new` | POST | Create new chat |
| `/api/chat/list` | GET | Get all chats |
| `/api/chat/<id>` | GET | Get chat details |
| `/api/chat/<id>/rename` | PUT | Rename chat |
| `/api/chat/<id>` | DELETE | Delete chat |

### Research

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/<id>/research` | POST | Perform research query |

### Document Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/<id>/upload` | POST | Upload document |
| `/api/chat/<id>/documents` | GET | List documents |
| `/api/document/<id>` | GET | Get document details |
| `/api/document/<id>` | DELETE | Delete document |

---

## 🌟 Example Queries

### Academic Research
- "What are the latest breakthroughs in quantum computing in 2024?"
- "How is climate change affecting global food security?"
- "What are transformer models in natural language processing?"
- "Recent advances in CRISPR gene editing techniques"

### Document Analysis (after uploading)
- "Summarize this paper in 10 sentences"
- "What are the main topics discussed?"
- "Extract all cited references"
- "Is this research paper genuine?"
- "What methodology was used?"

---

## 🛠️ Tech Stack

### Backend
- **Flask** - Web framework
- **LangGraph** - Multi-agent workflow orchestration
- **LangChain** - LLM framework
- **Groq** - Fast LLM inference (Llama 3.3 70B)
- **SQLite** - Lightweight database
- **PyPDF2** - PDF text extraction
- **python-docx** - DOCX text extraction

### Frontend
- **Vanilla JavaScript** - No frameworks, fast and simple
- **Marked.js** - Markdown rendering
- **CSS Variables** - Dynamic theming

### APIs
- **Semantic Scholar** - Academic paper search
- **arXiv** - Preprint repository

---

## 📝 Features in Detail

### 🎨 UI/UX Highlights
- **Compact design**: Small chatbox, optimized spacing
- **Document upload**: ChatGPT-style paperclip button
- **Theme toggle**: Seamless dark/light mode switching
- **Auto-resize textarea**: Grows with input
- **Markdown rendering**: Rich formatting for reports
- **Copy/Download**: Save reports easily

### 🔬 Research Workflow
1. **Query decomposition**: Breaks complex questions into focused sub-tasks
2. **Parallel search**: Searches multiple academic databases
3. **Relevance ranking**: Prioritizes most relevant papers
4. **Citation extraction**: Automatically formats references
5. **Synthesis**: Combines findings into cohesive narrative

### 📄 Document Intelligence
- **Text extraction**: Multi-format support
- **Smart summarization**: AI-generated overviews
- **Genuineness scoring**: 1-10 authenticity rating
- **Topic analysis**: Automatic subject extraction
- **Reference extraction**: Finds citations in text

---

## 🐛 Troubleshooting

### Server won't start
- Check if port 5000 is available
- Verify `.env` file exists with `GROQ_API_KEY`
- Ensure all dependencies are installed

### "Can't reach this page"
- Make sure server is running (`python app.py`)
- Try http://127.0.0.1:5000 instead of localhost

### Document upload fails
- File must be PDF, DOCX, or TXT
- Maximum file size is 20MB
- Check file isn't corrupted

### No research results
- Verify internet connection
- Check Groq API key is valid
- Academic APIs may be temporarily unavailable

---

## 📚 Dependencies

Key Python packages:
- `flask` - Web server
- `langchain` - LLM framework
- `langchain-groq` - Groq integration
- `langgraph` - Workflow graphs
- `PyPDF2` - PDF processing
- `python-docx` - Word docs
- `python-magic-bin` - File type detection
- `requests` - HTTP client
- `python-dotenv` - Environment variables

See `requirements.txt` for complete list.

---

## 🎓 Educational Purpose

This project was developed for academic coursework to demonstrate:
- Multi-agent AI systems
- LangGraph workflow design
- Academic research automation
- Document processing pipelines
- Web application development
- API integration

---

## 📄 License

Educational project for college coursework. Feel free to learn from and extend the code.

---

## 🙏 Acknowledgments

- **Groq** - Fast LLM inference
- **LangChain** - Framework and tools
- **Semantic Scholar** - Academic paper API
- **arXiv** - Research paper repository

---

**Built with ❤️ for academic research automation**
