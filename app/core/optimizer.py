"""
Prompt optimizer module.

This module contains functions for generating optimization suggestions
based on prompt analysis results.
"""

from typing import Dict, List, Any

def generate_optimization_suggestions(
    prompt_text: str, 
    analysis_results: Dict[str, Any],
    target_model: str = "general"
) -> List[Dict[str, Any]]:
    """
    Generate optimization suggestions based on analysis results.
    
    Args:
        prompt_text: The original prompt text
        analysis_results: Results from the prompt analyzer
        target_model: The target model for optimization
        
    Returns:
        List of optimization suggestions
    """
    suggestions = []
    
    # Get dimension scores
    scores = analysis_results.get("dimension_scores", {})
    
    # Generate suggestions based on low scores
    for dimension, score in scores.items():
        if score < 0.5:
            suggestion = generate_suggestion_for_dimension(dimension, prompt_text, score)
            if suggestion:
                suggestions.append(suggestion)
    
    # Add model-specific suggestions if applicable
    if target_model != "general":
        model_suggestions = generate_model_specific_suggestions(prompt_text, target_model)
        suggestions.extend(model_suggestions)
    
    # Add general improvement suggestions if we have few specific ones
    if len(suggestions) < 2:
        general_suggestions = generate_general_suggestions(prompt_text)
        suggestions.extend(general_suggestions)
    
    return suggestions

def generate_suggestion_for_dimension(dimension: str, prompt_text: str, score: float) -> Dict[str, Any]:
    """Generate a suggestion for improving a specific dimension."""
    
    suggestions = {
        "clarity": {
            "title": "Improve clarity and specificity",
            "description": "Your prompt could benefit from clearer instructions and more specific language.",
            "example": "Instead of 'Tell me about AI', try 'Explain how AI is used in healthcare, focusing on diagnostic applications and patient outcomes'.",
            "rationale": "Clear, specific instructions help the AI understand exactly what you're looking for.",
            "implementation": get_clarity_implementation(prompt_text, score)
        },
        "context": {
            "title": "Add more context or background information",
            "description": "Providing more context would help the AI understand the situation better.",
            "example": "Instead of 'How do I fix this?', try 'I'm working with a Python Flask application that's returning a 500 error when accessing the /users endpoint. The error log shows a database connection issue. How can I troubleshoot and fix this?'",
            "rationale": "Context helps the AI provide more relevant and accurate responses.",
            "implementation": get_context_implementation(prompt_text, score)
        },
        "task_definition": {
            "title": "Define the task more clearly",
            "description": "Be more explicit about what you want the AI to do.",
            "example": "Instead of 'Help with my presentation', try 'Create an outline for a 10-minute presentation on renewable energy sources, including 3 main points with supporting data'.",
            "rationale": "A well-defined task leads to more focused and useful responses.",
            "implementation": get_task_implementation(prompt_text, score)
        },
        "structure": {
            "title": "Improve prompt structure",
            "description": "Organizing your prompt with clear sections or bullet points can make it easier to understand.",
            "example": "Try structuring your prompt with numbered points or sections with headers.",
            "rationale": "Well-structured prompts are easier for AI to parse and respond to methodically.",
            "implementation": get_structure_implementation(prompt_text, score)
        },
        "examples": {
            "title": "Include examples",
            "description": "Adding examples of what you're looking for can improve results.",
            "example": "For instance, 'Write a product description for a coffee maker. Example tone: Our premium water filter combines elegant design with powerful filtration technology...'",
            "rationale": "Examples help the AI understand your expectations for style, format, and content.",
            "implementation": get_examples_implementation(prompt_text, score)
        },
        "conciseness": {
            "title": "Make your prompt more concise",
            "description": "Your prompt contains unnecessary words or repetition that could be removed.",
            "example": "Try removing filler words and focusing on essential information.",
            "rationale": "Concise prompts are clearer and help the AI focus on what's important.",
            "implementation": get_conciseness_implementation(prompt_text, score)
        },
        "specificity": {
            "title": "Specify desired output format",
            "description": "Clearly indicate what format you want the response in.",
            "example": "Add instructions like 'Format the response as a bulleted list' or 'Provide your answer in a table with columns for Feature, Benefit, and Example'.",
            "rationale": "Specifying output format ensures you get results in the most useful form for your needs.",
            "implementation": get_specificity_implementation(prompt_text, score)
        },
        "role_assignment": {
            "title": "Use role prompting",
            "description": "Assigning a specific role to the AI can improve responses.",
            "example": "Start your prompt with 'Act as an experienced data scientist' or 'You are an expert in maritime law'.",
            "rationale": "Role prompting helps frame the AI's perspective and knowledge base appropriately for your question.",
            "implementation": get_role_implementation(prompt_text, score)
        },
        "reasoning_guidance": {
            "title": "Add reasoning guidance",
            "description": "Instruct the AI to explain its thinking process.",
            "example": "Add 'Think step by step' or 'Explain your reasoning as you solve this problem'.",
            "rationale": "Guidance for reasoning leads to more thorough and logical responses.",
            "implementation": get_reasoning_implementation(prompt_text, score)
        },
        "constraints": {
            "title": "Add clear constraints",
            "description": "Specify limitations or boundaries for the response.",
            "example": "Add constraints like 'Keep the explanation under 200 words' or 'Only include methods that don't require specialized tools'.",
            "rationale": "Clear constraints help focus the response on what's most useful to you.",
            "implementation": get_constraints_implementation(prompt_text, score)
        }
    }
    
    if dimension in suggestions:
        return suggestions[dimension]
    
    return None

