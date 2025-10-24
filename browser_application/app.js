// Exact functionality from click-and-sing-magic with WebSocket integration
class ConcodeBrowserApp {
    constructor() {
        this.socket = null;
        this.serverAvailable = false;
        this.micAvailable = false;
        this.isRecording = false;
        this.fullSentences = [];
        this.audioContext = null;
        this.mediaStream = null;
        this.processor = null;
        this.wrap1 = true;
        this.wrap2 = true;
        
        this.SERVER_URL = "ws://localhost:8001";
        this.SERVER_CHECK_INTERVAL = 5000;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.connectToServer();
        this.requestMicrophoneAccess();
        this.updateStatus();
    }

    setupEventListeners() {
        // MicButton functionality
        const micButton = document.getElementById('micButton');
        micButton.addEventListener('click', () => this.toggleRecording());

        // Copy buttons
        document.getElementById('copyBtn1').addEventListener('click', () => this.copyToClipboard('backend'));
        document.getElementById('copyBtn2').addEventListener('click', () => this.copyToClipboard('python'));

        // Wrap buttons
        document.getElementById('wrapBtn1').addEventListener('click', () => this.toggleWrap(1));
        document.getElementById('wrapBtn2').addEventListener('click', () => this.toggleWrap(2));
    }

    // WebSocket connection management (from example_browserclient2)
    connectToServer() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            return;
        }

        this.socket = new WebSocket(this.SERVER_URL);

        this.socket.onopen = (event) => {
            this.serverAvailable = true;
            console.log('Connected to server');
            this.updateStatus();
        };

        this.socket.onmessage = (event) => {
            try {
                let data = JSON.parse(event.data);
                
                if (data.type === 'realtime') {
                    this.displayRealtimeText(data.text);
                } else if (data.type === 'fullSentence') {
                    this.fullSentences.push(data.text);
                    this.displayRealtimeText(""); // Refresh display with new full sentence
                }
            } catch (error) {
                console.error('Error parsing message:', error);
            }
        };

        this.socket.onclose = (event) => {
            this.serverAvailable = false;
            console.log('Disconnected from server');
            this.updateStatus();
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.serverAvailable = false;
            this.updateStatus();
        };
    }

    // MicButton functionality (from click-and-sing-magic)
    toggleRecording() {
        if (!this.micAvailable) {
            this.showToast('Microphone access is required. Please allow microphone access and refresh the page.');
            return;
        }

        if (!this.serverAvailable) {
            this.showToast('Server is not available. Please start the server and try again.');
            return;
        }

        this.isRecording = !this.isRecording;
        this.updateRecordingUI();
        this.updateStatus();

        if (this.isRecording && this.audioContext && this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }
    }

    updateRecordingUI() {
        const micButton = document.getElementById('micButton');
        const micIcon = document.getElementById('micIcon');
        const micOffIcon = document.getElementById('micOffIcon');
        const pulseRing1 = document.getElementById('pulseRing1');
        const pulseRing2 = document.getElementById('pulseRing2');

        if (this.isRecording) {
            micButton.classList.add('recording');
            micButton.classList.add('animate-glow');
            micButton.setAttribute('aria-label', 'Stop recording');
            micIcon.classList.add('hidden');
            micOffIcon.classList.remove('hidden');
            pulseRing1.classList.remove('hidden');
            pulseRing2.classList.remove('hidden');
            pulseRing1.classList.add('animate-pulse-ring');
            pulseRing2.classList.add('animate-pulse-ring');
        } else {
            micButton.classList.remove('recording');
            micButton.classList.remove('animate-glow');
            micButton.setAttribute('aria-label', 'Start recording');
            micIcon.classList.remove('hidden');
            micOffIcon.classList.add('hidden');
            pulseRing1.classList.add('hidden');
            pulseRing2.classList.add('hidden');
            pulseRing1.classList.remove('animate-pulse-ring');
            pulseRing2.classList.remove('animate-pulse-ring');
        }
    }

    updateStatus() {
        const status = document.getElementById('status');
        let statusText = '';
        
        if (!this.micAvailable) {
            statusText = '🎤 Please allow microphone access';
        } else if (!this.serverAvailable) {
            statusText = '🖥️ Connecting to server...';
        } else if (this.isRecording) {
            statusText = '🎙️ Recording... Speak now';
        } else {
            statusText = 'Click the microphone to start';
        }
        
        status.textContent = statusText;
    }

    // Audio processing (from example_browserclient2)
    requestMicrophoneAccess() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                this.mediaStream = stream;
                this.setupAudioProcessing(stream);
                this.micAvailable = true;
                this.updateStatus();
            })
            .catch(error => {
                console.error('Microphone access denied:', error);
                this.micAvailable = false;
                this.updateStatus();
            });
    }

    setupAudioProcessing(stream) {
        this.audioContext = new AudioContext();
        let source = this.audioContext.createMediaStreamSource(stream);
        this.processor = this.audioContext.createScriptProcessor(256, 1, 1);

        source.connect(this.processor);
        this.processor.connect(this.audioContext.destination);

        this.processor.onaudioprocess = (e) => {
            if (!this.isRecording || !this.serverAvailable || this.socket.readyState !== WebSocket.OPEN) {
                return;
            }

            let inputData = e.inputBuffer.getChannelData(0);
            let outputData = new Int16Array(inputData.length);

            // Convert to 16-bit PCM
            for (let i = 0; i < inputData.length; i++) {
                outputData[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
            }

            try {
                // Create metadata
                let metadata = JSON.stringify({ sampleRate: this.audioContext.sampleRate });
                let metadataBytes = new TextEncoder().encode(metadata);
                let metadataLength = new ArrayBuffer(4);
                let metadataLengthView = new DataView(metadataLength);
                metadataLengthView.setInt32(0, metadataBytes.byteLength, true);

                // Combine and send
                let combinedData = new Blob([metadataLength, metadataBytes, outputData.buffer]);
                this.socket.send(combinedData);
            } catch (error) {
                console.error('Error sending audio data:', error);
            }
        };
    }

    // Display functionality (from example_browserclient2 with click-and-sing-magic styling)
    displayRealtimeText(realtimeText) {
        const textDisplay = document.getElementById('textDisplay');
        
        let displayedText = this.fullSentences.map((sentence, index) => {
            let className = index % 2 === 0 ? 'text-yellow-400' : 'text-cyan-400';
            return `<span class="${className}">${this.escapeHtml(sentence)} </span>`;
        }).join('') + this.escapeHtml(realtimeText);

        textDisplay.innerHTML = displayedText || 'Data from backend will appear here...';
        
        // Auto-scroll to bottom
        textDisplay.scrollTop = textDisplay.scrollHeight;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // CodeBlock functionality (from click-and-sing-magic)
    copyToClipboard(type) {
        let content = '';
        
        if (type === 'backend') {
            content = this.fullSentences.join(' ') || 'Data from backend will appear here...';
        } else if (type === 'python') {
            content = `def greet(name):
    print(f"Hello, {name}!")

greet("World")`;
        }
        
        if (!content.trim()) {
            this.showToast('No content to copy');
            return;
        }
        
        navigator.clipboard.writeText(content).then(() => {
            this.showToast('Copied to clipboard');
        }).catch(error => {
            console.error('Failed to copy text:', error);
            this.showToast('Failed to copy text to clipboard');
        });
    }

    toggleWrap(blockNumber) {
        const codeElement = blockNumber === 1 ? 
            document.getElementById('backendData') : 
            document.getElementById('pythonCode');
        
        if (blockNumber === 1) {
            this.wrap1 = !this.wrap1;
            codeElement.className = this.wrap1 ? 'whitespace-pre-wrap break-words' : 'whitespace-pre';
        } else {
            this.wrap2 = !this.wrap2;
            codeElement.className = this.wrap2 ? 'whitespace-pre-wrap break-words' : 'whitespace-pre';
        }
    }

    // Toast functionality (from click-and-sing-magic Sonner)
    showToast(message) {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        
        container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            toast.classList.add('hide');
            setTimeout(() => {
                if (container.contains(toast)) {
                    container.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    // Periodic server connection check
    startServerCheck() {
        setInterval(() => {
            if (!this.serverAvailable) {
                this.connectToServer();
            }
        }, this.SERVER_CHECK_INTERVAL);
    }

    // Cleanup
    cleanup() {
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
        if (this.socket) {
            this.socket.close();
        }
    }
}

// Initialize the application
let app;

document.addEventListener('DOMContentLoaded', () => {
    app = new ConcodeBrowserApp();
    app.startServerCheck();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (app) {
        app.cleanup();
    }
});

// Add yellow and cyan text colors for transcription
const style = document.createElement('style');
style.textContent = `
    .text-yellow-400 { color: #facc15; }
    .text-cyan-400 { color: #22d3ee; }
`;
document.head.appendChild(style);