// Payment Gateway Integration JavaScript

document.addEventListener('DOMContentLoaded', function() {
    try {
        // Initialize tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Payment Gateway Selection
        const paymentCards = document.querySelectorAll('.payment-gateway-card');
        paymentCards.forEach(card => {
            card.addEventListener('click', function() {
                // Remove selection from all cards
                paymentCards.forEach(c => c.classList.remove('selected'));
                // Add selection to clicked card
                this.classList.add('selected');
                
                // Add ripple effect
                createRipple(this, event);
            });
        });

        // Auto-dismiss alerts
        setTimeout(function() {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => {
                if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
                    try {
                        const bsAlert = new bootstrap.Alert(alert);
                        bsAlert.close();
                    } catch (e) {
                        alert.remove();
                    }
                }
            });
        }, 5000);

        // Form validation
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });

        // Payment status checker
        const orderStatusElements = document.querySelectorAll('[data-order-id]');
        orderStatusElements.forEach(element => {
            const orderId = element.dataset.orderId;
            if (orderId) {
                checkPaymentStatus(orderId);
            }
        });

        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    } catch (error) {
        console.error('Error initializing page:', error);
    }
});

// Create ripple effect
function createRipple(element, event) {
    if (!element || !event) return;
    
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    element.appendChild(ripple);
    
    setTimeout(() => {
        if (ripple.parentNode) {
            ripple.remove();
        }
    }, 600);
}

