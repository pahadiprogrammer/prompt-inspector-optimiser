"""
Rule-based prompt analyzer module.

This module contains functions for analyzing prompts using rule-based techniques
without requiring API calls to LLM providers.
"""

import re
from typing import Dict, List, Any

# Define evaluation dimensions
DIMENSIONS = {
    "clarity": {
        "name": "Clarity & Specificity",
        "description": "How clear and unambiguous the instructions are",
        "weight": 1.0
    },
    "context": {
        "name": "Context Provided",
        "description": "Adequacy of background information",
        "weight": 0.8
    },
    "task_definition": {
        "name": "Task Definition",
        "description": "How well the expected task is defined",
        "weight": 1.0
    },
    "structure": {
        "name": "Structure",
        "description": "Organization and formatting of the prompt",
        "weight": 0.7
    },
    "examples": {
        "name": "Examples",
        "description": "Quality and relevance of examples provided",
        "weight": 0.8
    },
    "conciseness": {
        "name": "Conciseness",
        "description": "Efficiency of language without unnecessary verbosity",
        "weight": 0.6
    },
    "specificity": {
        "name": "Output Specificity",
        "description": "Clarity about the desired output format or style",
        "weight": 0.9
    },
    "role_assignment": {
        "name": "Role Assignment",
        "description": "Effective use of role prompting",
        "weight": 0.7
    },
    "reasoning_guidance": {
        "name": "Reasoning Guidance",
        "description": "Instructions for step-by-step thinking",
        "weight": 0.8
    },
    "constraints": {
        "name": "Constraints & Limitations",
        "description": "Clear boundaries and constraints",
        "weight": 0.7
    }
}

def analyze_prompt_rules(prompt_text: str, target_model: str = "general") -> Dict[str, Any]:
    """
    Analyze a prompt using rule-based techniques.
    
    Args:
        prompt_text: The prompt text to analyze
        target_model: The target model for the prompt
        
    Returns:
        Dictionary containing analysis results
    """
    # Initialize results
    results = {
        "dimension_scores": {},
        "strengths": [],
        "weaknesses": []
    }
    
    # Analyze clarity and specificity
    clarity_score = analyze_clarity(prompt_text)
    results["dimension_scores"]["clarity"] = clarity_score
    
    if clarity_score >= 0.8:
        results["strengths"].append("Clear and specific instructions")
    elif clarity_score <= 0.4:
        results["weaknesses"].append("Instructions lack clarity and specificity")
    
    # Analyze context
    context_score = analyze_context(prompt_text)
    results["dimension_scores"]["context"] = context_score
    
    if context_score >= 0.8:
        results["strengths"].append("Good background context provided")
    elif context_score <= 0.4:
        results["weaknesses"].append("Insufficient context or background information")
    
    # Analyze task definition
    task_score = analyze_task_definition(prompt_text)
    results["dimension_scores"]["task_definition"] = task_score
    
    if task_score >= 0.8:
        results["strengths"].append("Well-defined task or request")
    elif task_score <= 0.4:
        results["weaknesses"].append("Task or request is poorly defined")
    
    # Analyze structure
    structure_score = analyze_structure(prompt_text)
    results["dimension_scores"]["structure"] = structure_score
    
    if structure_score >= 0.8:
        results["strengths"].append("Well-structured prompt with good organization")
    elif structure_score <= 0.4:
        results["weaknesses"].append("Poor structure or organization")
    
    # Analyze examples
    examples_score = analyze_examples(prompt_text)
    results["dimension_scores"]["examples"] = examples_score
    
    if examples_score >= 0.8:
        results["strengths"].append("Effective use of examples")
    elif examples_score <= 0.4 and len(prompt_text) > 200:  # Only flag for longer prompts
        results["weaknesses"].append("Missing or ineffective examples")
    
    # Analyze conciseness
    conciseness_score = analyze_conciseness(prompt_text)
    results["dimension_scores"]["conciseness"] = conciseness_score
    
    if conciseness_score >= 0.8:
        results["strengths"].append("Concise and efficient language")
    elif conciseness_score <= 0.4:
        results["weaknesses"].append("Unnecessarily verbose or repetitive")
    
    # Analyze output specificity
    specificity_score = analyze_output_specificity(prompt_text)
    results["dimension_scores"]["specificity"] = specificity_score
    
    if specificity_score >= 0.8:
        results["strengths"].append("Clear output format or style specifications")
    elif specificity_score <= 0.4:
        results["weaknesses"].append("Unclear expectations for output format or style")
    
    # Analyze role assignment
    role_score = analyze_role_assignment(prompt_text)
    results["dimension_scores"]["role_assignment"] = role_score
    
    if role_score >= 0.8:
        results["strengths"].append("Effective use of role prompting")
    
    # Analyze reasoning guidance
    reasoning_score = analyze_reasoning_guidance(prompt_text)
    results["dimension_scores"]["reasoning_guidance"] = reasoning_score
    
    if reasoning_score >= 0.8:
        results["strengths"].append("Good guidance for reasoning process")
    
    # Analyze constraints
    constraints_score = analyze_constraints(prompt_text)
    results["dimension_scores"]["constraints"] = constraints_score
    
    if constraints_score >= 0.8:
        results["strengths"].append("Clear constraints and limitations")
    
    return results

