// static/js/webcam.js

// CSRF Token handling function
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

class WebcamCapture {
    constructor(videoElement, canvasElement) {
        this.video = videoElement;
        this.canvas = canvasElement;
        this.stream = null;
    }
    
    async start() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                    facingMode: "user",
                    frameRate: { ideal: 30 }
                }
            });
            this.video.srcObject = this.stream;
            
            // Wait for video to be ready
            await new Promise(resolve => {
                this.video.onloadedmetadata = () => {
                    this.video.play();
                    resolve();
                };
            });
        } catch (err) {
            throw new Error("Could not access webcam: " + err.message);
        }
    }
    
    capture() {
        const context = this.canvas.getContext('2d');
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        context.drawImage(this.video, 0, 0);
        
        // Use higher quality JPEG encoding
        return this.canvas.toDataURL('image/jpeg', 0.95);
    }
    
    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }
}

// Face Registration Handler
async function handleRegistration(webcam) {
    const imageData = webcam.capture();
    const csrfToken = getCookie('csrftoken');
    
    try {
        const response = await fetch('/api/register-face/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                image: imageData,
                username: document.getElementById('username').value,
                name: document.getElementById('name').value
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Registration failed');
        }
        
        alert('Registration successful!');
        window.location.href = '/login/';
        
    } catch (err) {
        alert(err.message);
    }
}

// Face Login Handler
async function handleLogin(webcam) {
    const imageData = webcam.capture();
    const csrfToken = getCookie('csrftoken');
    
    try {
        const response = await fetch('/api/login-face/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                image: imageData
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Login failed');
        }
        
        if (data.success) {
            window.location.href = '/dashboard/';
        } else {
            throw new Error(data.message || 'Face verification failed');
        }
        
    } catch (err) {
        console.error('Login error:', err);
        alert('Login failed: ' + (err.message || 'Unknown error occurred'));
    }
}