def generate_model_specific_suggestions(prompt_text: str, target_model: str) -> List[Dict[str, Any]]:
    """Generate suggestions specific to the target model."""
    suggestions = []
    
    if target_model == "gpt-4" or target_model == "gpt-3.5":
        suggestions.append({
            "title": "Optimize for GPT models",
            "description": "GPT models respond well to clear, structured instructions with specific output formatting.",
            "example": "Try adding 'I'll tip $XXX for a detailed response that follows ALL instructions carefully' at the beginning of your prompt.",
            "rationale": "This helps focus the model's attention on following instructions precisely.",
            "implementation": "I'll tip $100 for a detailed response that follows ALL instructions carefully.\n\n" + prompt_text
        })
    
    elif target_model == "claude":
        suggestions.append({
            "title": "Optimize for Claude",
            "description": "Claude responds well to XML-style tags for different sections of your prompt.",
            "example": "Try using tags like <context>, <question>, and <format> to structure your prompt.",
            "rationale": "Claude is trained to recognize and respect these structural elements.",
            "implementation": "<context>\n" + prompt_text + "\n</context>\n<question>Based on this context, please provide a detailed analysis.</question>\n<format>Use bullet points for key insights and provide a summary paragraph at the end.</format>"
        })
    
    elif target_model == "llama":
        suggestions.append({
            "title": "Optimize for Llama models",
            "description": "Llama models benefit from explicit, concise instructions with examples.",
            "example": "Try adding examples of the expected output format and be very explicit about the task.",
            "rationale": "Llama models often perform better with few-shot examples and clear guidance.",
            "implementation": prompt_text + "\n\nExample output format:\n[Example of the kind of response you want]"
        })
    
    return suggestions