def analyze_clarity(prompt_text: str) -> float:
    """Analyze the clarity and specificity of a prompt."""
    score = 0.5  # Start with a neutral score
    
    # Check for specific action verbs
    action_verbs = ["explain", "describe", "analyze", "compare", "summarize", "list", "create", "generate"]
    if any(verb in prompt_text.lower() for verb in action_verbs):
        score += 0.1
    
    # Check for specific questions
    question_words = ["what", "how", "why", "when", "where", "who", "which"]
    if any(f" {word} " in f" {prompt_text.lower()} " for word in question_words):
        score += 0.1
    
    # Check for ambiguous language
    ambiguous_terms = ["maybe", "perhaps", "somewhat", "kind of", "sort of", "etc", "and so on"]
    if any(term in prompt_text.lower() for term in ambiguous_terms):
        score -= 0.1
    
    # Check for specific quantities or metrics
    if re.search(r'\b\d+\b', prompt_text) or re.search(r'\b(few|several|many|most)\b', prompt_text.lower()):
        score += 0.1
    
    # Check for specific timeframes
    timeframes = ["minutes", "hours", "days", "weeks", "months", "years"]
    if any(timeframe in prompt_text.lower() for timeframe in timeframes):
        score += 0.05
    
    # Ensure score is between 0 and 1
    return max(0.0, min(1.0, score))

def analyze_context(prompt_text: str) -> float:
    """Analyze the context provided in a prompt."""
    score = 0.5  # Start with a neutral score
    
    # Check for context indicators
    context_indicators = [
        "background", "context", "previously", "currently", "situation", 
        "scenario", "setting", "environment", "given that", "assuming"
    ]
    
    # Count how many context indicators are present
    indicator_count = sum(1 for indicator in context_indicators if indicator in prompt_text.lower())
    score += min(0.2, indicator_count * 0.05)  # Cap at 0.2 bonus
    
    # Check for detailed context (longer sentences with context)
    sentences = re.split(r'[.!?]', prompt_text)
    context_sentences = [s for s in sentences if any(indicator in s.lower() for indicator in context_indicators)]
    if context_sentences:
        avg_context_length = sum(len(s) for s in context_sentences) / len(context_sentences)
        if avg_context_length > 100:
            score += 0.1
        elif avg_context_length > 50:
            score += 0.05
    
    # Check for absence of context in short prompts
    if len(prompt_text) < 100 and not any(indicator in prompt_text.lower() for indicator in context_indicators):
        score -= 0.2
    
    # Ensure score is between 0 and 1
    return max(0.0, min(1.0, score))

def analyze_task_definition(prompt_text: str) -> float:
    """Analyze how well the task is defined in a prompt."""
    score = 0.5  # Start with a neutral score
    
    # Check for clear task definition
    task_indicators = ["task is", "goal is", "objective is", "please", "I need", "I want", "create", "generate"]
    if any(indicator in prompt_text.lower() for indicator in task_indicators):
        score += 0.1
    
    # Check for specific deliverables
    deliverable_indicators = ["output", "result", "produce", "create", "generate", "write", "design"]
    if any(indicator in prompt_text.lower() for indicator in deliverable_indicators):
        score += 0.1
    
    # Check for task complexity indicators
    if "step by step" in prompt_text.lower() or "steps:" in prompt_text.lower():
        score += 0.1
    
    # Check for purpose indicators
    purpose_indicators = ["in order to", "so that", "purpose", "goal", "aim"]
    if any(indicator in prompt_text.lower() for indicator in purpose_indicators):
        score += 0.1
    
    # Check for vague requests
    vague_requests = ["do something", "help me", "I'm not sure", "whatever you think"]
    if any(request in prompt_text.lower() for request in vague_requests):
        score -= 0.2
    
    # Ensure score is between 0 and 1
    return max(0.0, min(1.0, score))

