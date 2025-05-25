# Prompt Inspector and Optimizer

A tool to analyze and optimize prompts for AI models, helping users create more effective prompts without expensive fine-tuning.

## Features

- Rule-based prompt analysis for immediate feedback
- LLM-based analysis for deeper insights (optional)
- Visualization of prompt quality across key dimensions
- Specific optimization suggestions with explanations
- Before/after comparison of prompts
- Educational tooltips explaining prompt engineering concepts
- Queue-based rate limiting for API calls

## Tech Stack

- **Backend**: Python with FastAPI
- **Frontend**: HTML, CSS, JavaScript with Chart.js
- **API Integration**: Support for various LLM providers (OpenAI, Anthropic, OpenRouter)

## Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/prompt-inspector-prototype.git
   cd prompt-inspector-prototype
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file to add your LLM API keys if you want to use LLM-based analysis.

### Running the Application

1. Start the server using the run script:
   ```
   python run.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

## Usage

1. Enter your prompt in the text area
2. Select your target model from the dropdown
   - Free models are available (Llama 3.3, Mistral, Gemma)
   - Paid models require an API key (OpenAI, Anthropic)
3. Choose whether to use detailed LLM analysis (requires API key for paid models)
4. Click "Analyze Prompt"
5. Review the analysis results, including:
   - Overall score and dimension scores visualization
   - Strengths and weaknesses
   - Before/after comparison of your prompt
   - Specific optimization suggestions with explanations
6. Copy the optimized prompt to use with your preferred AI model

## Development

### Project Structure

```
prompt-inspector-prototype/
├── app/
│   ├── api/
│   │   └── prompt_analysis.py
│   ├── core/
│   │   ├── analyzer.py
│   │   ├── optimizer.py
│   │   ├── llm_analyzer.py
│   │   └── rate_limiter.py
│   ├── models/
│   └── main.py
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── main.js
│   └── images/
├── templates/
│   └── index.html
├── tests/
├── .env.example
├── requirements.txt
├── run.py
└── README.md
```

### Environment Variables

The following environment variables can be set in your `.env` file:

- `PORT`: The port to run the server on (default: 8000)
- `HOST`: The host to bind to (default: 0.0.0.0)
- `DEBUG`: Enable debug mode with hot reloading (default: True)
- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `OPENROUTER_API_KEY`: Your OpenRouter API key

### Running Tests

```
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the 35-dimension prompt evaluation framework
- Inspired by existing prompt optimization tools like PromptPerfect and Promptify
