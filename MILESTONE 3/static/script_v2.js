// Enhanced JavaScript for ChatGPT-like Research Assistant

let currentChatId = null;
let chats = [];
let currentAbortController = null;  // For canceling ongoing requests

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function () {
    initializeApp();
});

async function initializeApp() {
    loadTheme();
    await loadChatList();

    if (chats.length === 0) {
        await createNewChat();
    } else {
        await loadChat(chats[0].id);
    }

    setupEventListeners();
}

function setupEventListeners() {
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    document.getElementById('newChatBtn').addEventListener('click', createNewChat);
    document.getElementById('deleteChatBtn').addEventListener('click', deleteCurrentChat);
    document.getElementById('editTitleBtn').addEventListener('click', editChatTitle);
    document.getElementById('toggleSidebarBtn').addEventListener('click', toggleSidebar);
    document.getElementById('researchForm').addEventListener('submit', handleFormSubmit);

    // Document upload handlers
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('fileInput');
    const closeDocPopup = document.getElementById('closeDocPopup');

    if (uploadBtn && fileInput) {
        uploadBtn.addEventListener('click', () => {
            const popup = document.getElementById('documentPopup');
            if (popup.classList.contains('hidden')) {
                fileInput.click();
            } else {
                popup.classList.add('hidden');
            }
        });
        fileInput.addEventListener('change', handleFileUpload);
    }

    if (closeDocPopup) {
        closeDocPopup.addEventListener('click', () => {
            document.getElementById('documentPopup').classList.add('hidden');
        });
    }

    const textarea = document.getElementById('queryInput');
    textarea.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
}

// ============================================================================
// THEME MANAGEMENT
// ============================================================================

function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);

    const themeIcon = document.querySelector('.theme-icon');
    const themeText = document.querySelector('.theme-text');

    if (theme === 'light') {
        themeIcon.textContent = '☀️';
        themeText.textContent = 'Light Mode';
    } else {
        themeIcon.textContent = '🌙';
        themeText.textContent = 'Dark Mode';
    }
}

// ============================================================================
// CHAT MANAGEMENT
// ============================================================================

async function loadChatList() {
    try {
        const response = await fetch('/api/chat/list');
        const data = await response.json();

        if (data.success) {
            chats = data.chats;
            renderChatList();
        }
    } catch (error) {
        console.error('Error loading chats:', error);
    }
}

function renderChatList() {
    const chatList = document.getElementById('chatList');
    chatList.innerHTML = '';

    chats.forEach(chat => {
        const chatItem = document.createElement('div');
        chatItem.className = 'chat-item';
        if (chat.id === currentChatId) {
            chatItem.classList.add('active');
        }

        chatItem.innerHTML = `
            <div class="chat-item-content" onclick="loadChat(${chat.id})">
                <div class="chat-item-title">${escapeHtml(chat.title)}</div>
                <div class="chat-item-date">${formatDate(chat.updated_at)}</div>
            </div>
        `;

        chatList.appendChild(chatItem);
    });
}

async function createNewChat() {
    try {
        const response = await fetch('/api/chat/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: 'New Research' })
        });

        const data = await response.json();

        if (data.success) {
            await loadChatList();
            await loadChat(data.chat_id);
        }
    } catch (error) {
        console.error('Error creating chat:', error);
        alert('Failed to create new chat');
    }
}

