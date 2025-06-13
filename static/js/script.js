function sendQuery() {
    const queryInput = document.getElementById('query');
    const query = queryInput.value.trim();
    if (!query) return;

    const messagesDiv = document.getElementById('messages');
    messagesDiv.innerHTML += `<p class="user-message">You: ${query}</p>`;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    fetch('/get_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            messagesDiv.innerHTML += `<p class="bot-message"><strong>Error:</strong> ${data.error}</p>`;
        } else {
            messagesDiv.innerHTML += `<p class="bot-message">Bot: ${data.answer}</p>`;
        }
        queryInput.value = '';
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    })
    .catch(error => {
        messagesDiv.innerHTML += `<p class="bot-message"><strong>Error:</strong> Failed to get response</p>`;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    });
}

// Allow pressing Enter to send query
document.getElementById('query').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendQuery();
    }
});