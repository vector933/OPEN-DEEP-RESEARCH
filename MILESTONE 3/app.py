"""
Enhanced Web Application with Chat History and Academic Search
===============================================================
Flask web server with ChatGPT-like features: chat history, rename, delete, theme toggle.
"""

from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from academic_orchestrator import AcademicResearchOrchestrator
import database as db
import secrets
import markdown
from datetime import datetime
from paper_fetcher import PaperFetcher

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configuration for session continuity
CONTEXT_WINDOW_SIZE = int(os.getenv("CONTEXT_WINDOW_SIZE", "5"))  # Number of previous messages to include as context

# Initialize the LLM and orchestrator
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    groq_api_key=groq_api_key
)

# Use Academic Research Orchestrator
orchestrator = AcademicResearchOrchestrator(llm)

# Initialize Paper Fetcher for URL handling
paper_fetcher = PaperFetcher()


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index_v2.html')


# ============================================================================
# CHAT MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/chat/new', methods=['POST'])
def create_new_chat():
    """Create a new chat session."""
    try:
        data = request.get_json() or {}
        title = data.get('title', 'New Research')
        
        chat_id = db.create_chat(title)
        
        return jsonify({
            'success': True,
            'chat_id': chat_id,
            'title': title
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/list', methods=['GET'])
def list_chats():
    """Get all chat sessions."""
    try:
        chats = db.get_all_chats()
        return jsonify({
            'success': True,
            'chats': chats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/<int:chat_id>', methods=['GET'])
def get_chat(chat_id):
    """Get a specific chat session."""
    try:
        chat = db.get_chat(chat_id)
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        messages = db.get_chat_messages(chat_id)
        
        return jsonify({
            'success': True,
            'chat': chat,
            'messages': messages
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/<int:chat_id>/rename', methods=['PUT'])
def rename_chat(chat_id):
    """Rename a chat session."""
    try:
        data = request.get_json()
        new_title = data.get('title', '').strip()
        
        if not new_title:
            return jsonify({'error': 'Title cannot be empty'}), 400
        
        success = db.rename_chat(chat_id, new_title)
        
        if not success:
            return jsonify({'error': 'Chat not found'}), 404
        
        return jsonify({
            'success': True,
            'title': new_title
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete a chat session."""
    try:
        success = db.delete_chat(chat_id)
        
        if not success:
            return jsonify({'error': 'Chat not found'}), 404
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/<int:chat_id>/context', methods=['GET'])
def get_conversation_context(chat_id):
    """Get formatted conversation context for a chat session."""
    try:
        # Verify chat exists
        chat = db.get_chat(chat_id)
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        # Get messages
        messages = db.get_chat_messages(chat_id)
        
        # Format the last N messages that would be used as context
        context_messages = messages[-CONTEXT_WINDOW_SIZE:]
        
        # Create formatted context
        formatted_context = []
        for i, msg in enumerate(context_messages, 1):
            formatted_context.append({
                'index': i,
                'query': msg['query'],
                'report_preview': msg['report'][:200] + '...' if len(msg['report']) > 200 else msg['report'],
                'created_at': msg.get('created_at', ''),
                'message_id': msg.get('id')
            })
        
        return jsonify({
            'success': True,
            'chat_id': chat_id,
            'context_window_size': CONTEXT_WINDOW_SIZE,
            'total_messages': len(messages),
            'context_messages_count': len(context_messages),
            'context': formatted_context,
            'will_use_context': len(context_messages) > 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# RESEARCH ENDPOINT
# ============================================================================

@app.route('/api/chat/<int:chat_id>/research', methods=['POST'])
def research_in_chat(chat_id):
    """Perform research and save to chat."""
    try:
        # Verify chat exists
        chat = db.get_chat(chat_id)
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({'error': 'Please enter a research question'}), 400
        
        # Validate query is meaningful (at least 3 words or 10 characters)
        words = user_query.split()
        if len(words) < 3 and len(user_query) < 10:
            return jsonify({
                'error': 'Please enter a more detailed research question. For example: "What is quantum computing?" or "How does climate change affect food security?"'
            }), 400
        
        # Check if query contains only gibberish (no vowels or too many repeated characters)
        vowels = set('aeiouAEIOU')
        has_vowels = any(c in vowels for c in user_query)
        
        # Check for excessive character repetition (like "aaaaaaa" or "iubhbu")
        if len(set(user_query.replace(' ', ''))) < 3:
            return jsonify({
                'error': 'Please enter a valid research question with meaningful words.'
            }), 400
        
        if not has_vowels and len(user_query) > 5:
            return jsonify({
                'error': 'Please enter a valid research question. Your input appears to be random characters.'
            }), 400
        
        # ============================================================
        # CHECK FOR RESEARCH PAPER URL
        # ============================================================
        if paper_fetcher.detect_url(user_query):
            print("🔗 Research paper URL detected!")
            
            try:
                # Extract URL and any accompanying question
                url, question = paper_fetcher.extract_url_and_question(user_query)
                
                if not url:
                    return jsonify({'error': 'Could not extract URL from query'}), 400
                
                # Fetch paper information
                print(f"📥 Fetching paper from: {url}")
                paper_info = paper_fetcher.fetch_paper_info(url)
                
                # Determine if this is a summary request or a specific question
                is_summary_request = question is None or len(question) < 10
                
                if is_summary_request:
                    # Generate detailed summary
                    print("📝 Generating detailed paper summary...")
                    
                    summary_prompt = f"""You are a research paper summarizer. Provide a comprehensive, well-structured summary of this research paper.

**Paper Information:**
- Title: {paper_info['title']}
- Authors: {paper_info['authors']}
- Source: {paper_info['source']}
{f"- Published: {paper_info.get('published', 'Unknown')}" if 'published' in paper_info else ""}
{f"- ArXiv ID: {paper_info.get('arxiv_id', '')}" if 'arxiv_id' in paper_info else ""}
{f"- DOI: {paper_info.get('doi', '')}" if 'doi' in paper_info else ""}

**Abstract:**
{paper_info['abstract']}

**Instructions:**
Create a comprehensive summary with the following sections:

1. **Overview**: Brief introduction to the paper
2. **Research Problem**: What problem does this paper address?
3. **Key Contributions**: Main contributions and findings
4. **Methodology**: Research approach and methods used (infer from abstract if needed)
5. **Significance**: Why is this research important?
6. **Access**: Where to find the full paper

Format your response in clear, professional markdown. Be thorough but concise."""

                    response = llm.invoke(summary_prompt)
                    final_report = response.content.strip()
                    
                    # Add paper metadata at the end
                    final_report += f"\n\n## Paper Details\n\n"
                    final_report += f"- **Title**: {paper_info['title']}\n"
                    final_report += f"- **Authors**: {paper_info['authors']}\n"
                    if 'published' in paper_info:
                        final_report += f"- **Published**: {paper_info['published']}\n"
                    if 'arxiv_id' in paper_info:
                        final_report += f"- **ArXiv ID**: {paper_info['arxiv_id']}\n"
                    if 'doi' in paper_info:
                        final_report += f"- **DOI**: {paper_info['doi']}\n"
                    if 'citations' in paper_info:
                        final_report += f"- **Citations**: {paper_info['citations']}\n"
                    final_report += f"- **URL**: {paper_info['url']}\n"
                    if paper_info.get('pdf_url'):
                        final_report += f"- **PDF**: {paper_info['pdf_url']}\n"
                    
                else:
                    # Answer specific question about the paper
                    print(f"❓ Answering question about paper: {question}")
                    
                    qa_prompt = f"""You are answering a specific question about a research paper.

**Paper Information:**
- Title: {paper_info['title']}
- Authors: {paper_info['authors']}
- Source: {paper_info['source']}

**Abstract:**
{paper_info['abstract']}

**User Question:**
{question}

**Instructions:**
- Answer the question based on the paper information provided
- If the abstract doesn't contain enough information to fully answer, acknowledge this and provide what you can infer
- Be specific and cite relevant parts of the abstract
- If you cannot answer the question from the available information, say so clearly
- Format your response in clear markdown

**Response:**"""

                    response = llm.invoke(qa_prompt)
                    final_report = response.content.strip()
                    
                    # Add paper reference
                    final_report += f"\n\n---\n\n**Paper Reference:**\n"
                    final_report += f"- **Title**: {paper_info['title']}\n"
                    final_report += f"- **Authors**: {paper_info['authors']}\n"
                    final_report += f"- **URL**: {paper_info['url']}\n"
                
                # Save to database
                db.add_message(chat_id, user_query, final_report)
                
                # Auto-rename chat if it's still "New Research"
                if chat['title'] == 'New Research':
                    # Use paper title (truncated)
                    new_title = paper_info['title'][:60]
                    if len(paper_info['title']) > 60:
                        new_title += '...'
                    db.rename_chat(chat_id, new_title)
                
                return jsonify({
                    'success': True,
                    'query': user_query,
                    'report': final_report,
                    'source': 'research_paper_url',
                    'paper_info': {
                        'title': paper_info['title'],
                        'authors': paper_info['authors'],
                        'url': paper_info['url']
                    },
                    'was_summary': is_summary_request
                })
                
            except ValueError as e:
                # URL detection succeeded but fetching failed
                print(f"⚠️ Failed to fetch paper: {str(e)}")
                return jsonify({
                    'error': f'Could not fetch paper information: {str(e)}',
                    'suggestion': 'Please check the URL or try searching for the paper by title instead.'
                }), 400
            except Exception as e:
                print(f"❌ Error processing paper URL: {str(e)}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    'error': f'Error processing paper URL: {str(e)}'
                }), 500
        
        # ============================================================
        # CHECK FOR UPLOADED DOCUMENTS FIRST
        # ============================================================
        documents = db.get_chat_documents(chat_id)
        
        if documents and len(documents) > 0:
            # User has uploaded documents - analyze them instead of searching papers
            print(f"📄 Found {len(documents)} uploaded document(s). Analyzing document content...")
            
            # Get the most recent document
            doc = documents[0]  # Most recent upload
            doc_details = db.get_document(doc['id'])
            
            if doc_details and doc_details.get('extracted_text'):
                # Create document-focused response
                doc_text = doc_details['extracted_text']
                doc_summary = doc_details.get('summary', 'No summary available')
                genuineness_score = doc_details.get('genuineness_score', 0)
                genuineness_analysis = doc_details.get('genuineness_analysis', '')
                
                # Limit text to avoid token limits (use first 6000 chars)
                text_preview = doc_text[:6000] if len(doc_text) > 6000 else doc_text
                
                # Generate document-based response
                prompt = f"""You are analyzing an uploaded research document. Answer the user's question based ONLY on the document content provided.

**Document Information:**
- Filename: {doc['filename']}
- Word Count: {doc_details.get('word_count', 'Unknown')}
- Genuineness Score: {genuineness_score}/10

**Document Summary:**
{doc_summary}

**Document Content:**
{text_preview}

**User Question:**
{user_query}

**Instructions:**
- Answer the question based ONLY on the document content above
- If asking for a summary, provide a clear, structured summary
- If asking about topics, extract and list the main topics
- If asking about references, extract any citations or references mentioned
- If asking about genuineness, provide the authenticity analysis
- If the question cannot be answered from the document, say so clearly
- Format your response in markdown with clear headings
- Be specific and cite relevant parts of the document

**Response:**"""

                try:
                    response = llm.invoke(prompt)
                    final_report = response.content.strip()
                    
                    # Add genuineness information if relevant to query
                    if any(keyword in user_query.lower() for keyword in ['genuine', 'authentic', 'real', 'fake', 'trust', 'quality']):
                        final_report += f"\n\n## Document Authenticity Analysis\n\n{genuineness_analysis}"
                    
                    # Save to database
                    db.add_message(chat_id, user_query, final_report)
                    
                    # Auto-rename chat if it's still "New Research"
                    if chat['title'] == 'New Research':
                        new_title = f"Analysis: {doc['filename'][:30]}"
                        db.rename_chat(chat_id, new_title)
                    
                    return jsonify({
                        'success': True,
                        'query': user_query,
                        'report': final_report,
                        'source': 'uploaded_document',
                        'document_used': doc['filename'],
                        'genuineness_score': genuineness_score
                    })
                    
                except Exception as e:
                    print(f"Error analyzing document: {str(e)}")
                    return jsonify({'error': f'Failed to analyze document: {str(e)}'}), 500
        
        # ============================================================
        # NO DOCUMENTS - Use normal academic paper search
        # ============================================================
        print("🔍 No documents found. Searching academic papers...")
        
        # Get conversation history for context
        messages = db.get_chat_messages(chat_id)
        
        # Format history for agents (use configurable context window)
        conversation_history = [
            {
                'query': msg['query'],
                'report': msg['report'],
                'created_at': msg.get('created_at', '')
            }
            for msg in messages[-CONTEXT_WINDOW_SIZE:]  # Use configurable window size
        ]
        
        # Log context usage for debugging
        if conversation_history:
            print(f"📚 Using conversation context: {len(conversation_history)} previous message(s)")
            print(f"   Last query in context: '{conversation_history[-1]['query'][:50]}...'")
        else:
            print("📝 Starting new conversation (no previous context)")
        
        # Perform research with academic papers AND conversation context
        final_report, papers = orchestrator.research(
            user_query, 
            conversation_history=conversation_history,
            verbose=False
        )
        
        # Save to database
        db.add_message(chat_id, user_query, final_report)
        
        # Auto-rename chat if it's still "New Research"
        if chat['title'] == 'New Research':
            # Use first few words of query as title
            new_title = ' '.join(user_query.split()[:6])
            if len(user_query.split()) > 6:
                new_title += '...'
            db.rename_chat(chat_id, new_title)
        
        # Convert markdown to HTML
        html_report = markdown.markdown(
            final_report,
            extensions=['tables', 'fenced_code', 'nl2br']
        )
        
        # Estimate context token count (rough estimate: ~4 chars per token)
        context_text = ""
        for msg in conversation_history:
            context_text += msg['query'] + " " + msg['report']
        estimated_context_tokens = len(context_text) // 4
        
        return jsonify({
            'success': True,
            'query': user_query,
            'report': final_report,
            'html_report': html_report,
            'paper_count': len(papers),
            'source': 'academic_papers',
            'conversation_context_used': len(conversation_history) > 0,
            'context_metadata': {
                'messages_used': len(conversation_history),
                'total_messages_in_chat': len(messages),
                'context_window_size': CONTEXT_WINDOW_SIZE,
                'estimated_context_tokens': estimated_context_tokens
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500



# ============================================================================
# DOCUMENT UPLOAD ENDPOINTS
# ============================================================================

from werkzeug.utils import secure_filename
from document_processor import DocumentProcessor

# Initialize document processor
doc_processor = DocumentProcessor(llm)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/chat/<int:chat_id>/upload', methods=['POST'])
def upload_document(chat_id):
    """Upload and process a document."""
    try:
        # Verify chat exists
        chat = db.get_chat(chat_id)
        if not chat:
            return jsonify({'error': 'Chat not found'}), 404
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload PDF, TXT, or DOCX files.'}), 400
        
        # Secure the filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            os.remove(file_path)
            return jsonify({'error': 'File too large. Maximum size is 20MB.'}), 400
        
        # Process document
        try:
            result = doc_processor.process_document(file_path)
            
            # Save to database
            doc_id = db.add_document(
                chat_id=chat_id,
                filename=filename,
                file_path=file_path,
                file_type=file.content_type or 'application/octet-stream',
                file_size=file_size,
                extracted_text=result['text'],
                summary=result['summary'],
                genuineness_score=result['genuineness']['score'],
                genuineness_analysis=result['genuineness']['analysis'],
                word_count=result['word_count']
            )
            
            return jsonify({
                'success': True,
                'document': {
                    'id': doc_id,
                    'filename': filename,
                    'file_size': file_size,
                    'word_count': result['word_count'],
                    'summary': result['summary'],
                    'genuineness_score': result['genuineness']['score'],
                    'genuineness_analysis': result['genuineness']['analysis'],
                    'is_genuine': result['genuineness']['is_genuine']
                }
            })
            
        except ValueError as e:
            # Remove file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/api/chat/<int:chat_id>/documents', methods=['GET'])
def list_documents(chat_id):
    """Get all documents for a chat."""
    try:
        documents = db.get_chat_documents(chat_id)
        return jsonify({
            'success': True,
            'documents': documents
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/document/<int:doc_id>', methods=['GET'])
def get_document_details(doc_id):
    """Get full document details including text."""
    try:
        document = db.get_document(doc_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({
            'success': True,
            'document': document
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/document/<int:doc_id>', methods=['DELETE'])
def delete_document_endpoint(doc_id):
    """Delete a document."""
    try:
        success = db.delete_document(doc_id)
        if not success:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'search_type': 'academic_papers',
        'workflow': 'langgraph',
        'features': ['chat_history', 'theme_toggle', 'conversation_memory', 'langgraph_workflow']
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Enhanced Research System Starting...")
    print("="*60)
    print("\n📍 Open your browser: http://localhost:5000")
    print("\n✨ Features:")
    print("   ✅ Academic paper search (Semantic Scholar + arXiv)")
    print("   ✅ LangGraph workflow coordination")
    print("   ✅ Conversational memory (context-aware)")
    print("   ✅ Chat history with sidebar")
    print("   ✅ New/Rename/Delete chats")
    print("   ✅ Light/Dark mode toggle")
    print("   ✅ Proper citations & references")
    print("\n💡 Press Ctrl+C to stop\n")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
