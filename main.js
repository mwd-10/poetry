document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generateBtn');
    const downloadBtn = document.getElementById('downloadBtn');

    if (generateBtn) {
        generateBtn.addEventListener('click', processPoem);
    }

    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadImage);
    }
});

async function processPoem() {
    const textElement = document.getElementById('poemInput');
    const authorElement = document.getElementById('authorInput');

    if (!textElement || !authorElement) return;

    const text = textElement.value;
    const author = authorElement.value;

    if (!text.trim()) {
        alert('الرجاء إدخال بيت شعري أولاً');
        return;
    }

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, author })
        });

        const data = await response.json();

        if (data.success) {
            typeEffect('displayText', data.text);
            document.getElementById('displayAuthor').innerText = data.author ? `- ${data.author}` : '';
            document.getElementById('rhymeBadge').innerText = data.rhyme;
            document.getElementById('downloadBtn').disabled = false;
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function typeEffect(elementId, text) {
    const element = document.getElementById(elementId);
    if (!element) return;
    element.innerText = '';
    let i = 0;

    const timer = setInterval(() => {
        if (i < text.length) {
            element.innerText += text.charAt(i);
            i++;
        } else {
            clearInterval(timer);
        }
    }, 40);
}

async function downloadImage() {
    const textElement = document.getElementById('poemInput');
    const authorElement = document.getElementById('authorInput');
    const themeElement = document.getElementById('themeSelect');
    
    if (!textElement || !authorElement) return;

    const text = textElement.value;
    const author = authorElement.value;
    const theme = themeElement ? themeElement.value : 'brown';

    try {
        const response = await fetch('/download-card', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, author, theme })
        });

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `poetry_card_${theme}.png`;
        document.body.appendChild(a);
        a.click();
        a.remove();
    } catch (error) {
        console.error('Download Error:', error);
    }
}