def analyze_structure(prompt_text: str) -> float:
    """Analyze the structure and organization of a prompt."""
    score = 0.5  # Start with a neutral score
    
    # Check for numbered lists
    if re.search(r'\b\d+\.\s', prompt_text):
        score += 0.15
    
    # Check for bullet points
    if re.search(r'[\•\-\*]\s', prompt_text):
        score += 0.15
    
    # Check for sections with headers
    if re.search(r'[A-Z][a-z]+:', prompt_text) or re.search(r'[A-Z][A-Z\s]+:', prompt_text):
        score += 0.1
    
    # Check for paragraphs (multiple line breaks)
    paragraphs = prompt_text.split('\n\n')
    if len(paragraphs) > 1:
        score += 0.05
    
    # Check for formatting like bold, italics, etc.
    if re.search(r'[\*\_]{1,2}[^\*\_]+[\*\_]{1,2}', prompt_text):
        score += 0.05
    
    # Ensure score is between 0 and 1
    return max(0.0, min(1.0, score))

def analyze_examples(prompt_text: str) -> float:
    """Analyze the use of examples in a prompt."""
    score = 0.5  # Start with a neutral score
    
    # Check for example indicators
    example_indicators = ["example", "instance", "case", "illustration", "e.g.", "for instance", "such as"]
    
    # Count how many example indicators are present
    indicator_count = sum(1 for indicator in example_indicators if indicator in prompt_text.lower())
    
    if indicator_count > 0:
        score += min(0.3, indicator_count * 0.1)  # Cap at 0.3 bonus
    
    # Check for formatted examples (code blocks, quotes)
    if re.search(r'```[^`]+```', prompt_text) or re.search(r'`[^`]+`', prompt_text):
        score += 0.1
    
    if re.search(r'\"[^\"]+\"', prompt_text) or re.search(r'\'[^\']+\'', prompt_text):
        score += 0.05
    
    # Check for "before and after" examples
    if ("before" in prompt_text.lower() and "after" in prompt_text.lower()) or ("input" in prompt_text.lower() and "output" in prompt_text.lower()):
        score += 0.1
    
    # Ensure score is between 0 and 1
    return max(0.0, min(1.0, score))

def analyze_conciseness(prompt_text: str) -> float:
    """Analyze the conciseness of a prompt."""
    score = 0.7  # Start with a slightly positive score
    
    # Check for excessive length
    if len(prompt_text) > 1000:
        score -= 0.2
    elif len(prompt_text) > 500:
        score -= 0.1
    
    # Check for repetition
    words = prompt_text.lower().split()
    word_count = len(words)
    unique_words = len(set(words))
    
    if word_count > 0:
        repetition_ratio = unique_words / word_count
        if repetition_ratio < 0.4:
            score -= 0.2
        elif repetition_ratio < 0.5:
            score -= 0.1
    
    # Check for filler words
    filler_words = ["basically", "actually", "literally", "very", "really", "just", "so", "quite"]
    filler_count = sum(1 for word in words if word in filler_words)
    
    if word_count > 0:
        filler_ratio = filler_count / word_count
        if filler_ratio > 0.05:
            score -= 0.1
    
    # Ensure score is between 0 and 1
    return max(0.0, min(1.0, score))

def analyze_output_specificity(prompt_text: str) -> float:
    """Analyze the specificity of output requirements in a prompt."""
    score = 0.5  # Start with a neutral score
    
    # Check for output format specifications
    format_indicators = [
        "format", "style", "layout", "structure", "template", 
        "json", "markdown", "html", "csv", "table", "list"
    ]
    
    if any(indicator in prompt_text.lower() for indicator in format_indicators):
        score += 0.15
    
    # Check for length specifications
    length_indicators = ["words", "characters", "sentences", "paragraphs", "pages", "length"]
    length_pattern = r'\b\d+\s+(?:' + '|'.join(length_indicators) + r')\b'
    
    if re.search(length_pattern, prompt_text.lower()):
        score += 0.15
    
    # Check for tone/style specifications
    tone_indicators = ["tone", "style", "voice", "formal", "informal", "technical", "simple", "academic"]
    
    if any(indicator in prompt_text.lower() for indicator in tone_indicators):
        score += 0.1
    
    # Check for audience specifications
    audience_indicators = ["audience", "reader", "user", "customer", "client", "stakeholder"]
    
    if any(indicator in prompt_text.lower() for indicator in audience_indicators):
        score += 0.1
    
    # Ensure score is between 0 and 1
    return max(0.0, min(1.0, score))

