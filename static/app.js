const form = document.getElementById('upload-form');
const fileInput = document.getElementById('file-input');
const preview = document.getElementById('preview');
const responseBox = document.getElementById('response');

fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        preview.style.display = 'none';
    }
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];
    if (!file) {
        responseBox.textContent = 'Selecione um arquivo.';
        return;
    }
    const formData = new FormData();
    formData.append('file', file);
    try {
        const res = await fetch('/upload', { method: 'POST', body: formData });
        const data = await res.json();
        responseBox.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
        responseBox.textContent = 'Erro: ' + err.message;
    }
});
