document.addEventListener('DOMContentLoaded', function() {
    // Get the form element
    const analysisForm = document.getElementById('analysis-form');
    
    // Add loading indicator functions
    function showLoading() {
        // Create loading overlay if it doesn't exist
        if (!document.getElementById('loading-overlay')) {
            const loadingOverlay = document.createElement('div');
            loadingOverlay.id = 'loading-overlay';
            loadingOverlay.style.position = 'fixed';
            loadingOverlay.style.top = '0';
            loadingOverlay.style.left = '0';
            loadingOverlay.style.width = '100%';
            loadingOverlay.style.height = '100%';
            loadingOverlay.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
            loadingOverlay.style.display = 'flex';
            loadingOverlay.style.justifyContent = 'center';
            loadingOverlay.style.alignItems = 'center';
            loadingOverlay.style.zIndex = '1000';
            
            const loadingSpinner = document.createElement('div');
            loadingSpinner.style.border = '5px solid #f3f3f3';
            loadingSpinner.style.borderTop = '5px solid #3498db';
            loadingSpinner.style.borderRadius = '50%';
            loadingSpinner.style.width = '50px';
            loadingSpinner.style.height = '50px';
            loadingSpinner.style.animation = 'spin 2s linear infinite';
            
            // Add the animation
            const style = document.createElement('style');
            style.innerHTML = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
            
            loadingOverlay.appendChild(loadingSpinner);
            document.body.appendChild(loadingOverlay);
        } else {
            document.getElementById('loading-overlay').style.display = 'flex';
        }
    }
    
    function hideLoading() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }
    
    // Function to validate the form
    function validateForm() {
        const csvFile = document.getElementById('csv_file').files[0];
        const modelName = document.getElementById('model_name').value;
        
        if (!csvFile) {
            alert('Please select a CSV file to upload.');
            return false;
        }
        
        if (!modelName) {
            alert('Please select a GenAI model.');
            return false;
        }
        
        // Check if file is a CSV
        if (!csvFile.name.toLowerCase().endsWith('.csv')) {
            alert('Please upload a file with .csv extension.');
            return false;
        }
        
        return true;
    }
    
    // Add event listener for form submission
    if (analysisForm) {
        analysisForm.addEventListener('submit', function(event) {
            // We don't prevent default because we want the form to submit normally
            // This is because we're using server-side rendering for the results
            
            // Validate the form
            if (!validateForm()) {
                event.preventDefault();
                return;
            }
            
            // Show loading indicator
            showLoading();
        });
    }
    
    // Hide loading indicator when page loads (in case it was left visible)
    hideLoading();
});
