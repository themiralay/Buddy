document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const voiceButton = document.getElementById('voice-button');
    const tasksList = document.getElementById('tasks-list');
    const filterButtons = document.querySelectorAll('.tasks-filter button');
    
    // User ID - in a real app, this would come from authentication
    const userId = 'default_user';
    
    // Voice recording variables
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    
    // Initialize
    init();
    
    function init() {
        // Setup event listeners
        sendButton.addEventListener('click', sendMessage);
        userInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        voiceButton.addEventListener('click', toggleVoiceRecording);
        
        // Setup task filter buttons
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                loadTasks(button.dataset.filter);
            });
        });
        
        // Setup media recorder if browser supports it
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            // We'll set it up when the user clicks the voice button
        } else {
            voiceButton.disabled = true;
            voiceButton.title = 'Voice input not supported in your browser';
        }
        
        // Load initial tasks
        loadTasks('all');
    }
    
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;
        
        // Add user message to UI
        addMessageToUI('user', message);
        
        // Clear input
        userInput.value = '';
        
        // Send to backend
        fetchChatResponse(message);
    }
    
    async function fetchChatResponse(message) {
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    user_id: userId,
                    include_voice: false
                })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Add assistant response to UI
            addMessageToUI('assistant', data.text);
            
            // Reload tasks if any were extracted
            if (data.tasks_extracted > 0) {
                const activeFilter = document.querySelector('.tasks-filter button.active').dataset.filter;
                loadTasks(activeFilter);
            }
        } catch (error) {
            console.error('Error:', error);
            addMessageToUI('assistant', 'Sorry, there was an error processing your request.');
        }
    }
    
    function addMessageToUI(sender, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar';
        avatarDiv.textContent = sender === 'user' ? '👤' : '🤖';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'content';
        
        const paragraph = document.createElement('p');
        paragraph.textContent = content;
        
        contentDiv.appendChild(paragraph);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    async function loadTasks(filter) {
        try {
            let url = `/api/tasks?user_id=${userId}`;
            if (filter !== 'all') {
                url += `&status=${filter}`;
            }
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            renderTasks(data.tasks || []);
        } catch (error) {
            console.error('Error loading tasks:', error);
            tasksList.innerHTML = '<p class="no-tasks">Error loading tasks</p>';
        }
    }
    
    function renderTasks(tasks) {
        if (tasks.length === 0) {
            tasksList.innerHTML = '<p class="no-tasks">No tasks yet. Ask me to remind you about something!</p>';
            return;
        }
        
        tasksList.innerHTML = '';
        
        tasks.forEach(task => {
            const taskDiv = document.createElement('div');
            taskDiv.className = `task-item ${task.status}`;
            taskDiv.dataset.id = task.id;
            
            const description = document.createElement('div');
            description.className = 'description';
            description.textContent = task.description;
            
            const meta = document.createElement('div');
            meta.className = 'meta';
            
            const date = document.createElement('span');
            date.textContent = new Date(task.created_at).toLocaleString();
            
            const status = document.createElement('span');
            status.textContent = task.status;
            
            meta.appendChild(date);
            meta.appendChild(status);
            
            const actions = document.createElement('div');
            actions.className = 'actions';
            
            if (task.status === 'pending') {
                const completeButton = document.createElement('button');
                completeButton.textContent = 'Complete';
                completeButton.addEventListener('click', () => updateTaskStatus(task.id, 'completed'));
                actions.appendChild(completeButton);
            } else if (task.status === 'completed') {
                const reopenButton = document.createElement('button');
                reopenButton.textContent = 'Reopen';
                reopenButton.addEventListener('click', () => updateTaskStatus(task.id, 'pending'));
                actions.appendChild(reopenButton);
            }
            
            taskDiv.appendChild(description);
            taskDiv.appendChild(meta);
            taskDiv.appendChild(actions);
            
            tasksList.appendChild(taskDiv);
        });
    }
    
    async function updateTaskStatus(taskId, status) {
        try {
            const response = await fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const activeFilter = document.querySelector('.tasks-filter button.active').dataset.filter;
            loadTasks(activeFilter);
        } catch (error) {
            console.error('Error updating task:', error);
        }
    }
    
    function toggleVoiceRecording() {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    }
    
    function startRecording() {
        if (isRecording) return;
        
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.addEventListener('dataavailable', event => {
                    audioChunks.push(event.data);
                });
                
                mediaRecorder.addEventListener('stop', () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/mp3' });
                    sendVoiceRecording(audioBlob);
                    
                    // Stop all tracks to release microphone
                    stream.getTracks().forEach(track => track.stop());
                });
                
                mediaRecorder.start();
                isRecording = true;
                voiceButton.textContent = '⏹️';
                voiceButton.title = 'Stop recording';
                voiceButton.classList.add('recording');
            })
            .catch(error => {
                console.error('Error accessing microphone:', error);
                alert('Could not access microphone. Please check permissions.');
            });
    }
    
    function stopRecording() {
        if (!isRecording) return;
        
        mediaRecorder.stop();
        isRecording = false;
        voiceButton.textContent = '🎤';
        voiceButton.title = 'Voice Input';
        voiceButton.classList.remove('recording');
    }
    
    async function sendVoiceRecording(audioBlob) {
        // Add a placeholder message
        const placeholderId = Date.now();
        addMessageToUI('user', '🎤 Processing voice message...');
        
        const formData = new FormData();
        formData.append('audio', audioBlob);
        formData.append('user_id', userId);
        
        try {
            const response = await fetch('/api/voice', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Replace placeholder with actual transcription
            const messages = chatMessages.querySelectorAll('.message');
            const placeholder = messages[messages.length - 1];
            placeholder.querySelector('p').textContent = data.text || '(Could not transcribe audio)';
            
            // Add assistant response
            addMessageToUI('assistant', data.text);
            
            // Play audio response if available
            if (data.voice_data) {
                playAudioResponse(data.voice_data);
            }
            
            // Reload tasks if any were extracted
            if (data.tasks_extracted > 0) {
                const activeFilter = document.querySelector('.tasks-filter button.active').dataset.filter;
                loadTasks(activeFilter);
            }
        } catch (error) {
            console.error('Error processing voice:', error);
            addMessageToUI('assistant', 'Sorry, there was an error processing your voice message.');
        }
    }
    
    function playAudioResponse(base64Audio) {
        const audio = new Audio(`data:audio/mp3;base64,${base64Audio}`);
        audio.play().catch(error => {
            console.error('Error playing audio:', error);
        });
    }
});