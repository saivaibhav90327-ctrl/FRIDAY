document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('user-input');
    const cpuBar = document.getElementById('cpu-bar');
    const ramBar = document.getElementById('ram-bar');
    const cpuVal = document.getElementById('cpu-val');
    const ramVal = document.getElementById('ram-val');
    const systemLogs = document.getElementById('system-logs');
    const micBtn = document.getElementById('mic-btn');

    // Real System Stats from Backend
    async function updateStats() {
        try {
            const response = await fetch('http://localhost:5000/stats');
            const data = await response.json();

            cpuBar.style.width = `${data.cpu}%`;
            ramBar.style.width = `${data.ram}%`;
            cpuVal.textContent = `${Math.round(data.cpu)}%`;
            ramVal.textContent = `${Math.round(data.ram)}%`;
            
            document.getElementById('latency').textContent = data.latency;
            document.getElementById('net-speed').textContent = data.status;
        } catch (err) {
            console.error("Backend offline");
        }
    }

    setInterval(updateStats, 1000);

    async function updateSecurity() {
        try {
            const response = await fetch('http://localhost:5000/security');
            const data = await response.json();
            document.getElementById('threats').textContent = data.threats;
        } catch (err) {}
    }
    setInterval(updateSecurity, 5000);

    // Logging System
    function addLog(message) {
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.textContent = `> ${message}`;
        systemLogs.appendChild(entry);
        systemLogs.scrollTop = systemLogs.scrollHeight;
        
        if (systemLogs.children.length > 5) {
            systemLogs.removeChild(systemLogs.firstChild);
        }
    }

    // Voice Visualizer Animation
    const bars = document.querySelectorAll('.bar');
    function animateVoice() {
        bars.forEach(bar => {
            const height = Math.random() * 100;
            bar.style.height = `${height}%`;
        });
    }

    // Real Voice Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = true; // Stay active
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onresult = (event) => {
            let interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                const transcript = event.results[i][0].transcript.toLowerCase();
                if (event.results[i].isFinal) {
                    addLog(`Heard: ${transcript}`);
                    
                    // Wake Word Detection
                    if (transcript.includes('friday')) {
                        const cmd = transcript.split('friday').pop().trim();
                        if (cmd) {
                            processCommand(cmd);
                        } else {
                            addLog("FRIDAY: At your service, Boss. What is your command?");
                            speak("At your service, Boss. What is your command?");
                        }
                    }
                }
            }
        };

        recognition.onend = () => {
            if (voiceInterval) recognition.start(); // Auto-restart if we want "Always Listening"
        };
    }

    let voiceInterval;
    micBtn.addEventListener('click', () => {
        if (!recognition) {
            addLog("Voice Recognition not supported in this browser.");
            return;
        }

        if (voiceInterval) {
            recognition.stop();
            clearInterval(voiceInterval);
            voiceInterval = null;
            micBtn.style.filter = 'grayscale(1)';
            addLog("FRIDAY: Hibernating.");
        } else {
            recognition.start();
            voiceInterval = setInterval(animateVoice, 100);
            micBtn.style.filter = 'grayscale(0) drop-shadow(0 0 5px var(--primary))';
            addLog('FRIDAY: Listening for wake word "Friday"...');
        }
    });

    // Handle Input
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const cmd = userInput.value.trim();
            if (cmd) {
                processCommand(cmd);
                userInput.value = '';
            }
        }
    });

    async function processCommand(cmd) {
        addLog(`User: ${cmd}`);
        
        try {
            const response = await fetch('http://localhost:5000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: cmd })
            });
            const data = await response.json();
            addLog(`FRIDAY: ${data.response}`);
            speak(data.response);
        } catch (err) {
            addLog("FRIDAY: Core offline. Check backend connection.");
        }
    }

    function speak(text) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.1;
        utterance.pitch = 1.2; // Slightly higher/metallic for FRIDAY
        window.speechSynthesis.speak(utterance);
    }

    addLog('System online. Welcome back, Boss.');
});
