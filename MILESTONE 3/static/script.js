+// JavaScript for AI Research Assistant

let currentReport = '';
let currentQuery = '';

// Set example query
function setQuery(query) {
    document.getElementById('queryInput').value = query;
    document.getElementById('queryInput').focus();
}

// Handle form submission
document.getElementById('researchForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const query = document.getElementById('queryInput').value.trim();
    if (!query) return;

    currentQuery = query;

    // Show loading, hide others
    showSection('loadingSection');

    try {
        const response = await fetch('/research', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });

        const data = await response.json();

        if (data.success) {
            currentReport = data.report;
            displayResults(data.query, data.html_report);
        } else {
            showError(data.error || 'An unknown error occurred');
        }
    } catch (error) {
        showError('Failed to connect to the server. Please try again.');
        console.error('Error:', error);
    }
});

// Display results
function displayResults(query, htmlReport) {
    document.getElementById('displayQuery').textContent = query;
    document.getElementById('reportContent').innerHTML = htmlReport;
    showSection('resultsSection');
}

// Show error
function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    showSection('errorSection');
}

// Show specific section
function showSection(sectionId) {
    const sections = ['searchSection', 'loadingSection', 'resultsSection', 'errorSection'];
    sections.forEach(id => {
        document.getElementById(id).classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');
}

// New search
function newSearch() {
    document.getElementById('queryInput').value = '';
    showSection('searchSection');
    document.getElementById('queryInput').focus();
}

// Copy report
function copyReport() {
    navigator.clipboard.writeText(currentReport).then(() => {
        alert('✅ Report copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('❌ Failed to copy report');
    });
}

// Download report
function downloadReport() {
    const blob = new Blob([currentReport], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research_report_${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Focus on input when page loads
window.addEventListener('load', function () {
    document.getElementById('queryInput').focus();
});
