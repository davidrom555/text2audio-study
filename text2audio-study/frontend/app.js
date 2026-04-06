/**
 * Text2Audio Study - Frontend JavaScript
 * Maneja la interfaz de usuario y comunicación con el backend
 */

// Configuración
const API_BASE_URL = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
    ? 'http://localhost:8000'
    : window.location.origin;

// Estado de la aplicación
const state = {
    mode: 'file', // 'file' o 'text'
    currentFile: null,
    extractedText: '',
    ttsEngine: 'edge', // 'edge', 'gtts', 'pyttsx3'
    isConverting: false
};

// Referencias a elementos DOM
const elements = {
    // Botones de modo
    btnModeFile: document.getElementById('btn-mode-file'),
    btnModeText: document.getElementById('btn-mode-text'),
    
    // Paneles
    panelFile: document.getElementById('panel-file'),
    panelText: document.getElementById('panel-text'),
    
    // File upload
    dropZone: document.getElementById('drop-zone'),
    fileInput: document.getElementById('file-input'),
    fileSelected: document.getElementById('file-selected'),
    filenameDisplay: document.getElementById('filename-display'),
    btnRemoveFile: document.getElementById('btn-remove-file'),
    
    // Text input
    textInput: document.getElementById('text-input'),
    charCount: document.getElementById('char-count'),
    
    // Configuración TTS
    ttsEngines: document.querySelectorAll('input[name="tts-engine"]'),
    edgeConfig: document.getElementById('edge-config'),
    gttsConfig: document.getElementById('gtts-config'),
    pyttsx3Config: document.getElementById('pyttsx3-config'),
    edgeVoiceSelect: document.getElementById('edge-voice-select'),
    languageSelect: document.getElementById('language-select'),
    pyttsx3LanguageSelect: document.getElementById('pyttsx3-language-select'),
    speedSlider: document.getElementById('speed-slider'),
    speedValue: document.getElementById('speed-value'),
    
    // Preview y resultado
    textPreview: document.getElementById('text-preview'),
    btnEditText: document.getElementById('btn-edit-text'),
    btnConvert: document.getElementById('btn-convert'),
    resultPanel: document.getElementById('result-panel'),
    loadingPanel: document.getElementById('loading-panel'),
    audioPlayer: document.getElementById('audio-player'),
    downloadLink: document.getElementById('download-link'),
    btnNewConversion: document.getElementById('btn-new-conversion'),
    
    // Alertas
    alerts: document.getElementById('alerts')
};

// ============================================
// INICIALIZACIÓN
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkHealth();
});

function setupEventListeners() {
    // Cambio de modo
    elements.btnModeFile.addEventListener('click', () => setMode('file'));
    elements.btnModeText.addEventListener('click', () => setMode('text'));
    
    // File upload
    elements.dropZone.addEventListener('click', () => elements.fileInput.click());
    elements.dropZone.addEventListener('dragover', handleDragOver);
    elements.dropZone.addEventListener('dragleave', handleDragLeave);
    elements.dropZone.addEventListener('drop', handleDrop);
    elements.fileInput.addEventListener('change', handleFileSelect);
    elements.btnRemoveFile.addEventListener('click', removeFile);
    
    // Text input
    elements.textInput.addEventListener('input', handleTextInput);
    
    // Configuración TTS
    elements.ttsEngines.forEach(radio => {
        radio.addEventListener('change', handleTTSChange);
    });
    elements.speedSlider.addEventListener('input', (e) => {
        elements.speedValue.textContent = e.target.value + 'x';
    });
    
    // Conversión
    elements.btnConvert.addEventListener('click', convertToAudio);
    elements.btnNewConversion.addEventListener('click', resetConversion);
}

// ============================================
// FUNCIONES DE MODO
// ============================================