async function loadChat(chatId) {
    try {
        const response = await fetch(`/api/chat/${chatId}`);
        const data = await response.json();

        if (data.success) {
            currentChatId = chatId;
            document.getElementById('chatTitle').textContent = data.chat.title;

            renderMessages(data.messages);
            renderChatList();
            loadDocuments();  // Load documents for this chat

            if (data.messages.length > 0) {
                document.getElementById('welcomeScreen').classList.add('hidden');
            } else {
                document.getElementById('welcomeScreen').classList.remove('hidden');
            }
        }
    } catch (error) {
        console.error('Error loading chat:', error);
        try {
            const response = await fetch(`/api/chat/${currentChatId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                await loadChatList();

                if (chats.length > 0) {
                    await loadChat(chats[0].id);
                } else {
                    await createNewChat();
                }
            }
        } catch (error) {
            console.error('Error deleting chat:', error);
            alert('Failed to delete chat');
        }
    }
}

async function editChatTitle() {
    if (!currentChatId) return;

    const currentTitle = document.getElementById('chatTitle').textContent;
    const newTitle = prompt('Enter new title:', currentTitle);

    if (!newTitle || newTitle === currentTitle) return;

    try {
        const response = await fetch(`/api/chat/${currentChatId}/rename`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: newTitle })
        });

        const data = await response.json();

        if (data.success) {
            document.getElementById('chatTitle').textContent = newTitle;
            await loadChatList();
        }
    } catch (error) {
        console.error('Error renaming chat:', error);
        alert('Failed to rename chat');
    }
}

async function deleteCurrentChat() {
    if (!currentChatId) return;

    if (!confirm('Are you sure you want to delete this chat?')) return;

    try {
        const response = await fetch(`/api/chat/${currentChatId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            await loadChatList();

            if (chats.length > 0) {
                await loadChat(chats[0].id);
            } else {
                await createNewChat();
            }
        }
    } catch (error) {
        console.error('Error deleting chat:', error);
        alert('Failed to delete chat');
    }
}

// ============================================================================
// MESSAGE RENDERING
// ============================================================================

function renderMessages(messages) {
    const messagesDiv = document.getElementById('messages');
    messagesDiv.innerHTML = '';

    // Store messages globally for copy/download functions
    window.currentMessages = messages;

    messages.forEach((msg, index) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';

        // Convert markdown to HTML using marked.js
        const reportHtml = marked.parse(msg.report);

        messageDiv.innerHTML = `
            <div class="message-query">
                <strong>Your Query:</strong>
                ${escapeHtml(msg.query)}
            </div>
            <div class="message-report">
                <div class="report-actions">
                    <button class="btn-action" onclick="copyReport(${index})" title="Copy to clipboard">
                        📋 Copy
                    </button>
                    <button class="btn-action" onclick="downloadReport(${index})" title="Download as markdown">
                        💾 Download
                    </button>
                </div>
                <div class="report-content">
                    ${reportHtml}
                </div>
            </div>
        `;

        messagesDiv.appendChild(messageDiv);
    });

    // Scroll to bottom
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// ============================================================================
// RESEARCH
// ============================================================================

function handleFormSubmit(e) {
    e.preventDefault();

    // If currently researching, stop it
    if (currentAbortController) {
        stopResearch();
    } else {
        submitResearch();
    }
}

function stopResearch() {
    if (currentAbortController) {
        currentAbortController.abort();
        currentAbortController = null;

        // Reset UI
        document.getElementById('loadingMessage').classList.add('hidden');
        toggleStopButton(false);

        const queryInput = document.getElementById('queryInput');
        queryInput.disabled = false;
        queryInput.focus();
    }
}

function toggleStopButton(isResearching) {
    const sendIcon = document.getElementById('sendIcon');
    const stopIcon = document.getElementById('stopIcon');
    const sendBtn = document.getElementById('sendBtn');

    if (isResearching) {
        sendIcon.style.display = 'none';
        stopIcon.style.display = 'inline';
        sendBtn.style.backgroundColor = 'var(--danger, #ef4444)';
        sendBtn.title = 'Stop generating';
    } else {
        sendIcon.style.display = 'inline';
        stopIcon.style.display = 'none';
        sendBtn.style.backgroundColor = '';
        sendBtn.title = 'Send message';
    }
}

async function submitResearch() {
    if (!currentChatId) {
        await createNewChat();
    }

    const query = document.getElementById('queryInput').value.trim();
    if (!query) return;

    // Create abort controller for this request
    currentAbortController = new AbortController();

    // Show stop button
    toggleStopButton(true);
    const queryInput = document.getElementById('queryInput');
    queryInput.disabled = true;

    document.getElementById('welcomeScreen').classList.add('hidden');
    document.getElementById('loadingMessage').classList.remove('hidden');

    document.getElementById('queryInput').value = '';
    document.getElementById('queryInput').style.height = 'auto';

    try {
        const response = await fetch(`/api/chat/${currentChatId}/research`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query }),
            signal: currentAbortController.signal  // Add abort signal
        });

        const data = await response.json();

        if (data.success) {
            await loadChat(currentChatId);
            await loadChatList();
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
            queryInput.value = query;
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Research stopped by user');
            queryInput.value = query;  // Restore query
        } else {
            console.error('Error performing research:', error);
            alert('Failed to perform research. Please try again.');
            queryInput.value = query;
        }
    } finally {
        document.getElementById('loadingMessage').classList.add('hidden');
        toggleStopButton(false);
        currentAbortController = null;
        queryInput.disabled = false;
        queryInput.focus();
    }
}

