const API_URL = 'http://localhost:8000';
let selectedFile = null;

document.addEventListener('DOMContentLoaded', () => {
    setupDragAndDrop();
    loadClasses();
    loadKnowledge();
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
    document.getElementById('contextInput').value = '';
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
        
        const context = document.getElementById('contextInput').value.trim();
        if (context) {
            formData.append('context', context);
        }

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

async function loadDemo() {
    const btn = event.target;
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> 加载中...';

    try {
        const response = await fetch(`${API_URL}/analyze_ambiguous_demo`);
        const data = await response.json();

        if (data.success) {
            displayDemoResult(data);
            showToast('演示数据加载成功！');
        } else {
            showToast('加载演示失败', true);
        }
    } catch (error) {
        showToast('网络连接失败', true);
        console.error('Error:', error);
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🎯 查看揣摩演示';
    }
}

function displayResult(data) {
    const charDisplay = document.getElementById('resultChar');
    const statusBadge = document.getElementById('statusBadge');
    const storySection = document.getElementById('storySection');
    const inferenceSection = document.getElementById('inferenceSection');
    const progressFill = document.getElementById('confidenceProgress');
    
    // 设置字符显示
    charDisplay.textContent = data.display_character || data.character;
    charDisplay.classList.remove('unknown');
    
    // 设置状态徽章和颜色
    statusBadge.classList.remove('known', 'ambiguous', 'polluted');
    progressFill.classList.remove('low', 'medium');
    
    document.getElementById('confidenceValue').textContent = `${data.confidence}%`;
    progressFill.style.width = `${data.confidence}%`;
    
    if (data.confidence < 35) {
        progressFill.classList.add('low');
    } else if (data.confidence < 50) {
        progressFill.classList.add('medium');
    }

    if (data.is_unknown) {
        // 未知字/疑难字
        charDisplay.classList.add('unknown');
        
        if (data.is_polluted) {
            statusBadge.textContent = '污染字';
            statusBadge.classList.add('polluted');
        } else if (data.is_ambiguous) {
            statusBadge.textContent = '难以定义字';
            statusBadge.classList.add('ambiguous');
        } else {
            statusBadge.textContent = '未知字';
            statusBadge.classList.add('ambiguous');
        }
        
        storySection.style.display = 'none';
        inferenceSection.style.display = 'block';
        
        if (data.inference) {
            displayInference(data.inference);
        }
    } else {
        // 已知字
        statusBadge.textContent = '已知字';
        statusBadge.classList.add('known');
        
        storySection.style.display = 'block';
        inferenceSection.style.display = 'none';
        document.getElementById('resultStory').textContent = data.story || '暂无字源故事';
    }

    // 显示其他候选
    displayPredictions(data.all_predictions, data.character);

    document.getElementById('resultSection').style.display = 'block';
    document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
}

function displayDemoResult(data) {
    const charDisplay = document.getElementById('resultChar');
    const statusBadge = document.getElementById('statusBadge');
    const storySection = document.getElementById('storySection');
    const inferenceSection = document.getElementById('inferenceSection');
    const progressFill = document.getElementById('confidenceProgress');
    
    // 演示模式显示
    charDisplay.textContent = '日';
    charDisplay.classList.add('unknown');
    
    statusBadge.textContent = '难以定义字（演示）';
    statusBadge.classList.remove('known', 'ambiguous', 'polluted');
    statusBadge.classList.add('ambiguous');
    
    document.getElementById('confidenceValue').textContent = '25.3%';
    progressFill.style.width = '25.3%';
    progressFill.classList.remove('low', 'medium');
    progressFill.classList.add('low');
    
    storySection.style.display = 'none';
    inferenceSection.style.display = 'block';
    
    // 构造inference对象
    const inference = {
        rough_meaning: data.analysis.rough_meaning,
        explanation_text: data.explanation,
        detailed_analysis: data.analysis,
        is_polluted: false,
        is_ambiguous: true,
        possible_meanings: [],
        suggestions: data.analysis.suggestions || []
    };
    
    displayInference(inference, data.analysis);
    
    // 显示模拟的候选
    const demoPreds = [
        {char: '日', prob: 25.3},
        {char: '口', prob: 18.7},
        {char: '曰', prob: 12.1},
        {char: '白', prob: 8.5},
        {char: '田', prob: 6.2}
    ];
    displayPredictions(demoPreds, '日');

    document.getElementById('resultSection').style.display = 'block';
    document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
}

function displayInference(inference, analysisData = null) {
    const analysis = analysisData || inference.detailed_analysis || {};
    
    // 大致含义
    document.getElementById('roughMeaning').textContent = inference.rough_meaning || '暂无分析结果';
    
    // 污染评估
    let pollutionText = '图像清晰';
    if (inference.is_polluted) {
        pollutionText = '⚠️ 图像存在较严重污染或残缺，识别结果仅供参考';
    } else if (inference.is_ambiguous) {
        pollutionText = '📝 字形清晰但置信度较低，可能是未收录字或异体字';
    }
    document.getElementById('pollutionStatus').textContent = pollutionText;
    
    // 部首分析
    const radicalDiv = document.getElementById('radicalAnalysis');
    if (analysis.radical_analysis && analysis.radical_analysis.length > 0) {
        radicalDiv.innerHTML = analysis.radical_analysis.slice(0, 3).map(r => 
            `<span class="analysis-tag highlight">「${r.name}」${r.meaning}</span>`
        ).join('');
    } else {
        radicalDiv.innerHTML = '<span class="text-muted">未检测到明显部首特征</span>';
    }
    
    // 形近字
    const similarDiv = document.getElementById('similarChars');
    if (analysis.similar_chars && analysis.similar_chars.length > 0) {
        similarDiv.innerHTML = analysis.similar_chars.slice(0, 5).map(c => 
            `<span class="analysis-tag">${c}</span>`
        ).join('');
    } else {
        similarDiv.innerHTML = '<span class="text-muted">未找到明显形近字</span>';
    }
    
    // 语境推断
    const contextDiv = document.getElementById('contextHints');
    if (analysis.context_hints && analysis.context_hints.length > 0) {
        contextDiv.innerHTML = analysis.context_hints.slice(0, 3).map(c => 
            `<span class="analysis-tag highlight">${c}</span>`
        ).join('');
    } else {
        contextDiv.innerHTML = '<span class="text-muted">无足够上下文信息</span>';
    }
    
    // 合文检测
    const hewenDiv = document.getElementById('hewenAnalysis');
    if (analysis.hewen_possibility && analysis.hewen_possibility.length > 0) {
        hewenDiv.innerHTML = analysis.hewen_possibility.slice(0, 2).map(h => 
            `<span class="analysis-tag highlight">「${h.name}」→ ${h.meaning}</span>`
        ).join('');
    } else {
        hewenDiv.innerHTML = '<span class="text-muted">未检测到常见合文模式</span>';
    }
    
    // 建议
    const suggestionsDiv = document.getElementById('suggestions');
    if (inference.suggestions && inference.suggestions.length > 0) {
        suggestionsDiv.innerHTML = inference.suggestions.slice(0, 4).map(s => 
            `<div style="margin: 5px 0;">• ${s}</div>`
        ).join('');
    } else {
        suggestionsDiv.innerHTML = '<div>建议结合更多甲骨文献进行比对考证</div>';
    }
    
    // 详细解释文本
    document.getElementById('explanationText').textContent = inference.explanation_text || '暂无详细分析报告';
}

function displayPredictions(predictions, mainChar) {
    const predictionsList = document.getElementById('otherPredictions');
    predictionsList.innerHTML = '';

    if (predictions && predictions.length > 0) {
        predictions.forEach(pred => {
            if (pred.char !== mainChar && pred.char !== `[?${mainChar}?]`) {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span class="prediction-char">${pred.char}</span>
                    <span class="prediction-prob">${pred.prob}%</span>
                `;
                predictionsList.appendChild(li);
            }
        });
    }
    
    if (predictionsList.children.length === 0) {
        predictionsList.innerHTML = '<li style="justify-content: center; color: #999;">无其他候选</li>';
    }
}

async function loadClasses() {
    try {
        const response = await fetch(`${API_URL}/classes`);
        const data = await response.json();

        if (data.success) {
            const grid = document.getElementById('classesGrid');
            grid.innerHTML = '';

            data.classes.forEach((item, index) => {
                const div = document.createElement('div');
                div.className = 'class-item';
                div.innerHTML = `
                    <span class="char">${item.char}</span>
                    <small>#${index + 1}</small>
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

async function loadKnowledge() {
    try {
        const response = await fetch(`${API_URL}/knowledge`);
        const data = await response.json();

        if (data.success) {
            const k = data.knowledge;
            document.getElementById('radicalCount').textContent = k.total_radicals;
            
            const categoriesDiv = document.getElementById('knowledgeCategories');
            if (k.categories) {
                categoriesDiv.innerHTML = k.categories.map(cat => 
                    `<span class="category-tag">${cat}</span>`
                ).join('');
            }
        }
    } catch (error) {
        console.error('加载知识库失败:', error);
        document.getElementById('radicalCount').textContent = '141+';
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
            <small>#${index + 1}</small>
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