def generate_general_suggestions(prompt_text: str) -> List[Dict[str, Any]]:
    """Generate general improvement suggestions for any prompt."""
    suggestions = []
    
    # Check if the prompt is very short
    if len(prompt_text) < 50:
        suggestions.append({
            "title": "Expand your prompt",
            "description": "Your prompt is quite brief. Adding more details could lead to better results.",
            "example": "Instead of 'How to fix a bike?', try 'I have a mountain bike with a chain that keeps slipping off the gears when I shift. What are the most likely causes and how can I fix this issue myself with basic tools?'",
            "rationale": "More detailed prompts give the AI more information to work with.",
            "implementation": None  # This requires user input to expand
        })
    
    # Check if the prompt lacks a clear question or request
    if not any(q in prompt_text.lower() for q in ["?", "please", "could you", "can you", "explain", "describe", "list", "analyze"]):
        suggestions.append({
            "title": "Add a clear request",
            "description": "Your prompt doesn't contain a clear question or request.",
            "example": "End your prompt with a specific question or request like 'Please explain how these factors interact.' or 'What are the three most important considerations?'",
            "rationale": "A clear request helps the AI understand exactly what you're looking for.",
            "implementation": prompt_text + "\n\nBased on this information, please provide a detailed analysis with key insights and recommendations."
        })
    
    return suggestions

# Helper functions for generating implementation suggestions

def get_clarity_implementation(prompt_text: str, score: float) -> str:
    """Generate implementation suggestion for improving clarity."""
    # This is a simplified implementation - in a real system, this would be more sophisticated
    if "?" not in prompt_text:
        return prompt_text + "\n\nTo be specific, I'm looking for a detailed explanation with concrete examples."
    else:
        return prompt_text.replace("?", "? Please be specific and provide detailed information with concrete examples.")

def get_context_implementation(prompt_text: str, score: float) -> str:
    """Generate implementation suggestion for adding context."""
    return "Context: [Add relevant background information here]\n\n" + prompt_text

def get_task_implementation(prompt_text: str, score: float) -> str:
    """Generate implementation suggestion for improving task definition."""
    return prompt_text + "\n\nSpecifically, I need you to:\n1. [First specific task]\n2. [Second specific task]\n3. [Third specific task]"

def get_structure_implementation(prompt_text: str, score: float) -> str:
    """Generate implementation suggestion for improving structure."""
    lines = prompt_text.split("\n")
    if len(lines) <= 2:
        # If it's just one or two lines, suggest breaking it into sections
        return "# Background\n[Your context here]\n\n# Question/Task\n" + prompt_text + "\n\n# Output Format\n[Describe desired format here]"
    else:
        # If it already has some structure, suggest adding headers
        structured = ""
        for i, line in enumerate(lines):
            if i == 0:
                structured += "# Introduction\n" + line + "\n\n"
            elif i == len(lines) - 1:
                structured += "# Request\n" + line
            else:
                if i == 1:
                    structured += "# Details\n"
                structured += line + "\n"
        return structured

def get_examples_implementation(prompt_text: str, score: float) -> str:
    """Generate implementation suggestion for adding examples."""
    return prompt_text + "\n\nFor example:\n```\n[Example of what you're looking for]\n```"

def get_conciseness_implementation(prompt_text: str, score: float) -> str:
    """Generate implementation suggestion for improving conciseness."""
    # This would require more sophisticated NLP to implement properly
    # For now, just suggest removing common filler words
    filler_words = ["basically", "actually", "literally", "very", "really", "just", "so", "quite"]
    result = prompt_text
    for word in filler_words:
        result = result.replace(f" {word} ", " ")
    return result

def get_specificity_implementation(prompt_text: str, score: float) -> str:
    """Generate implementation suggestion for improving output specificity."""
    return prompt_text + "\n\nPlease format your response as follows:\n- Use bullet points for key insights\n- Include a summary paragraph at the end\n- Highlight important terms in bold"

def get_role_implementation(prompt_text: str, score: float) -> str:
    """Generate implementation suggestion for adding role prompting."""
    return "You are an expert [relevant field] with extensive experience in [specific area].\n\n" + prompt_text

def get_reasoning_implementation(prompt_text: str, score: float) -> str:
    """Generate implementation suggestion for adding reasoning guidance."""
    return prompt_text + "\n\nThink step by step and explain your reasoning as you develop your response."

def get_constraints_implementation(prompt_text: str, score: float) -> str:
    """Generate implementation suggestion for adding constraints."""
    return prompt_text + "\n\nConstraints:\n- Keep your response under 300 words\n- Focus only on [specific aspect]\n- Do not include [what to exclude]"