function setMode(mode) {
    state.mode = mode;
    
    if (mode === 'file') {
        elements.btnModeFile.classList.add('bg-indigo-600', 'text-white');
        elements.btnModeFile.classList.remove('bg-gray-100', 'text-gray-600');
        elements.btnModeText.classList.add('bg-gray-100', 'text-gray-600');
        elements.btnModeText.classList.remove('bg-indigo-600', 'text-white');
        elements.panelFile.classList.remove('hidden');
        elements.panelText.classList.add('hidden');
    } else {
        elements.btnModeText.classList.add('bg-indigo-600', 'text-white');
        elements.btnModeText.classList.remove('bg-gray-100', 'text-gray-600');
        elements.btnModeFile.classList.add('bg-gray-100', 'text-gray-600');
        elements.btnModeFile.classList.remove('bg-indigo-600', 'text-white');
        elements.panelFile.classList.add('hidden');
        elements.panelText.classList.remove('hidden');
    }
    
    updatePreview();
    updateConvertButton();
}

// ============================================
// FILE UPLOAD
// ============================================

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

async function processFile(file) {
    const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(ext)) {
        showAlert('error', 'Formato no soportado. Usa: PDF, DOC, DOCX o TXT');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        showAlert('error', 'Archivo muy grande. Máximo 10MB');
        return;
    }
    
    state.currentFile = file;
    elements.filenameDisplay.textContent = file.name;
    elements.fileSelected.classList.remove('hidden');
    elements.dropZone.classList.add('hidden');
    
    // Extraer texto
    await extractTextFromFile(file);
}

async function extractTextFromFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showAlert('info', 'Extrayendo texto del archivo...');
        
        const response = await fetch(`${API_BASE_URL}/api/extract-text`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error extrayendo texto');
        }
        
        const data = await response.json();
        state.extractedText = data.text;
        
        updatePreview();
        updateConvertButton();
        
        showAlert('success', `Texto extraído: ${data.char_count} caracteres`);
        
    } catch (error) {
        showAlert('error', error.message);
        removeFile();
    }
}

function removeFile(e) {
    if (e) e.stopPropagation();
    
    state.currentFile = null;
    state.extractedText = '';
    elements.fileInput.value = '';
    elements.fileSelected.classList.add('hidden');
    elements.dropZone.classList.remove('hidden');
    
    updatePreview();
    updateConvertButton();
}

// ============================================
// TEXT INPUT
// ============================================

function handleTextInput(e) {
    const text = e.target.value;
    state.extractedText = text;
    elements.charCount.textContent = `${text.length} caracteres`;
    
    updatePreview();
    updateConvertButton();
}

// ============================================
// PREVIEW
// ============================================

function updatePreview() {
    const text = state.extractedText;
    
    if (!text) {
        elements.textPreview.innerHTML = `
            <p class="text-gray-400 text-center mt-20">
                <i class="fas fa-file-import text-3xl mb-2"></i><br>
                Sube un archivo o pega texto para ver la vista previa
            </p>
        `;
        elements.btnEditText.classList.add('hidden');
        return;
    }
    
    // Escapar HTML
    const escaped = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br>');
    
    elements.textPreview.innerHTML = escaped;
    elements.btnEditText.classList.remove('hidden');
}

// ============================================
// CONFIGURACIÓN TTS
// ============================================

function handleTTSChange(e) {
    state.ttsEngine = e.target.value;
    
    // Ocultar todos los configs primero
    elements.edgeConfig.classList.add('hidden');
    elements.gttsConfig.classList.add('hidden');
    elements.pyttsx3Config.classList.add('hidden');
    
    // Mostrar el config correspondiente
    if (state.ttsEngine === 'edge') {
        elements.edgeConfig.classList.remove('hidden');
    } else if (state.ttsEngine === 'gtts') {
        elements.gttsConfig.classList.remove('hidden');
    } else if (state.ttsEngine === 'pyttsx3') {
        elements.pyttsx3Config.classList.remove('hidden');
    }
    
    updateConvertButton();
}

// Obtener el idioma según el motor seleccionado
function getSelectedLanguage() {
    if (state.ttsEngine === 'pyttsx3') {
        return elements.pyttsx3LanguageSelect.value;
    } else if (state.ttsEngine === 'edge') {
        // Para Edge TTS, extraer el idioma de la voz seleccionada
        const voiceId = elements.edgeVoiceSelect.value;
        if (voiceId.startsWith('es-')) return 'es';
        if (voiceId.startsWith('en-')) return 'en';
        return 'es';
    }
    return elements.languageSelect.value;
}

