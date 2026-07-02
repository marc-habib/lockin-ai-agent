"""
Agent handler for LockIn AI.

Main entry point for agent execution - the run_agent_handler() function.
"""

import time
import uuid
from typing import Dict, Any
from app.agent.intent_router import intent_router
from app.agent.agent_service import agent_service
from app.guardrails import input_guardrails, profile_guardrails, output_guardrails
from app.services.profile_service import profile_service
from app.models.enums import RequestStatus
from app.schemas.chat import ChatResponse


def run_agent_handler(user_id: str, message: str) -> ChatResponse:
    """
    Main handler function for agent execution.
    
    This is the required handler function that orchestrates the entire
    agent pipeline from input validation to response generation.
    
    Args:
        user_id: User identifier
        message: User message
    
    Returns:
        ChatResponse with result or error
    """
    start_time = time.time()
    request_id = f"req_{uuid.uuid4().hex[:12]}"
    
    # Step 1: Input Guardrails
    is_valid, error_msg = input_guardrails.validate(message)
    if not is_valid:
        latency_ms = int((time.time() - start_time) * 1000)
        return ChatResponse(
            request_id=request_id,
            status=RequestStatus.BLOCKED,
            guardrail_triggered=error_msg,
            latency_ms=latency_ms
        )
    
    # Step 2: Profile Guardrails
    profile, missing_fields = profile_guardrails.get_profile_or_error(user_id)
    if not profile:
        latency_ms = int((time.time() - start_time) * 1000)
        return ChatResponse(
            request_id=request_id,
            status=RequestStatus.PROFILE_REQUIRED,
            missing_fields=missing_fields,
            latency_ms=latency_ms
        )
    
    # Step 3: Intent Classification
    intent = intent_router.classify(message)
    
    # Step 4: Agent Execution
    try:
        agent_result = agent_service.run(
            message=message,
            profile=profile,
            intent=intent,
            user_id=user_id
        )
        
        # Check if agent returned an error
        if agent_result.get('error'):
            latency_ms = int((time.time() - start_time) * 1000)
            return ChatResponse(
                request_id=request_id,
                status=RequestStatus.ERROR,
                response=agent_result.get('response', 'An error occurred'),
                latency_ms=latency_ms
            )
        
        response_text = agent_result.get('response', '')
        tool_calls = agent_result.get('tool_calls', [])
        tool_results = agent_result.get('tool_results', [])
        
        # Step 5: Output Guardrails
        is_valid_output, output_error = output_guardrails.validate(
            response=response_text,
            tool_results=tool_results
        )
        
        if not is_valid_output:
            latency_ms = int((time.time() - start_time) * 1000)
            return ChatResponse(
                request_id=request_id,
                status=RequestStatus.BLOCKED,
                guardrail_triggered=f"Output validation failed: {output_error}",
                latency_ms=latency_ms
            )
        
        # Clean response to remove internal reflection text
        cleaned_response = output_guardrails.clean_response(response_text)
        
        # Extract structured data from tool results for meal plans
        structured_data = None
        if intent == Intent.MEAL_PLAN and tool_results:
            for result in tool_results:
                if result.get('tool_name') == 'daily_planner' and result.get('success'):
                    structured_data = result.get('result')
                    break
        
        # Step 6: Build Response
        latency_ms = int((time.time() - start_time) * 1000)
        
        return ChatResponse(
            request_id=request_id,
            status=RequestStatus.SUCCESS,
            intent=intent,
            response=cleaned_response,
            data=structured_data,
            latency_ms=latency_ms,
            tool_calls=tool_calls if tool_calls else None
        )
    
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return ChatResponse(
            request_id=request_id,
            status=RequestStatus.ERROR,
            response=f"An error occurred: {str(e)}",
            latency_ms=latency_ms
        )


def get_handler_metadata() -> Dict[str, Any]:
    """
    Get metadata about the handler.
    
    Returns:
        Dict with handler information
    """
    return {
        'handler_name': 'run_agent_handler',
        'version': '1.0.0',
        'description': 'Main agent execution handler with full pipeline',
        'pipeline_steps': [
            'Input Guardrails',
            'Profile Guardrails',
            'Intent Classification',
            'Agent Execution',
            'Output Guardrails',
            'Response Building'
        ]
    }