// ============================================================================
// UI HELPERS
// ============================================================================

function setExampleQuery(query) {
    document.getElementById('queryInput').value = query;
    document.getElementById('queryInput').focus();
    const textarea = document.getElementById('queryInput');
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

function copyReport(index) {
    if (!window.currentMessages || !window.currentMessages[index]) return;

    const report = window.currentMessages[index].report;

    navigator.clipboard.writeText(report).then(() => {
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✅ Copied!';
        btn.style.background = 'var(--success)';

        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy report');
    });
}

function downloadReport(index) {
    if (!window.currentMessages || !window.currentMessages[index]) return;

    const msg = window.currentMessages[index];
    const content = `# Research Report\n\n**Query:** ${msg.query}\n\n---\n\n${msg.report}`;

    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;

    const filename = msg.query.substring(0, 50).replace(/[^a-z0-9]/gi, '_').toLowerCase();
    a.download = `research_${filename}_${Date.now()}.md`;

    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('hidden');
}

function formatDate(dateString) {
    // Handle both UTC and local timestamps
    // SQLite returns UTC timestamps, so we need to parse them correctly
    let date;
    if (dateString.includes('T') || dateString.includes('Z')) {
        // ISO format or UTC
        date = new Date(dateString);
    } else {
        // SQLite format: "YYYY-MM-DD HH:MM:SS" (assume UTC)
        date = new Date(dateString + ' UTC');
    }

    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================================
// DOCUMENT UPLOAD
// ============================================================================

async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`/api/chat/${currentChatId}/upload`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Document uploaded successfully!', 'success');
            await loadDocuments();
            // Show the popup with documents
            document.getElementById('documentPopup').classList.remove('hidden');
        } else {
            showNotification(result.error || 'Upload failed', 'error');
        }
    } catch (error) {
        showNotification('Upload failed: ' + error.message, 'error');
    }

    event.target.value = '';
}

async function loadDocuments() {
    if (!currentChatId) return;

    try {
        const response = await fetch(`/api/chat/${currentChatId}/documents`);
        const result = await response.json();

        if (result.success) {
            displayDocuments(result.documents);
        }
    } catch (error) {
        console.error('Failed to load documents:', error);
    }
}

function displayDocuments(documents) {
    const documentList = document.getElementById('documentList');
    if (!documentList) return;

    if (documents.length === 0) {
        documentList.innerHTML = '<div style="text-align: center; padding: 20px; color: var(--text-tertiary);">No documents uploaded yet</div>';
        return;
    }

    documentList.innerHTML = documents.map(doc => `
        <div class="document-item" onclick="showDocumentDetails(${doc.id})">
            <div class="document-name">${escapeHtml(doc.filename)}</div>
            <div class="document-meta">
                <span>${(doc.file_size / 1024).toFixed(1)} KB</span>
                ${doc.genuineness_score ? `<span class="genuineness-badge">${doc.genuineness_score}/10</span>` : ''}
            </div>
        </div>
    `).join('');
}

function showDocumentDetails(docId) {
    // TODO: Show modal with document summary and analysis
    console.log('Show document details:', docId);
}

function showNotification(message, type = 'info') {
    // Simple notification - can be enhanced
    alert(message);
}