def analyze_role_assignment(prompt_text: str) -> float:
    """Analyze the use of role prompting in a prompt."""
    score = 0.5  # Start with a neutral score
    
    # Check for role assignment patterns
    role_patterns = [
        r'(?:act|serve|behave|respond|think|write)\s+as\s+(?:an?|the)\s+([a-z\s]+)',
        r'you\s+are\s+(?:an?|the)\s+([a-z\s]+)',
        r'(?:assume|take|adopt)\s+the\s+role\s+of\s+(?:an?|the)\s+([a-z\s]+)',
        r'(?:pretend|imagine)\s+(?:you\s+are|yourself\s+as)\s+(?:an?|the)\s+([a-z\s]+)'
    ]
    
    for pattern in role_patterns:
        if re.search(pattern, prompt_text.lower()):
            score += 0.3
            break
    
    # Check for expertise level specification
    expertise_indicators = ["expert", "specialist", "professional", "experienced", "knowledgeable"]
    
    if any(indicator in prompt_text.lower() for indicator in expertise_indicators):
        score += 0.1
    
    # Check for role-specific knowledge references
    knowledge_patterns = [
        r'with\s+(?:expertise|specialization|knowledge|background|experience)\s+in',
        r'who\s+(?:specializes|focuses|works)\s+in',
        r'trained\s+in'
    ]
    
    for pattern in knowledge_patterns:
        if re.search(pattern, prompt_text.lower()):
            score += 0.1
            break
    
    # Ensure score is between 0 and 1
    return max(0.0, min(1.0, score))

def analyze_reasoning_guidance(prompt_text: str) -> float:
    """Analyze the guidance for reasoning process in a prompt."""
    score = 0.5  # Start with a neutral score
    
    # Check for step-by-step reasoning instructions
    reasoning_indicators = [
        "step by step", "think through", "reasoning", "explain your thinking",
        "show your work", "walk through", "break down", "analyze"
    ]
    
    if any(indicator in prompt_text.lower() for indicator in reasoning_indicators):
        score += 0.2
    
    # Check for explicit thinking process guidance
    thinking_patterns = [
        r'think\s+(?:carefully|critically|thoroughly|deeply|step\s+by\s+step)',
        r'(?:before|first)\s+(?:answering|responding)',
        r'consider\s+(?:all|different|various)\s+(?:aspects|factors|perspectives)'
    ]
    
    for pattern in thinking_patterns:
        if re.search(pattern, prompt_text.lower()):
            score += 0.1
            break
    
    # Check for structured reasoning frameworks
    frameworks = ["pros and cons", "advantages and disadvantages", "costs and benefits", "swot"]
    
    if any(framework in prompt_text.lower() for framework in frameworks):
        score += 0.2
    
    # Ensure score is between 0 and 1
    return max(0.0, min(1.0, score))

def analyze_constraints(prompt_text: str) -> float:
    """Analyze the clarity of constraints and limitations in a prompt."""
    score = 0.5  # Start with a neutral score
    
    # Check for constraint indicators
    constraint_indicators = [
        "constraint", "limitation", "restriction", "boundary", "limit",
        "must", "should", "need to", "have to", "required", "necessary",
        "don't", "do not", "avoid", "exclude"
    ]
    
    # Count how many constraint indicators are present
    indicator_count = sum(1 for indicator in constraint_indicators if indicator in prompt_text.lower())
    
    if indicator_count > 0:
        score += min(0.3, indicator_count * 0.05)  # Cap at 0.3 bonus
    
    # Check for specific constraints
    specific_constraints = [
        r'(?:no|without)\s+(?:more|less)\s+than\s+\d+',
        r'(?:minimum|maximum|at\s+least|at\s+most)\s+\d+',
        r'(?:only|exclusively)\s+use',
        r'(?:do\s+not|don\'t|avoid)\s+(?:use|include|mention)'
    ]
    
    for pattern in specific_constraints:
        if re.search(pattern, prompt_text.lower()):
            score += 0.1
            break
    
    # Check for time or resource constraints
    time_constraints = [
        r'(?:within|in|under)\s+\d+\s+(?:minute|hour|day|week)',
        r'(?:by|before|until)\s+(?:tomorrow|today|monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
        r'deadline',
        r'time\s+(?:limit|constraint|restriction)'
    ]
    
    for pattern in time_constraints:
        if re.search(pattern, prompt_text.lower()):
            score += 0.1
            break
    
    # Ensure score is between 0 and 1
    return max(0.0, min(1.0, score))