// Check payment status
function checkPaymentStatus(orderId) {
    fetch(`/payment/payment-status/${orderId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updatePaymentStatus(orderId, data);
            }
        })
        .catch(error => {
            console.error('Error checking payment status:', error);
        });
}

// Update payment status in UI
function updatePaymentStatus(orderId, data) {
    const statusElement = document.querySelector(`[data-order-status="${orderId}"]`);
    if (statusElement) {
        if (data.is_paid) {
            statusElement.innerHTML = '<span class="badge bg-success">Paid</span>';
        } else {
            statusElement.innerHTML = '<span class="badge bg-warning">Pending</span>';
        }
    } else {
        console.warn(`Status element not found for order ${orderId}`);
    }
}

// Loading state management
function showLoading(element) {
    if (!element) return;
    const originalText = element.innerHTML;
    element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
    element.disabled = true;
    element.dataset.originalText = originalText;
}

function hideLoading(element) {
    if (!element) return;
    element.innerHTML = element.dataset.originalText || element.innerHTML;
    element.disabled = false;
}

// Payment form submission
function submitPaymentForm(gateway, buttonElement) {
    const form = document.getElementById(`${gateway}-form`);
    if (!form) {
        console.error(`Form with ID ${gateway}-form not found`);
        return;
    }
    
    // Use the passed button element or find one in the form
    const submitButton = buttonElement || form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        showLoading(submitButton);
    }
    
    setTimeout(() => {
        form.submit();
    }, 1000);
}

// Copy to clipboard
function copyToClipboard(text, element) {
    if (!element) {
        console.error('Element not provided for copyToClipboard');
        return;
    }
    
    navigator.clipboard.writeText(text).then(() => {
        const originalText = element.innerHTML;
        element.innerHTML = 'Copied!';
        element.classList.add('btn-success');
        
        setTimeout(() => {
            element.innerHTML = originalText;
            element.classList.remove('btn-success');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        showError('Failed to copy to clipboard');
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-NP', {
        style: 'currency',
        currency: 'NPR',
        minimumFractionDigits: 0
    }).format(amount);
}

// Validate amount
function validateAmount(amount) {
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
        return { valid: false, message: 'Please enter a valid amount' };
    }
    if (numAmount < 10) {
        return { valid: false, message: 'Minimum amount is Rs. 10' };
    }
    if (numAmount > 100000) {
        return { valid: false, message: 'Maximum amount is Rs. 100,000' };
    }
    return { valid: true, message: '' };
}

// Real-time amount validation
document.addEventListener('input', function(e) {
    if (e.target.name === 'amount') {
        const validation = validateAmount(e.target.value);
        const feedback = e.target.nextElementSibling;
        
        if (!validation.valid) {
            e.target.classList.add('is-invalid');
            if (feedback && feedback.classList.contains('invalid-feedback')) {
                feedback.textContent = validation.message;
            }
        } else {
            e.target.classList.remove('is-invalid');
            e.target.classList.add('is-valid');
        }
    }
});

// Progress tracking
function updateProgress(step) {
    const steps = ['order', 'payment', 'success'];
    const progressBar = document.querySelector('.progress-bar');
    const currentStepIndex = steps.indexOf(step);
    
    if (progressBar && currentStepIndex !== -1) {
        const progress = ((currentStepIndex + 1) / steps.length) * 100;
        progressBar.style.width = progress + '%';
        progressBar.setAttribute('aria-valuenow', progress);
    } else if (!progressBar) {
        console.warn('Progress bar element not found');
    }
}

// Error handling
function showError(message, type = 'danger') {
    const alertContainer = document.querySelector('.alert-container') || document.querySelector('.container') || document.body;
    if (!alertContainer) {
        console.error('No container found for alert message:', message);
        return;
    }
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.insertBefore(alert, alertContainer.firstChild);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        if (alert && alert.parentNode) {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                alert.remove();
            }
        }
    }, 5000);
}

// Success message
function showSuccess(message) {
    showError(message, 'success');
}

// Khalti payment integration
function initiateKhaltiPayment(orderId, amount, publicKey) {
    const config = {
        "publicKey": publicKey,
        "productIdentity": orderId,
        "productName": "Order Payment",
        "productUrl": window.location.origin,
        "paymentPreference": [
            "KHALTI",
            "EBANKING",
            "MOBILE_BANKING",
            "CONNECT_IPS",
            "SCT"
        ],
        "eventHandler": {
            onSuccess(payload) {
                console.log(payload);
                // Verify payment on server
                verifyKhaltiPayment(payload.token, orderId);
            },
            onError(error) {
                console.log(error);
                showError('Payment failed. Please try again.');
            },
            onClose() {
                console.log('Payment widget closed');
            }
        }
    };

    const checkout = new KhaltiCheckout(config);
    checkout.show({ amount: amount * 100 }); // Convert to paisa
}

// Verify Khalti payment
function verifyKhaltiPayment(token, orderId) {
    fetch('/payment/khalti-verify/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            token: token,
            order_id: orderId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = `/payment/order-success/${orderId}/`;
        } else {
            showError('Payment verification failed. Please contact support.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('An error occurred during payment verification.');
    });
}

// Get CSRF token
function getCsrfToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

// Initialize page based on URL
function initializePage() {
    const path = window.location.pathname;
    
    if (path.includes('checkout')) {
        updateProgress('payment');
    } else if (path.includes('success')) {
        updateProgress('success');
        confetti(); // Add confetti animation for success page
    } else if (path.includes('order-list')) {
        updateProgress('order');
    }
}

// Confetti animation for success page
function confetti() {
    // Simple confetti implementation
    for (let i = 0; i < 50; i++) {
        createConfettiPiece();
    }
}

function createConfettiPiece() {
    const confetti = document.createElement('div');
    confetti.style.position = 'fixed';
    confetti.style.width = '10px';
    confetti.style.height = '10px';
    confetti.style.backgroundColor = getRandomColor();
    confetti.style.left = Math.random() * 100 + 'vw';
    confetti.style.top = '-10px';
    confetti.style.zIndex = '9999';
    confetti.style.borderRadius = '50%';
    
    document.body.appendChild(confetti);
    
    const animation = confetti.animate([
        { transform: 'translateY(0) rotate(0deg)', opacity: 1 },
        { transform: `translateY(100vh) rotate(${Math.random() * 360}deg)`, opacity: 0 }
    ], {
        duration: Math.random() * 2000 + 1000,
        easing: 'ease-out'
    });
    
    animation.onfinish = () => confetti.remove();
}

function getRandomColor() {
    const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3', '#54a0ff'];
    return colors[Math.floor(Math.random() * colors.length)];
}

// Copy Order ID to clipboard (for orders page)
function copyOrderId(orderId) {
    navigator.clipboard.writeText(orderId).then(() => {
        showSuccess('Order ID copied to clipboard!');
    }).catch(() => {
        showError('Failed to copy Order ID');
    });
}

// Filter orders (for orders page)
function filterOrders(filter) {
    const table = document.getElementById('ordersTable');
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const status = row.dataset.orderStatus;
        if (filter === 'all' || status === filter) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Refresh orders (for orders page)
function refreshOrders() {
    location.reload();
}

// Export orders (for orders page)
function exportOrders() {
    showError('Export functionality coming soon!', 'info');
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initializePage);

// Create ripple effect
function createRipple(element, event) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Check payment status
function checkPaymentStatus(orderId) {
    fetch(`/payment/payment-status/${orderId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updatePaymentStatus(orderId, data);
            }
        })
        .catch(error => {
            console.error('Error checking payment status:', error);
        });
}

