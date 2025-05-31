// Main JavaScript for Prompt Inspector and Optimizer

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const promptForm = document.getElementById('prompt-form');
    const promptInput = document.getElementById('prompt-input');
    const modelSelect = document.getElementById('model-select');
    const modelValidationMessage = document.getElementById('model-validation-message');
    const detailedAnalysis = document.getElementById('detailed-analysis');
    const apiKeySection = document.getElementById('api-key-section');
    const apiKeyInput = document.getElementById('api-key-input');
    const toggleApiKey = document.getElementById('toggle-api-key');
    const analyzeButton = document.getElementById('analyze-button');
    const backButton = document.getElementById('back-button');
    const errorBackButton = document.getElementById('error-back-button');
    const copyButton = document.getElementById('copy-button');
    
    const inputSection = document.getElementById('input-section');
    const resultsSection = document.getElementById('results-section');
    const loadingSection = document.getElementById('loading-section');
    const errorSection = document.getElementById('error-section');
    const errorMessage = document.getElementById('error-message');
    
    const overallScoreValue = document.getElementById('overall-score-value');
    const strengthsList = document.getElementById('strengths-list');
    const weaknessesList = document.getElementById('weaknesses-list');
    const suggestionsContainer = document.getElementById('suggestions-container');
    const originalPromptDisplay = document.getElementById('original-prompt-display');
    const optimizedPromptDisplay = document.getElementById('optimized-prompt-display');
    
    // Chart instance
    let radarChart = null;
    
    // Event Listeners
    promptForm.addEventListener('submit', handleFormSubmit);
    backButton.addEventListener('click', showInputSection);
    errorBackButton.addEventListener('click', showInputSection);
    copyButton.addEventListener('click', copyOptimizedPrompt);
    detailedAnalysis.addEventListener('change', toggleApiKeyField);
    toggleApiKey.addEventListener('click', toggleApiKeyVisibility);
    modelSelect.addEventListener('change', handleModelChange);
    
    // Toggle API key field visibility based on detailed analysis checkbox
    function toggleApiKeyField() {
        if (detailedAnalysis.checked) {
            apiKeySection.classList.remove('hidden');
        } else {
            apiKeySection.classList.add('hidden');
        }
    }
    
    // Toggle API key visibility (show/hide password)
    function toggleApiKeyVisibility() {
        if (apiKeyInput.type === 'password') {
            apiKeyInput.type = 'text';
            toggleApiKey.textContent = '🔒';
        } else {
            apiKeyInput.type = 'password';
            toggleApiKey.textContent = '👁️';
        }
    }
    
    // Handle model selection change
    function handleModelChange() {
        const selectedModel = modelSelect.value;
        
        // Update placeholder text based on selected model
        if (selectedModel.includes('gpt')) {
            apiKeyInput.placeholder = 'Enter your OpenAI API key';
        } else if (selectedModel.includes('claude')) {
            apiKeyInput.placeholder = 'Enter your Anthropic API key';
        } else if (selectedModel.includes('openrouter')) {
            apiKeyInput.placeholder = 'Enter your OpenRouter API key';
        } else {
            apiKeyInput.placeholder = 'Enter your API key';
        }
        
        // Clear validation message
        modelValidationMessage.textContent = '';
        
        // If detailed analysis is checked, show API key field
        if (detailedAnalysis.checked) {
            apiKeySection.classList.remove('hidden');
        }
    }
    
    // Handle form submission
    async function handleFormSubmit(event) {
        event.preventDefault();
        
        // Validate prompt text
        const promptText = promptInput.value.trim();
        if (!promptText) {
            alert('Please enter a prompt to analyze.');
            promptInput.focus();
            return;
        }
        
        // Validate model selection
        const selectedModel = modelSelect.value;
        if (!selectedModel) {
            modelValidationMessage.textContent = 'Please select a model.';
            modelSelect.focus();
            return;
        }
        
        // Check if API key is required but not provided
        if (detailedAnalysis.checked && !apiKeyInput.value.trim()) {
            alert('Please enter an API key for detailed analysis or uncheck the detailed analysis option.');
            apiKeyInput.focus();
            return;
        }
        
        showLoadingSection();
        
        try {
            const response = await analyzePrompt(
                promptText,
                selectedModel,
                detailedAnalysis.checked,
                apiKeyInput.value.trim()
            );
            
            displayResults(response, promptText);
            showResultsSection();
        } catch (error) {
            console.error('Error analyzing prompt:', error);
            errorMessage.textContent = error.message || 'An error occurred while analyzing your prompt. Please try again.';
            showErrorSection();
        }
    }
    
    // API call to analyze prompt
    async function analyzePrompt(promptText, targetModel, detailedAnalysis, apiKey) {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt_text: promptText,
                target_model: targetModel,
                detailed_analysis: detailedAnalysis,
                api_key: apiKey // Send API key with the request
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to analyze prompt');
        }
        
        const result = await response.json();
        
        // If detailed analysis was requested, show a notification
        if (detailedAnalysis) {
            // Add a notification to the UI
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.textContent = 'Detailed LLM analysis requested. Results will be enhanced when available.';
            document.body.appendChild(notification);
            
            // Remove the notification after 5 seconds
            setTimeout(() => {
                notification.style.opacity = '0';
                notification.style.transition = 'opacity 0.5s ease';
                setTimeout(() => {
                    notification.remove();
                }, 500);
            }, 5000);
        }
        
        return result;
    }
    
    // Display analysis results
    function displayResults(results, originalPrompt) {
        // Display overall score (already scaled to 0-5 in backend)
        const overallScore = Math.round(results.overall_score * 10) / 10;
        overallScoreValue.textContent = overallScore.toFixed(1);
        
        // Update score circle color based on score
        const scoreCircle = document.querySelector('.score-circle');
        if (overallScore >= 4) {
            scoreCircle.style.backgroundColor = '#d4edda'; // Green tint
        } else if (overallScore >= 3) {
            scoreCircle.style.backgroundColor = '#fff3cd'; // Yellow tint
        } else {
            scoreCircle.style.backgroundColor = '#f8d7da'; // Red tint
        }
        
        // Display strengths
        strengthsList.innerHTML = '';
        results.strengths.forEach(strength => {
            const li = document.createElement('li');
            li.textContent = strength;
            strengthsList.appendChild(li);
        });
        
        // Display weaknesses
        weaknessesList.innerHTML = '';
        results.weaknesses.forEach(weakness => {
            const li = document.createElement('li');
            li.textContent = weakness;
            weaknessesList.appendChild(li);
        });
        
        // Display suggestions
        suggestionsContainer.innerHTML = '';
        results.suggestions.forEach(suggestion => {
            const card = createSuggestionCard(suggestion);
            suggestionsContainer.appendChild(card);
        });
        
        // Display original and optimized prompts
        originalPromptDisplay.textContent = originalPrompt;
        optimizedPromptDisplay.textContent = results.optimized_prompt;
        
        // Create radar chart
        createRadarChart(results.scores);
    }
    
    // Create a suggestion card
    function createSuggestionCard(suggestion) {
        const card = document.createElement('div');
        card.className = 'suggestion-card';
        
        const title = document.createElement('h4');
        title.textContent = suggestion.title;
        card.appendChild(title);
        
        const description = document.createElement('p');
        description.textContent = suggestion.description;
        card.appendChild(description);
        
        if (suggestion.example) {
            const example = document.createElement('div');
            example.className = 'example';
            example.textContent = suggestion.example;
            card.appendChild(example);
        }
        
        if (suggestion.rationale) {
            const rationale = document.createElement('p');
            rationale.className = 'rationale';
            rationale.textContent = suggestion.rationale;
            card.appendChild(rationale);
        }
        
        return card;
    }
    
    // Create radar chart for dimension scores
    function createRadarChart(scores) {
        // Destroy existing chart if it exists
        if (radarChart) {
            radarChart.destroy();
        }
        
        const ctx = document.getElementById('radar-chart').getContext('2d');
        
        // Prepare data for chart
        const labels = [];
        const data = [];
        
        for (const [dimension, score] of Object.entries(scores)) {
            // Convert dimension ID to readable label
            const label = dimension
                .split('_')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');
            
            labels.push(label);
            // Scale scores from 0-1 to 0-5 for consistency with overall score
            data.push(score * 5);
        }
        
        // Create chart
        radarChart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Dimension Scores',
                    data: data,
                    backgroundColor: 'rgba(74, 111, 165, 0.2)',
                    borderColor: 'rgba(74, 111, 165, 1)',
                    pointBackgroundColor: 'rgba(74, 111, 165, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(74, 111, 165, 1)'
                }]
            },
            options: {
                scales: {
                    r: {
                        angleLines: {
                            display: true
                        },
                        suggestedMin: 0,
                        suggestedMax: 5
                    }
                }
            }
        });
    }
    
    // Copy optimized prompt to clipboard
    function copyOptimizedPrompt() {
        const text = optimizedPromptDisplay.textContent;
        navigator.clipboard.writeText(text).then(() => {
            const originalText = copyButton.textContent;
            copyButton.textContent = 'Copied!';
            setTimeout(() => {
                copyButton.textContent = originalText;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }
    
    // Show/hide sections
    function showInputSection() {
        inputSection.classList.remove('hidden');
        resultsSection.classList.add('hidden');
        loadingSection.classList.add('hidden');
        errorSection.classList.add('hidden');
    }
    
    function showResultsSection() {
        inputSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        loadingSection.classList.add('hidden');
        errorSection.classList.add('hidden');
    }
    
    function showLoadingSection() {
        inputSection.classList.add('hidden');
        resultsSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        errorSection.classList.add('hidden');
    }
    
    function showErrorSection() {
        inputSection.classList.add('hidden');
        resultsSection.classList.add('hidden');
        loadingSection.classList.add('hidden');
        errorSection.classList.remove('hidden');
    }
    
    // Initialize UI state
    toggleApiKeyField();
    handleModelChange();
});