// Obtener la voz seleccionada según el motor
function getSelectedVoice() {
    if (state.ttsEngine === 'edge') {
        return elements.edgeVoiceSelect.value;
    }
    return null;
}

// ============================================
// CONVERSIÓN
// ============================================

function updateConvertButton() {
    const hasContent = state.extractedText.length >= 10;
    elements.btnConvert.disabled = !hasContent || state.isConverting;
}

async function convertToAudio() {
    if (state.isConverting) return;
    
    state.isConverting = true;
    updateConvertButton();
    
    elements.loadingPanel.classList.remove('hidden');
    elements.resultPanel.classList.add('hidden');
    
    try {
        let response;
        
        if (state.mode === 'file' && state.currentFile) {
            // Convertir archivo directamente
            const formData = new FormData();
            formData.append('file', state.currentFile);
            formData.append('engine', state.ttsEngine);
            formData.append('language', getSelectedLanguage());
            formData.append('speed', elements.speedSlider.value);
            
            const voice = getSelectedVoice();
            if (voice) {
                formData.append('voice', voice);
            }
            
            response = await fetch(`${API_BASE_URL}/api/convert-file`, {
                method: 'POST',
                body: formData
            });
            
        } else {
            // Convertir texto directo
            const body = {
                text: state.extractedText,
                engine: state.ttsEngine,
                language: getSelectedLanguage(),
                speed: parseFloat(elements.speedSlider.value)
            };
            
            const voice = getSelectedVoice();
            if (voice) {
                body.voice = voice;
            }
            
            response = await fetch(`${API_BASE_URL}/api/text-to-speech`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error en conversión');
        }
        
        // Obtener blob del audio
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const filename = response.headers.get('content-disposition')?.match(/filename="(.+)"/)?.[1] || 'audio.mp3';
        
        // Mostrar resultado
        elements.audioPlayer.src = url;
        elements.downloadLink.href = url;
        elements.downloadLink.download = filename;
        
        elements.loadingPanel.classList.add('hidden');
        elements.resultPanel.classList.remove('hidden');
        
        showAlert('success', '¡Audio generado exitosamente!');
        
    } catch (error) {
        elements.loadingPanel.classList.add('hidden');
        showAlert('error', error.message);
    } finally {
        state.isConverting = false;
        updateConvertButton();
    }
}

function resetConversion() {
    elements.resultPanel.classList.add('hidden');
    elements.audioPlayer.src = '';
    
    if (state.mode === 'file') {
        removeFile();
    } else {
        elements.textInput.value = '';
        state.extractedText = '';
        elements.charCount.textContent = '0 caracteres';
        updatePreview();
        updateConvertButton();
    }
}

// ============================================
// UTILIDADES
// ============================================

function showAlert(type, message) {
    const alertClass = {
        'success': 'bg-green-100 border-green-400 text-green-800',
        'error': 'bg-red-100 border-red-400 text-red-800',
        'info': 'bg-blue-100 border-blue-400 text-blue-800'
    }[type] || 'bg-gray-100 border-gray-400 text-gray-800';
    
    const icon = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'info': 'fa-info-circle'
    }[type] || 'fa-info-circle';
    
    elements.alerts.innerHTML = `
        <div class="${alertClass} border px-4 py-3 rounded-xl flex items-center fade-in">
            <i class="fas ${icon} mr-3"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()" class="ml-auto text-current hover:opacity-75">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        const alert = elements.alerts.firstElementChild;
        if (alert) {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }
    }, 5000);
}

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`, {
            method: 'GET',
            signal: AbortSignal.timeout(5000)
        });
        
        if (response.ok) {
            console.log('✅ Backend conectado');
        }
    } catch (error) {
        console.warn('⚠️ Backend no disponible:', error.message);
        showAlert('info', 'Conectando al servidor...');
    }
}
