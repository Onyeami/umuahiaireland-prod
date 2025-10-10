/**
 * Custom File Upload Alert System
 * Provides feedback for Cloudinary file uploads across all forms
 */

class FileUploadAlerts {
    constructor() {
        this.init();
    }

    init() {
        this.createAlertContainer();
        this.setupFormListeners();
    }

    createAlertContainer() {
        // Create alert container if it doesn't exist
        if (!document.getElementById('upload-alerts-container')) {
            const container = document.createElement('div');
            container.id = 'upload-alerts-container';
            container.className = 'fixed top-4 right-4 z-50 space-y-2';
            container.style.cssText = `
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
    }

    showAlert(message, type = 'info', duration = 5000) {
        const container = document.getElementById('upload-alerts-container');
        const alertId = 'alert-' + Date.now();
        
        // Create alert element
        const alert = document.createElement('div');
        alert.id = alertId;
        alert.className = `upload-alert upload-alert-${type}`;
        
        // Set styles based on type
        const styles = this.getAlertStyles(type);
        alert.style.cssText = styles.base;
        
        // Create alert content
        alert.innerHTML = `
            <div style="${styles.content}">
                <div style="${styles.icon}">${this.getIcon(type)}</div>
                <div style="${styles.message}">${message}</div>
                <button onclick="fileUploadAlerts.removeAlert('${alertId}')" 
                        style="${styles.closeButton}" 
                        aria-label="Close alert">×</button>
            </div>
            <div style="${styles.progressBar}" class="progress-bar"></div>
        `;

        container.appendChild(alert);

        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.removeAlert(alertId);
            }, duration);

            // Animate progress bar
            const progressBar = alert.querySelector('.progress-bar');
            if (progressBar) {
                setTimeout(() => {
                    progressBar.style.width = '0%';
                }, 100);
            }
        }

        // Add entrance animation
        setTimeout(() => {
            alert.style.transform = 'translateX(0)';
            alert.style.opacity = '1';
        }, 10);

        return alertId;
    }

    removeAlert(alertId) {
        const alert = document.getElementById(alertId);
        if (alert) {
            alert.style.transform = 'translateX(100%)';
            alert.style.opacity = '0';
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 300);
        }
    }

    getAlertStyles(type) {
        const colors = {
            success: { bg: '#10b981', border: '#059669', text: '#ffffff' },
            error: { bg: '#ef4444', border: '#dc2626', text: '#ffffff' },
            warning: { bg: '#f59e0b', border: '#d97706', text: '#ffffff' },
            info: { bg: '#3b82f6', border: '#2563eb', text: '#ffffff' },
            uploading: { bg: '#8b5cf6', border: '#7c3aed', text: '#ffffff' }
        };

        const color = colors[type] || colors.info;

        return {
            base: `
                background: ${color.bg};
                border-left: 4px solid ${color.border};
                border-radius: 8px;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                transform: translateX(100%);
                opacity: 0;
                transition: all 0.3s ease-in-out;
                overflow: hidden;
                position: relative;
            `,
            content: `
                display: flex;
                align-items: center;
                padding: 12px 16px;
                color: ${color.text};
            `,
            icon: `
                margin-right: 12px;
                font-size: 18px;
                font-weight: bold;
            `,
            message: `
                flex: 1;
                font-size: 14px;
                line-height: 1.4;
                font-weight: 500;
            `,
            closeButton: `
                background: none;
                border: none;
                color: ${color.text};
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                opacity: 0.7;
                padding: 0;
                margin-left: 8px;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            `,
            progressBar: `
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: rgba(255, 255, 255, 0.3);
                width: 100%;
                transition: width linear;
                transition-duration: ${type === 'uploading' ? '0s' : '5s'};
            `
        };
    }

    getIcon(type) {
        const icons = {
            success: '✓',
            error: '✗',
            warning: '⚠',
            info: 'ℹ',
            uploading: '⟳'
        };
        return icons[type] || icons.info;
    }

    setupFormListeners() {
        // Listen for form submissions on file upload forms
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (this.isFileUploadForm(form)) {
                this.handleFormSubmission(form, e);
            }
        });

        // Listen for file input changes
        document.addEventListener('change', (e) => {
            if (e.target.type === 'file' && e.target.files.length > 0) {
                this.handleFileSelection(e.target);
            }
        });
    }

    isFileUploadForm(form) {
        // Check if form contains file inputs
        return form.querySelector('input[type="file"]') !== null;
    }

    handleFormSubmission(form, event) {
        const fileInputs = form.querySelectorAll('input[type="file"]');
        let hasFiles = false;

        fileInputs.forEach(input => {
            if (input.files && input.files.length > 0) {
                hasFiles = true;
            }
        });

        if (hasFiles) {
            const uploadingAlertId = this.showAlert(
                'Uploading files to Cloudinary... Please wait.',
                'uploading',
                0
            );

            // Store alert ID for later removal
            form.dataset.uploadingAlert = uploadingAlertId;

            // Show progress for large files
            this.showUploadProgress(form);
        }
    }

    handleFileSelection(fileInput) {
        const files = Array.from(fileInput.files);
        let message = '';

        if (files.length === 1) {
            const file = files[0];
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            message = `Selected: ${file.name} (${sizeMB} MB)`;
        } else {
            message = `Selected ${files.length} files`;
        }

        this.showAlert(message, 'info', 3000);
    }

    showUploadProgress(form) {
        // Simulate upload progress for user feedback
        const progressAlert = form.querySelector('.progress-bar');
        if (progressAlert) {
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 20;
                if (progress > 90) {
                    progress = 90; // Don't go to 100% until actual completion
                }
                progressAlert.style.width = progress + '%';
                
                if (progress >= 90) {
                    clearInterval(interval);
                }
            }, 500);
        }
    }

    // Public methods for manual alert triggering
    showSuccess(message, duration = 5000) {
        return this.showAlert(message, 'success', duration);
    }

    showError(message, duration = 7000) {
        return this.showAlert(message, 'error', duration);
    }

    showWarning(message, duration = 6000) {
        return this.showAlert(message, 'warning', duration);
    }

    showInfo(message, duration = 4000) {
        return this.showAlert(message, 'info', duration);
    }

    showUploading(message, duration = 0) {
        return this.showAlert(message, 'uploading', duration);
    }

    // Method to be called when upload completes
    handleUploadComplete(form, success, message) {
        // Remove uploading alert
        if (form.dataset.uploadingAlert) {
            this.removeAlert(form.dataset.uploadingAlert);
            delete form.dataset.uploadingAlert;
        }

        // Show result
        if (success) {
            this.showSuccess(message || 'Files uploaded successfully to Cloudinary!');
        } else {
            this.showError(message || 'Upload failed. Files saved locally as fallback.');
        }
    }
}

// Initialize the alert system when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.fileUploadAlerts = new FileUploadAlerts();
});

// Expose for global access
window.FileUploadAlerts = FileUploadAlerts;