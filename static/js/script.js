document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('scrapeForm');
    const urlInput = document.getElementById('urlInput');
    const messagesDiv = document.getElementById('messages');
    const downloadSection = document.getElementById('downloadSection');
    const downloadBtn = document.getElementById('downloadBtn');
    const submitBtn = form.querySelector('button[type="submit"]');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Clear previous messages and hide download section
        messagesDiv.textContent = '';
        downloadSection.classList.add('hidden');
        
        const url = urlInput.value;
        
        try {
            // Disable the form while processing
            submitBtn.disabled = true;
            submitBtn.textContent = 'Scraping...';
            
            // Create EventSource for Server-Sent Events
            const eventSource = new EventSource(`/scrape?url=${encodeURIComponent(url)}`);
            
            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                // Create and append message element
                const messageElement = document.createElement('div');
                messageElement.textContent = data.message;
                messagesDiv.appendChild(messageElement);
                
                // Auto-scroll to the bottom
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                
                // If this is a success message, show the download button
                if (data.success === true) {
                    downloadSection.classList.remove('hidden');
                    downloadBtn.onclick = () => {
                        window.location.href = '/download';
                    };
                }
                
                // If this is an error message, close the connection
                if (data.success === false) {
                    eventSource.close();
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Start Scraping';
                }
            };
            
            eventSource.onerror = (error) => {
                console.error('EventSource failed:', error);
                eventSource.close();
                submitBtn.disabled = false;
                submitBtn.textContent = 'Start Scraping';
            };
            
        } catch (error) {
            const errorElement = document.createElement('div');
            errorElement.textContent = `Error: ${error.message}`;
            errorElement.style.color = 'red';
            messagesDiv.appendChild(errorElement);
            submitBtn.disabled = false;
            submitBtn.textContent = 'Start Scraping';
        }
    });
}); 