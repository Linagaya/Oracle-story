const API_URL = 'http://localhost:8000';
let selectedFile = null;

document.addEventListener('DOMContentLoaded', () => {
    setupDragAndDrop();
    loadClasses();
});

function setupDragAndDrop() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
}

function handleFileSelect(file) {
    if (!file.type.startsWith('image/')) {
        showToast('请上传图片文件', true);
        return;
    }

    selectedFile = file;

    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('previewImage').src = e.target.result;
        document.getElementById('previewContainer').style.display = 'block';
        document.getElementById('uploadArea').style.display = 'none';
        document.getElementById('predictBtn').disabled = false;
    };
    reader.readAsDataURL(file);
}

function resetUpload() {
    selectedFile = null;
    document.getElementById('previewContainer').style.display = 'none';
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('predictBtn').disabled = true;
    document.getElementById('fileInput').value = '';
    document.getElementById('resultSection').style.display = 'none';
}

async function predict() {
    if (!selectedFile) {
        showToast('请先选择图片', true);
        return;
    }

    const btn = document.getElementById('predictBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> 识别中...';

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            displayResult(data);
            showToast('识别成功！');
        } else {
            showToast(data.error || '识别失败', true);
        }
    } catch (error) {
        showToast('网络连接失败，请确保后端服务已启动', true);
        console.error('Error:', error);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🔍 开始识别';
    }
}

function displayResult(data) {
    document.getElementById('resultChar').textContent = data.character;
    document.getElementById('confidenceValue').textContent = `${data.confidence}%`;
    document.getElementById('confidenceProgress').style.width = `${data.confidence}%`;
    document.getElementById('resultStory').textContent = data.story;

    const predictionsList = document.getElementById('otherPredictions');
    predictionsList.innerHTML = '';

    if (data.all_predictions && data.all_predictions.length > 0) {
        data.all_predictions.forEach(pred => {
            if (pred.char !== data.character) {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span class="prediction-char">${pred.char}</span>
                    <span class="prediction-prob">${pred.prob}%</span>
                `;
                predictionsList.appendChild(li);
            }
        });
    }

    document.getElementById('resultSection').style.display = 'block';
    document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
}

async function loadClasses() {
    try {
        const response = await fetch(`${API_URL}/classes`);
        const data = await response.json();

        if (data.success) {
            const grid = document.getElementById('classesGrid');
            grid.innerHTML = '';

            data.classes.forEach(item => {
                const div = document.createElement('div');
                div.className = 'class-item';
                div.innerHTML = `
                    <span class="char">${item.char}</span>
                    <small>${item.id}</small>
                `;
                div.title = item.story;
                grid.appendChild(div);
            });
        }
    } catch (error) {
        console.error('加载字库失败:', error);
        loadDefaultClasses();
    }
}

function loadDefaultClasses() {
    const defaultClasses = ['日', '月', '山', '水', '火', '木', '金', '土', '人', '口', 
                           '目', '手', '足', '心', '田', '天', '地', '王', '卜', '贞'];
    
    const grid = document.getElementById('classesGrid');
    defaultClasses.forEach((char, index) => {
        const div = document.createElement('div');
        div.className = 'class-item';
        div.innerHTML = `
            <span class="char">${char}</span>
            <small>${index}</small>
        `;
        grid.appendChild(div);
    });
}

function showToast(message, isError = false) {
    const toast = document.createElement('div');
    toast.className = `toast ${isError ? 'error' : ''}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}