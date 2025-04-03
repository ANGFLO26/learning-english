// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// Test submission handling
const testForm = document.getElementById('test-form');
if (testForm) {
    testForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const formData = new FormData(testForm);
        const answers = {};
        
        for (let [key, value] of formData.entries()) {
            if (key.startsWith('answer_')) {
                const testId = key.split('_')[1];
                answers[testId] = value;
            }
        }
        
        // Send answers to server
        fetch(window.location.href, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(answers)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                alert(data.message || 'An error occurred. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    });
}

// Learning mode functionality
function playAudio(text, lang) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    window.speechSynthesis.speak(utterance);
}

// Handle audio playback buttons
document.querySelectorAll('.play-audio').forEach(button => {
    button.addEventListener('click', function() {
        const text = this.dataset.text;
        const lang = this.dataset.lang;
        playAudio(text, lang);
    });
});

// Handle keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Space bar to check answer in learning mode
    if (event.code === 'Space' && document.getElementById('answer-input')) {
        event.preventDefault();
        checkAnswer();
    }
    
    // Enter key to submit test
    if (event.code === 'Enter' && document.getElementById('test-form')) {
        event.preventDefault();
        document.getElementById('test-form').dispatchEvent(new Event('submit'));
    }
}); 