"""
Database Layer for Chat History Management
===========================================
SQLite database for storing chat sessions and messages.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

DB_PATH = "research_chats.db"


def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create chats table with local time
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT (DATETIME('now', 'localtime')),
            updated_at TIMESTAMP DEFAULT (DATETIME('now', 'localtime'))
        )
    """)
    
    # Create messages table with local time
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            query TEXT NOT NULL,
            report TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT (DATETIME('now', 'localtime')),
            FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
        )
    """)
    
    # Create documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            extracted_text TEXT,
            summary TEXT,
            genuineness_score INTEGER,
            genuineness_analysis TEXT,
            word_count INTEGER,
            uploaded_at TIMESTAMP DEFAULT (DATETIME('now', 'localtime')),
            FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()


def create_chat(title: str = "New Research") -> int:
    """Create a new chat session."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO chats (title) VALUES (?)",
        (title,)
    )
    
    chat_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return chat_id


def get_all_chats() -> List[Dict]:
    """Get all chat sessions."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, created_at, updated_at 
        FROM chats 
        ORDER BY updated_at DESC
    """)
    
    chats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return chats


def get_chat(chat_id: int) -> Optional[Dict]:
    """Get a specific chat session."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, title, created_at, updated_at FROM chats WHERE id = ?",
        (chat_id,)
    )
    
    row = cursor.fetchone()
    chat = dict(row) if row else None
    conn.close()
    
    return chat


def rename_chat(chat_id: int, new_title: str) -> bool:
    """Rename a chat session."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE chats SET title = ?, updated_at = DATETIME('now', 'localtime') WHERE id = ?",
        (new_title, chat_id)
    )
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success


def delete_chat(chat_id: int) -> bool:
    """Delete a chat session and all its messages."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return success


def add_message(chat_id: int, query: str, report: str) -> int:
    """Add a message to a chat session."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Add message
    cursor.execute(
        "INSERT INTO messages (chat_id, query, report) VALUES (?, ?, ?)",
        (chat_id, query, report)
    )
    
    message_id = cursor.lastrowid
    
    # Update chat's updated_at timestamp with local time
    cursor.execute(
        "UPDATE chats SET updated_at = DATETIME('now', 'localtime') WHERE id = ?",
        (chat_id,)
    )
    
    conn.commit()
    conn.close()
    
    return message_id


def get_chat_messages(chat_id: int) -> List[Dict]:
    """Get all messages for a chat session."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, query, report, created_at 
        FROM messages 
        WHERE chat_id = ? 
        ORDER BY created_at ASC
    """, (chat_id,))
    
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return messages


# ============================================================================
# DOCUMENT FUNCTIONS
# ============================================================================

def add_document(
    chat_id: int,
    filename: str,
    file_path: str,
    file_type: str,
    file_size: int,
    extracted_text: str,
    summary: str,
    genuineness_score: int,
    genuineness_analysis: str,
    word_count: int
) -> int:
    """Add a document to a chat session."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO documents (
            chat_id, filename, file_path, file_type, file_size,
            extracted_text, summary, genuineness_score,
            genuineness_analysis, word_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        chat_id, filename, file_path, file_type, file_size,
        extracted_text, summary, genuineness_score,
        genuineness_analysis, word_count
    ))
    
    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return doc_id


def get_chat_documents(chat_id: int) -> List[Dict]:
    """Get all documents for a chat session."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, filename, file_type, file_size, summary,
               genuineness_score, word_count, uploaded_at
        FROM documents
        WHERE chat_id = ?
        ORDER BY uploaded_at DESC
    """, (chat_id,))
    
    documents = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return documents


def get_document(doc_id: int) -> Optional[Dict]:
    """Get a specific document."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM documents WHERE id = ?
    """, (doc_id,))
    
    row = cursor.fetchone()
    doc = dict(row) if row else None
    conn.close()
    
    return doc


def delete_document(doc_id: int) -> bool:
    """Delete a document."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get file path before deleting
    cursor.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,))
    result = cursor.fetchone()
    
    if result:
        file_path = result[0]
        # Delete from database
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        # Delete physical file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        return success
    
    conn.close()
    return False


# Initialize database on import
init_db()
