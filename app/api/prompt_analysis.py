from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.core.analyzer import analyze_prompt_rules
from app.core.optimizer import generate_optimization_suggestions
from app.core.llm_analyzer import analyze_prompt_with_llm
from app.core.rate_limiter import RateLimiter
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(tags=["prompt"])

# Initialize rate limiter
rate_limiter = RateLimiter(max_requests=10, time_window=60)  # 10 requests per minute

class PromptRequest(BaseModel):
    prompt_text: str
    target_model: Optional[str] = "general"
    detailed_analysis: bool = False
    api_key: Optional[str] = None  # Field for API key

class AnalysisResponse(BaseModel):
    scores: Dict[str, float]
    overall_score: float
    suggestions: List[Dict[str, Any]]
    strengths: List[str]
    weaknesses: List[str]
    optimized_prompt: str

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_prompt(
    prompt_request: PromptRequest, 
    background_tasks: BackgroundTasks,
    _: None = Depends(rate_limiter.limit)
):
    """
    Analyze a prompt and provide optimization suggestions.
    
    This endpoint performs both rule-based and LLM-based analysis
    to evaluate prompt quality and suggest improvements.
    """
    try:
        logger.info(f"Analyzing prompt for target model: {prompt_request.target_model}")
        logger.info(f"Detailed analysis requested: {prompt_request.detailed_analysis}")
        
        # Perform rule-based analysis first (synchronous)
        rule_analysis = analyze_prompt_rules(prompt_request.prompt_text, prompt_request.target_model)
        logger.info("Rule-based analysis completed")
        
        # Initialize variables for LLM analysis results
        llm_analysis = None
        
        # If detailed analysis is requested and API key is provided, perform LLM analysis
        if prompt_request.detailed_analysis and prompt_request.api_key:
            logger.info("Starting LLM analysis with provided API key")
            try:
                # For immediate response, we'll use the rule-based analysis
                # but also perform the LLM analysis synchronously for this prototype
                # In a production app, you would use background tasks or WebSockets
                llm_analysis = await analyze_prompt_with_llm(
                    prompt_request.prompt_text,
                    prompt_request.target_model,
                    prompt_request.api_key  # Pass the API key from the request
                )
                logger.info("LLM analysis completed successfully")
            except Exception as e:
                # If LLM analysis fails, log the error but continue with rule-based analysis
                logger.error(f"LLM analysis failed: {str(e)}", exc_info=True)
                llm_analysis = None
        
        # Generate optimization suggestions
        suggestions = generate_optimization_suggestions(
            prompt_request.prompt_text,
            rule_analysis,
            prompt_request.target_model
        )
        logger.info(f"Generated {len(suggestions)} optimization suggestions")
        
        # Calculate overall score (0-1 scale)
        raw_overall_score = sum(rule_analysis["dimension_scores"].values()) / len(rule_analysis["dimension_scores"])
        # Scale to 0-5 range for display
        overall_score = raw_overall_score * 5
        logger.info(f"Overall score: {overall_score:.2f}/5 (raw: {raw_overall_score:.2f})")
        
        # Create optimized prompt (placeholder - will be implemented in optimizer)
        optimized_prompt = prompt_request.prompt_text
        
        # If we have LLM analysis results, use them to enhance our response
        if llm_analysis and "error" not in llm_analysis:
            logger.info("Merging LLM analysis results with rule-based analysis")
            # Merge LLM analysis with rule-based analysis
            # This is a simplified example - in a real app, you would do more sophisticated merging
            if "dimension_scores" in llm_analysis:
                rule_analysis["dimension_scores"].update(llm_analysis["dimension_scores"])
                logger.info("Updated dimension scores with LLM analysis")
            
            if "strengths" in llm_analysis and llm_analysis["strengths"]:
                rule_analysis["strengths"].extend(llm_analysis["strengths"])
                logger.info(f"Added {len(llm_analysis['strengths'])} strengths from LLM analysis")
            
            if "weaknesses" in llm_analysis and llm_analysis["weaknesses"]:
                rule_analysis["weaknesses"].extend(llm_analysis["weaknesses"])
                logger.info(f"Added {len(llm_analysis['weaknesses'])} weaknesses from LLM analysis")
            
            if "suggestions" in llm_analysis and llm_analysis["suggestions"]:
                suggestions.extend(llm_analysis["suggestions"])
                logger.info(f"Added {len(llm_analysis['suggestions'])} suggestions from LLM analysis")
            
            if "improved_prompt" in llm_analysis and llm_analysis["improved_prompt"]:
                optimized_prompt = llm_analysis["improved_prompt"]
                logger.info("Using improved prompt from LLM analysis")
        
        logger.info("Preparing final response")
        return {
            "scores": rule_analysis["dimension_scores"],
            "overall_score": overall_score,
            "suggestions": suggestions,
            "strengths": rule_analysis["strengths"],
            "weaknesses": rule_analysis["weaknesses"],
            "optimized_prompt": optimized_prompt
        }
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/dimensions")
async def get_dimensions():
    """Get the list of dimensions used for prompt evaluation."""
    # This will be implemented to return the evaluation dimensions
    dimensions = [
        {"id": "clarity", "name": "Clarity & Specificity", "description": "How clear and unambiguous the instructions are"},
        {"id": "context", "name": "Context Provided", "description": "Adequacy of background information"},
        {"id": "task_definition", "name": "Task Definition", "description": "How well the expected task is defined"},
        {"id": "structure", "name": "Structure", "description": "Organization and formatting of the prompt"},
        {"id": "examples", "name": "Examples", "description": "Quality and relevance of examples provided"},
        # More dimensions will be added
    ]
    return {"dimensions": dimensions}