// Update payment status in UI
function updatePaymentStatus(orderId, data) {
    const statusElement = document.querySelector(`[data-order-status="${orderId}"]`);
    if (statusElement) {
        if (data.is_paid) {
            statusElement.innerHTML = '<span class="badge bg-success">Paid</span>';
        } else {
            statusElement.innerHTML = '<span class="badge bg-warning">Pending</span>';
        }
    } else {
        console.warn(`Status element not found for order ${orderId}`);
    }
}

// Loading state management
function showLoading(element) {
    if (!element) return;
    const originalText = element.innerHTML;
    element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
    element.disabled = true;
    element.dataset.originalText = originalText;
}

function hideLoading(element) {
    if (!element) return;
    element.innerHTML = element.dataset.originalText || element.innerHTML;
    element.disabled = false;
}

// Payment form submission
function submitPaymentForm(gateway) {
    const form = document.getElementById(`${gateway}-form`);
    if (!form) {
        console.error(`Form with ID ${gateway}-form not found`);
        return;
    }
    
    // Find the button that triggered this function
    const submitButton = event ? event.target : form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        showLoading(submitButton);
    }
    
    setTimeout(() => {
        form.submit();
    }, 1000);
}

// Copy to clipboard
function copyToClipboard(text, element) {
    if (!element) {
        console.error('Element not provided for copyToClipboard');
        return;
    }
    
    navigator.clipboard.writeText(text).then(() => {
        const originalText = element.innerHTML;
        element.innerHTML = 'Copied!';
        element.classList.add('btn-success');
        
        setTimeout(() => {
            element.innerHTML = originalText;
            element.classList.remove('btn-success');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        showError('Failed to copy to clipboard');
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-NP', {
        style: 'currency',
        currency: 'NPR',
        minimumFractionDigits: 0
    }).format(amount);
}

// Validate amount
function validateAmount(amount) {
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount) || numAmount <= 0) {
        return { valid: false, message: 'Please enter a valid amount' };
    }
    if (numAmount < 10) {
        return { valid: false, message: 'Minimum amount is Rs. 10' };
    }
    if (numAmount > 100000) {
        return { valid: false, message: 'Maximum amount is Rs. 100,000' };
    }
    return { valid: true, message: '' };
}

// Real-time amount validation
document.addEventListener('input', function(e) {
    if (e.target.name === 'amount') {
        const validation = validateAmount(e.target.value);
        const feedback = e.target.nextElementSibling;
        
        if (!validation.valid) {
            e.target.classList.add('is-invalid');
            if (feedback && feedback.classList.contains('invalid-feedback')) {
                feedback.textContent = validation.message;
            }
        } else {
            e.target.classList.remove('is-invalid');
            e.target.classList.add('is-valid');
        }
    }
});

