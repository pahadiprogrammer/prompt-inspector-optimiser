"""
LLM-based prompt analyzer module.

This module contains functions for analyzing prompts using LLM API calls
for deeper, more nuanced analysis.
"""

import os
import json
import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default system prompt for LLM analysis
SYSTEM_PROMPT = """
You are a prompt engineering expert tasked with analyzing and improving prompts for AI models.
Evaluate the prompt based on clarity, specificity, context, structure, examples, and other key dimensions.
Provide specific, actionable feedback on how to improve the prompt.
Your analysis should be detailed, constructive, and focused on helping the user create more effective prompts.
"""

# Default OpenRouter model
DEFAULT_OPENROUTER_MODEL = "meta-llama/llama-3.3-8b-instruct:free"

async def analyze_prompt_with_llm(
    prompt_text: str,
    target_model: str = "general",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze a prompt using an LLM API call.
    
    Args:
        prompt_text: The prompt text to analyze
        target_model: The target model for the prompt
        api_key: Optional API key for the LLM service
        
    Returns:
        Dictionary containing analysis results
    """
    logger.info(f"Starting LLM analysis for target model: {target_model}")
    
    # Use environment variable if no API key provided
    if not api_key:
        logger.info("No API key provided in request, checking environment variables")
        # Try to get API key based on target model
        if target_model == "openrouter" or target_model == "general":
            api_key = os.environ.get("OPENROUTER_API_KEY")
        elif target_model.startswith("gpt"):
            api_key = os.environ.get("OPENAI_API_KEY")
        elif target_model == "claude":
            api_key = os.environ.get("ANTHROPIC_API_KEY")
        else:
            # Default to any available API key
            api_key = (os.environ.get("OPENAI_API_KEY") or 
                      os.environ.get("ANTHROPIC_API_KEY") or 
                      os.environ.get("OPENROUTER_API_KEY"))
    else:
        logger.info("API key provided in request")
    
    # If still no API key, use a free model or return an error
    if not api_key:
        logger.warning("No API key available, falling back to free model")
        return await analyze_with_free_model(prompt_text, target_model)
    
    # Prepare the analysis prompt
    analysis_prompt = """
    Please analyze the following prompt and provide detailed feedback on how to improve it.
    
    PROMPT TO ANALYZE:
    ```
    {0}
    ```
    
    Target AI model: {1}
    
    Evaluate the prompt on the following dimensions:
    1. Clarity & Specificity
    2. Context Provided
    3. Task Definition
    4. Structure & Organization
    5. Examples (if applicable)
    6. Conciseness
    7. Output Format Specification
    8. Role Assignment (if applicable)
    9. Reasoning Guidance
    10. Constraints & Limitations
    
    For each dimension, provide:
    - A score from 1-5
    - Specific strengths
    - Suggestions for improvement
    
    Then provide 3-5 specific, actionable suggestions to improve the overall effectiveness of the prompt.
    
    Format your response as a JSON object with the following structure:
    {{
        "dimension_scores": {{
            "clarity": 4,
            "context": 3,
            ...
        }},
        "strengths": ["strength1", "strength2", ...],
        "weaknesses": ["weakness1", "weakness2", ...],
        "suggestions": [
            {{
                "title": "Suggestion title",
                "description": "Detailed description",
                "example": "Example implementation",
                "rationale": "Why this would help"
            }},
            ...
        ],
        "improved_prompt": "A revised version of the prompt"
    }}
    """.format(prompt_text, target_model)
    
    try:
        # Determine which API to use based on target_model
        if target_model.startswith("openrouter"):
            logger.info("Making API call to OpenRouter")
            # Extract the specific model if provided in the format "openrouter:model-name"
            if ":" in target_model:
                model = target_model.split(":", 1)[1]
                logger.info(f"Using specified OpenRouter model: {model}")
            else:
                model = DEFAULT_OPENROUTER_MODEL
                logger.info(f"Using default OpenRouter model: {model}")
            return await call_openrouter_api(analysis_prompt, api_key, model)
        elif target_model.startswith("gpt"):
            logger.info(f"Making API call to OpenAI with model {target_model}")
            return await call_openai_api(analysis_prompt, api_key, target_model)
        elif target_model == "claude":
            logger.info("Making API call to Anthropic")
            return await call_anthropic_api(analysis_prompt, api_key)
        else:
            # Default to OpenRouter for "general" or unknown models
            logger.info(f"Using default OpenRouter model ({DEFAULT_OPENROUTER_MODEL}) for general analysis")
            return await call_openrouter_api(analysis_prompt, api_key, DEFAULT_OPENROUTER_MODEL)
            
    except Exception as e:
        logger.error(f"Error during LLM analysis: {str(e)}", exc_info=True)
        return {
            "error": f"Failed to analyze prompt with LLM: {str(e)}"
        }

async def call_openrouter_api(prompt: str, api_key: str, model: str = DEFAULT_OPENROUTER_MODEL) -> Dict[str, Any]:
    """Call OpenRouter API"""
    logger.info(f"Sending request to OpenRouter API using model: {model}")
    
    # Set higher token limit for free models
    max_tokens_value = 4000 if "free" in model else 1000
    logger.info(f"Using max_tokens: {max_tokens_value} for model: {model}")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,  # Use the provided model parameter
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": max_tokens_value
            }
        ) as response:
            logger.info(f"Received response from OpenRouter API with status: {response.status}")
            return await process_llm_response(response)

async def call_openai_api(prompt: str, api_key: str, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
    """Call OpenAI API"""
    logger.info(f"Sending request to OpenAI API with model: {model}")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
        ) as response:
            logger.info(f"Received response from OpenAI API with status: {response.status}")
            return await process_llm_response(response)

async def call_anthropic_api(prompt: str, api_key: str) -> Dict[str, Any]:
    """Call Anthropic API"""
    logger.info("Sending request to Anthropic API")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": "claude-2",
                "system": SYSTEM_PROMPT,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
        ) as response:
            logger.info(f"Received response from Anthropic API with status: {response.status}")
            return await process_llm_response(response)

async def process_llm_response(response) -> Dict[str, Any]:
    """Process response from LLM API"""
    if response.status == 200:
        result = await response.json()
        logger.info("Successfully received JSON response from LLM API")
        
        try:
            # Extract content based on API response structure
            if "choices" in result and len(result["choices"]) > 0:
                # OpenAI or OpenRouter format
                content = result["choices"][0]["message"]["content"]
                logger.info("Extracted content from OpenAI/OpenRouter format response")
                # Log a preview of the content
                content_preview = content[:200] + "..." if len(content) > 200 else content
                logger.info(f"Content preview: {content_preview}")
            elif "content" in result:
                # Anthropic format
                content = result["content"][0]["text"]
                logger.info("Extracted content from Anthropic format response")
                # Log a preview of the content
                content_preview = content[:200] + "..." if len(content) > 200 else content
                logger.info(f"Content preview: {content_preview}")
            else:
                logger.error(f"Unexpected API response format: {result.keys()}")
                return {"error": "Unexpected API response format"}
                
            # Extract JSON from the response
            json_str = content.strip()
            
            # Try to find JSON in the response
            # First, look for JSON code blocks
            if "```json" in json_str:
                # Extract content between ```json and ```
                start_idx = json_str.find("```json") + 7
                end_idx = json_str.find("```", start_idx)
                if end_idx != -1:
                    json_str = json_str[start_idx:end_idx].strip()
                    logger.info("Extracted JSON from ```json code block")
            elif "```" in json_str:
                # Extract content between ``` and ```
                start_idx = json_str.find("```") + 3
                end_idx = json_str.find("```", start_idx)
                if end_idx != -1:
                    json_str = json_str[start_idx:end_idx].strip()
                    logger.info("Extracted JSON from ``` code block")
            else:
                # Try to find JSON object directly
                start_idx = json_str.find("{")
                end_idx = json_str.rfind("}") + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = json_str[start_idx:end_idx].strip()
                    logger.info("Extracted JSON object directly from content")
            
            try:
                analysis = json.loads(json_str)
                logger.info("Successfully parsed JSON from LLM response")
            except json.JSONDecodeError:
                # If parsing fails, try to clean up the JSON string
                logger.warning("Initial JSON parsing failed, attempting to clean up the JSON string")
                # Remove any text before the first { and after the last }
                start_idx = json_str.find("{")
                end_idx = json_str.rfind("}") + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = json_str[start_idx:end_idx].strip()
                    analysis = json.loads(json_str)
                    logger.info("Successfully parsed JSON after cleanup")
            
            # Log some key parts of the analysis
            if "dimension_scores" in analysis:
                logger.info(f"Dimension scores: {analysis['dimension_scores']}")
            if "strengths" in analysis and analysis["strengths"]:
                logger.info(f"First strength: {analysis['strengths'][0]}")
            if "weaknesses" in analysis and analysis["weaknesses"]:
                logger.info(f"First weakness: {analysis['weaknesses'][0]}")
            if "suggestions" in analysis and analysis["suggestions"]:
                logger.info(f"First suggestion title: {analysis['suggestions'][0]['title']}")
            
            return analysis
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse LLM response: {str(e)}", exc_info=True)
            logger.error(f"Raw content: {content[:500]}..." if 'content' in locals() else "No content")
            return {
                "error": f"Failed to parse LLM response: {str(e)}",
                "raw_response": content[:1000] if 'content' in locals() else "No content"
            }
    else:
        error_text = await response.text()
        logger.error(f"API request failed with status {response.status}: {error_text}")
        return {
            "error": f"API request failed with status {response.status}",
            "details": error_text
        }

async def analyze_with_free_model(prompt_text: str, target_model: str) -> Dict[str, Any]:
    """
    Analyze a prompt using a free model or service.
    
    This is a fallback when no API key is available.
    
    Args:
        prompt_text: The prompt text to analyze
        target_model: The target model for the prompt
        
    Returns:
        Dictionary containing analysis results
    """
    logger.info("Using free model fallback as no API key is available")
    # This is a placeholder - in a real implementation, this would connect to a free API
    # For now, return a message indicating that LLM analysis requires an API key
    return {
        "note": "Detailed LLM analysis requires an API key. Using rule-based analysis only.",
        "dimension_scores": {},
        "strengths": [],
        "weaknesses": [],
        "suggestions": [
            {
                "title": "Add API key for enhanced analysis",
                "description": "For more detailed analysis, provide an API key in the form.",
                "example": "Enter your API key in the field that appears when 'Detailed Analysis' is checked.",
                "rationale": "LLM-based analysis provides more nuanced feedback on your prompts."
            }
        ]
    }
