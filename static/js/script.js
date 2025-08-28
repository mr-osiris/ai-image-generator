// Main JavaScript for AI Image Generator

class ImageGenerator {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
        this.loadModels();
    }

    initializeElements() {
        this.form = document.getElementById('imageForm');
        this.promptInput = document.getElementById('prompt');
        this.modelSelect = document.getElementById('model');
        this.sizeSelect = document.getElementById('size');
        this.qualitySelect = document.getElementById('quality');
        this.generateBtn = document.getElementById('generateBtn');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsGrid = document.getElementById('resultsGrid');
        this.toggleAdvanced = document.getElementById('toggleAdvanced');
        this.advancedContent = document.getElementById('advancedContent');
    }

    attachEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.toggleAdvanced.addEventListener('click', () => this.toggleAdvancedOptions());
        
        // Auto-resize textarea
        this.promptInput.addEventListener('input', this.autoResizeTextarea);
    }

    autoResizeTextarea() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    }

    toggleAdvancedOptions() {
        const isOpen = this.advancedContent.classList.contains('show');
        
        if (isOpen) {
            this.advancedContent.classList.remove('show');
            this.toggleAdvanced.classList.remove('active');
        } else {
            this.advancedContent.classList.add('show');
            this.toggleAdvanced.classList.add('active');
        }
    }

    async loadModels() {
        try {
            this.modelSelect.innerHTML = '<option value="">Loading models...</option>';
            
            const response = await fetch('/api/models');
            const data = await response.json();
            
            this.modelSelect.innerHTML = '';
            
            if (data.data && data.data.length > 0) {
                data.data.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = `${model.id} (${model.tier})`;
                    this.modelSelect.appendChild(option);
                });
                
                // Select first model by default
                this.modelSelect.value = data.data[0].id;
                this.showToast('Models loaded successfully', 'success');
            } else {
                this.modelSelect.innerHTML = '<option value="">No models available</option>';
                this.showToast('No models available', 'error');
            }
        } catch (error) {
            console.error('Error loading models:', error);
            this.modelSelect.innerHTML = '<option value="">Error loading models</option>';
            this.showToast('Error loading models', 'error');
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const prompt = this.promptInput.value.trim();
        const model = this.modelSelect.value;
        const size = this.sizeSelect.value;
        const quality = this.qualitySelect.value;
        
        if (!prompt) {
            this.showToast('Please enter a prompt', 'error');
            return;
        }
        
        if (!model) {
            this.showToast('Please select a model', 'error');
            return;
        }
        
        this.setLoading(true);
        this.hideResults();
        
        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                    model: model,
                    size: size,
                    quality: quality
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayResults(data.images);
                this.showToast(data.message, 'success');
            } else {
                this.showToast(data.error || 'Failed to generate image', 'error');
            }
        } catch (error) {
            console.error('Error generating image:', error);
            this.showToast('Network error occurred', 'error');
        } finally {
            this.setLoading(false);
        }
    }

    setLoading(loading) {
        if (loading) {
            this.generateBtn.classList.add('loading');
            this.generateBtn.disabled = true;
            this.loadingOverlay.style.display = 'flex';
        } else {
            this.generateBtn.classList.remove('loading');
            this.generateBtn.disabled = false;
            this.loadingOverlay.style.display = 'none';
        }
    }

    hideResults() {
        this.resultsSection.style.display = 'none';
        this.resultsGrid.innerHTML = '';
    }

    displayResults(images) {
        if (!images || images.length === 0) {
            this.showToast('No images generated', 'warning');
            return;
        }
        
        this.resultsGrid.innerHTML = '';
        
        images.forEach(image => {
            const resultItem = this.createResultItem(image);
            this.resultsGrid.appendChild(resultItem);
        });
        
        this.resultsSection.style.display = 'block';
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    createResultItem(image) {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        
        resultItem.innerHTML = `
            <img src="${image.url}" alt="Generated image" class="result-image" loading="lazy">
            <div class="result-info">
                <div class="result-prompt">${image.prompt}</div>
                <div class="result-meta">
                    <span>Model: ${image.model}</span>
                    <button class="download-btn" onclick="downloadImage('${image.url}', '${image.filename}')">
                        <i class="fas fa-download"></i>
                        Download
                    </button>
                </div>
            </div>
        `;
        
        return resultItem;
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = this.getToastIcon(type);
        toast.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${message}</span>
        `;
        
        const container = document.getElementById('toast-container');
        container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Remove toast after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => container.removeChild(toast), 300);
        }, 5000);
    }

    getToastIcon(type) {
        switch (type) {
            case 'success': return 'fa-check-circle';
            case 'error': return 'fa-exclamation-circle';
            case 'warning': return 'fa-exclamation-triangle';
            default: return 'fa-info-circle';
        }
    }
}

// Global function for downloading images
function downloadImage(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Show toast notification
    if (window.imageGenerator) {
        window.imageGenerator.showToast('Download started', 'success');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.imageGenerator = new ImageGenerator();
});

// Add some visual effects
document.addEventListener('DOMContentLoaded', () => {
    // Add floating animation to hero section
    const hero = document.querySelector('.hero');
    if (hero) {
        hero.style.animation = 'fadeInUp 1s ease-out';
    }
    
    // Add stagger animation to form elements
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach((group, index) => {
        group.style.opacity = '0';
        group.style.transform = 'translateY(20px)';
        group.style.animation = `fadeInUp 0.6s ease-out ${index * 0.1}s forwards`;
    });
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    
    .result-item {
        animation: fadeInUp 0.6s ease-out;
    }
    
    .generate-btn:hover {
        animation: pulse 2s infinite;
    }
`;
document.head.appendChild(style);
