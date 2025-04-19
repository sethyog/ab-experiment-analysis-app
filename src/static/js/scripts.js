document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const instructionInput = document.getElementById('instruction-input');
    const modelSelect = document.getElementById('model-select');
    const resultContainer = document.getElementById('result-container');

    uploadForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const formData = new FormData(uploadForm);
        const instructions = instructionInput.value;
        const selectedModel = modelSelect.value;

        formData.append('instructions', instructions);
        formData.append('model', selectedModel);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const result = await response.json();
            displayResult(result);
        } catch (error) {
            console.error('Error:', error);
            resultContainer.innerHTML = 'An error occurred while processing your request.';
        }
    });

    function displayResult(result) {
        resultContainer.innerHTML = `
            <h3>Analysis Summary</h3>
            <p>${result.summary}</p>
            <h4>Recommended Actions</h4>
            <p>${result.recommendations}</p>
        `;
    }
});