# Prompt Inspector and Optimizer - Continue Development

Use this prompt when continuing development on the prompt inspector and optimizer project in a new session:

```
I'm continuing work on my prompt inspector and optimizer prototype in /Users/yugander/genAi/prompt-inspector-prototype. 
Please review the existing code structure to understand what's been implemented so far, and help me develop [specific feature you want to work on].

Before we start, please analyze the key files including app/main.py, app/core/analyzer.py, and any other relevant components to get a complete understanding of the implementation.
```

Replace `[specific feature you want to work on]` with the particular feature or enhancement you want to implement in that session.

## Key Project Files

- `app/main.py`: FastAPI application setup
- `app/api/prompt_analysis.py`: API endpoints for prompt analysis
- `app/core/analyzer.py`: Rule-based prompt analysis
- `app/core/optimizer.py`: Prompt optimization suggestions
- `app/core/llm_analyzer.py`: LLM-based analysis integration
- `app/core/rate_limiter.py`: Queue-based rate limiting
- `templates/index.html`: Main HTML template
- `static/css/styles.css`: Styling for the web interface
- `static/js/main.js`: Frontend JavaScript

## Project Overview

This prototype analyzes prompts using both rule-based techniques and LLM API calls, provides optimization suggestions, and visualizes prompt quality across key dimensions. It includes features like before/after comparison, educational tooltips, and queue-based rate limiting for API calls.
