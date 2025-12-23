# AI Research Assistant

An intelligent academic research assistant that I built to help automate the tedious parts of literature review and paper analysis. This project combines multi-agent AI systems with a clean ChatGPT-inspired web interface to search academic databases, analyze research papers, and generate comprehensive reports with proper citations.

## What It Does

I've been frustrated with how time-consuming academic research can be - jumping between different paper databases, manually extracting citations, trying to synthesize information from multiple sources. This tool was my attempt to streamline that process.

The system breaks down your research questions into focused sub-tasks, searches multiple academic databases (Semantic Scholar and arXiv), and then synthesizes everything into a well-structured report with proper APA citations. You can also upload research papers (PDFs or Word docs) and ask questions about them directly.

**Key capabilities:**
- Multi-agent research workflow using LangGraph
- Academic paper search across Semantic Scholar and arXiv
- Document upload and intelligent analysis
- Context-aware conversations (remembers what you discussed)
- Modern web UI with dark mode support
- Automatic citation extraction and formatting

## Screenshots

![Web Interface](./MILESTONE%203/static/screenshot.png)
*The main chat interface with dark mode enabled*

## Getting Started

### What You'll Need

- Python 3.8 or newer
- A Groq API key (free tier works fine - grab one at https://console.groq.com/keys)
- Internet connection for searching papers

### Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/vector933/OPEN-DEEP-RESEARCH.git
   cd OPEN-DEEP-RESEARCH
   ```

2. **Navigate to the main application**
   ```bash
   cd "MILESTONE 3"
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   If you run into issues with `python-magic-bin`, you might need to install it separately or skip it (it's used for file type detection).

4. **Set up your environment variables**
   
   Create a `.env` file in the `MILESTONE 3` directory:
   ```env
   GROQ_API_KEY=your_actual_groq_api_key_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   
   Navigate to http://localhost:5000 and start researching!

## How to Use It

### Basic Research Queries

Just type in your research question like you would ask a person:

- "What are the latest developments in transformer models for NLP?"
- "How is quantum computing being applied to drug discovery?"
- "What are the main challenges in climate change modeling?"

The system will automatically break down your query, search relevant papers, and generate a comprehensive report with citations.

### Analyzing Your Own Papers

1. Click the paperclip icon (📎) at the bottom of the chat
2. Upload a PDF, DOCX, or TXT file
3. The system will process it and extract key information
4. You can then ask questions about the document:
   - "Summarize the methodology used"
   - "What are the main findings?"
   - "Extract all the references"

### Managing Conversations

- **New Chat**: Click the "New Chat" button in the sidebar
- **Rename**: Click the edit icon next to any chat
- **Delete**: Click the trash icon
- **Search**: Use the search bar to find past conversations

## Project Structure

```
OPEN-DEEP-RESEARCH/
├── MILESTONE 3/              # Main application directory
│   ├── app.py               # Flask web server & API
│   ├── database.py          # SQLite operations
│   ├── document_processor.py # Document upload & analysis
│   ├── academic_orchestrator.py # LangGraph workflow
│   ├── workflow.py          # State graph definition
│   │
│   ├── planner_agent/       # Query decomposition
│   ├── searcher_agent/      # Paper search & synthesis
│   ├── writer_agent/        # Report generation
│   │
│   ├── templates/           # HTML templates
│   ├── static/             # CSS & JavaScript
│   ├── uploads/            # Uploaded documents (created automatically)
│   │
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Your API keys (create this)
│
├── Architecture_diagram.png
└── README.md              # This file
```

## How It Works

I implemented this using a multi-agent architecture with LangGraph. Here's the basic flow:

### For Research Queries

```
Your Question
    ↓
[Planner Agent] → Breaks it into 3 focused sub-questions
    ↓
[Searcher Agent] → Searches academic databases for each question
    ↓                Ranks papers by relevance
    ↓
[Writer Agent] → Synthesizes everything into one cohesive report
    ↓
Final Report with Citations
```

### For Document Analysis

```
Upload Document (PDF/DOCX/TXT)
    ↓
[Document Processor] → Extracts text
    ↓                   Generates summary
    ↓                   Assesses genuineness
    ↓
Ask Questions
    ↓
[Direct Analysis] → Answers based on document content
```

## Tech Stack

After trying a few different approaches, I settled on:

**Backend:**
- **Flask** - Simple and gets the job done
- **LangGraph** - For orchestrating the multi-agent workflow
- **LangChain** - Makes working with LLMs much easier
- **Groq** - Fast inference with Llama 3.3 70B (seriously fast compared to other options I tried)
- **SQLite** - Lightweight database for chat history

**Frontend:**
- **Vanilla JavaScript** - Kept it simple, no framework overhead
- **Marked.js** - For rendering markdown responses
- **CSS Variables** - Makes theme switching easy

**APIs:**
- **Semantic Scholar** - Great for computer science papers
- **arXiv** - Preprint repository with tons of research

## API Endpoints

If you want to integrate this into your own project:

### Chat Management
- `POST /api/chat/new` - Create new chat
- `GET /api/chat/list` - Get all chats
- `GET /api/chat/<id>` - Get specific chat
- `PUT /api/chat/<id>/rename` - Rename chat
- `DELETE /api/chat/<id>` - Delete chat

### Research
- `POST /api/chat/<id>/research` - Submit research query

### Documents
- `POST /api/chat/<id>/upload` - Upload document
- `GET /api/chat/<id>/documents` - List documents
- `GET /api/document/<id>` - Get document details
- `DELETE /api/document/<id>` - Delete document

## Troubleshooting

**Server won't start?**
- Make sure port 5000 isn't already in use
- Check that your `.env` file exists and has a valid `GROQ_API_KEY`
- Verify all dependencies installed correctly

**Can't reach the page?**
- Confirm the server is actually running (you should see Flask output in terminal)
- Try http://127.0.0.1:5000 instead of localhost
- Check your firewall isn't blocking port 5000

**Document upload fails?**
- Files must be PDF, DOCX, or TXT format
- Maximum size is 20MB
- Make sure the file isn't corrupted

**No search results?**
- Verify your internet connection
- Double-check your Groq API key is valid
- The academic APIs might be temporarily down (happens occasionally)

## What I Learned

Building this taught me a lot about:
- Designing multi-agent AI systems that actually work reliably
- The challenges of working with different academic APIs (they all have quirks)
- Creating intuitive chat interfaces
- Managing conversation context and history
- Document processing at scale

The trickiest part was getting the agent coordination right - making sure the planner generates good sub-questions, the searcher finds relevant papers, and the writer synthesizes everything coherently.

## Future Improvements

Some ideas I'm considering:
- Add more academic databases (PubMed, Google Scholar)
- Implement collaborative filtering for better paper recommendations
- Add export to BibTeX/EndNote
- Support for uploading multiple documents at once
- Add visualization of citation networks
- Integration with reference managers

## Contributing

This started as a college project, but I'm open to contributions! If you find bugs or have ideas for improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please keep the code style consistent and add comments where things might be unclear.

## License

MIT License - feel free to use this for your own research or build upon it for your projects.

## Acknowledgments

Huge thanks to:
- **Groq** for providing fast, free LLM inference
- **LangChain team** for the excellent framework and documentation
- **Semantic Scholar** for the academic paper API
- **arXiv** for making research accessible

This project was developed as part of my coursework to explore multi-agent AI systems and their applications in academic research automation.

---

**Questions or issues?** Feel free to open an issue on GitHub or reach out!

Built with ☕ and probably too many late nights debugging API calls.
