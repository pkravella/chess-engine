document.addEventListener('DOMContentLoaded', function() {
    const statusDiv = document.getElementById('status');
    const toggleButton = document.getElementById('toggleAnalysis');
    let isAnalyzing = false;

    // Check connection to the local engine server
    async function checkConnection() {
        try {
            const response = await fetch('http://localhost:5000/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1' }),
            });
            
            if (response.ok) {
                statusDiv.textContent = 'Connected to engine';
                statusDiv.className = 'status connected';
                toggleButton.disabled = false;
            } else {
                throw new Error('Server error');
            }
        } catch (error) {
            statusDiv.textContent = 'Engine not connected. Please start the local server.';
            statusDiv.className = 'status disconnected';
            toggleButton.disabled = true;
        }
    }

    // Toggle analysis state
    toggleButton.addEventListener('click', function() {
        isAnalyzing = !isAnalyzing;
        toggleButton.textContent = isAnalyzing ? 'Stop Analysis' : 'Start Analysis';
        
        // Send message to content script
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {
                action: isAnalyzing ? 'startAnalysis' : 'stopAnalysis'
            });
        });
    });

    // Initial connection check
    checkConnection();
}); 