// Progress tracking
function updateProgress(step) {
    const steps = ['order', 'payment', 'success'];
    const progressBar = document.querySelector('.progress-bar');
    const currentStepIndex = steps.indexOf(step);
    
    if (progressBar && currentStepIndex !== -1) {
        const progress = ((currentStepIndex + 1) / steps.length) * 100;
        progressBar.style.width = progress + '%';
        progressBar.setAttribute('aria-valuenow', progress);
    } else if (!progressBar) {
        console.warn('Progress bar element not found');
    }
}

// Error handling
function showError(message, type = 'danger') {
    const alertContainer = document.querySelector('.alert-container') || document.querySelector('.container') || document.body;
    if (!alertContainer) {
        console.error('No container found for alert message:', message);
        return;
    }
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.insertBefore(alert, alertContainer.firstChild);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        if (alert && alert.parentNode) {
            try {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } catch (e) {
                alert.remove();
            }
        }
    }, 5000);
}

// Success message
function showSuccess(message) {
    showError(message, 'success');
}

// Khalti payment integration
function initiateKhaltiPayment(orderId, amount, publicKey) {
    const config = {
        "publicKey": publicKey,
        "productIdentity": orderId,
        "productName": "Order Payment",
        "productUrl": window.location.origin,
        "paymentPreference": [
            "KHALTI",
            "EBANKING",
            "MOBILE_BANKING",
            "CONNECT_IPS",
            "SCT"
        ],
        "eventHandler": {
            onSuccess(payload) {
                console.log(payload);
                // Verify payment on server
                verifyKhaltiPayment(payload.token, orderId);
            },
            onError(error) {
                console.log(error);
                showError('Payment failed. Please try again.');
            },
            onClose() {
                console.log('Payment widget closed');
            }
        }
    };

    const checkout = new KhaltiCheckout(config);
    checkout.show({ amount: amount * 100 }); // Convert to paisa
}

// Verify Khalti payment
function verifyKhaltiPayment(token, orderId) {
    fetch('/payment/khalti-verify/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            token: token,
            order_id: orderId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = `/payment/order-success/${orderId}/`;
        } else {
            showError('Payment verification failed. Please contact support.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showError('An error occurred during payment verification.');
    });
}

// Get CSRF token
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Initialize page based on URL
function initializePage() {
    const path = window.location.pathname;
    
    if (path.includes('checkout')) {
        updateProgress('payment');
    } else if (path.includes('success')) {
        updateProgress('success');
        confetti(); // Add confetti animation for success page
    } else if (path.includes('order-list')) {
        updateProgress('order');
    }
}

// Confetti animation for success page
function confetti() {
    // Simple confetti implementation
    for (let i = 0; i < 50; i++) {
        createConfettiPiece();
    }
}

function createConfettiPiece() {
    const confetti = document.createElement('div');
    confetti.style.position = 'fixed';
    confetti.style.width = '10px';
    confetti.style.height = '10px';
    confetti.style.backgroundColor = getRandomColor();
    confetti.style.left = Math.random() * 100 + 'vw';
    confetti.style.top = '-10px';
    confetti.style.zIndex = '9999';
    confetti.style.borderRadius = '50%';
    
    document.body.appendChild(confetti);
    
    const animation = confetti.animate([
        { transform: 'translateY(0) rotate(0deg)', opacity: 1 },
        { transform: `translateY(100vh) rotate(${Math.random() * 360}deg)`, opacity: 0 }
    ], {
        duration: Math.random() * 2000 + 1000,
        easing: 'ease-out'
    });
    
    animation.onfinish = () => confetti.remove();
}

function getRandomColor() {
    const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3', '#54a0ff'];
    return colors[Math.floor(Math.random() * colors.length)];
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initializePage);
