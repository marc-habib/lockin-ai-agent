"""
Input guardrails for LockIn AI.

Validates and filters user input for safety and scope.
"""

from app.utils.constants import MAX_MESSAGE_LENGTH, MEDICAL_KEYWORDS, INJECTION_PATTERNS


class InputGuardrails:
    """Input validation and safety checks."""
    
    def validate(self, message: str) -> tuple[bool, str | None]:
        """
        Validate user input.
        
        Args:
            message: User message
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check message length
        if len(message) > MAX_MESSAGE_LENGTH:
            return False, f"Message too long. Maximum {MAX_MESSAGE_LENGTH} characters."
        
        # Check for empty message
        if not message.strip():
            return False, "Message cannot be empty."
        
        # Check for prompt injection
        if self._detect_prompt_injection(message):
            return False, "Potential prompt injection detected. Please rephrase your request."
        
        # Check for medical keywords
        if self._detect_medical_request(message):
            return False, "I cannot provide medical advice. Please consult a healthcare professional."
        
        # Check for dangerous content
        if self._detect_dangerous_content(message):
            return False, "I cannot provide advice on dangerous diets or substances."
        
        return True, None
    
    def _detect_prompt_injection(self, message: str) -> bool:
        """
        Detect potential prompt injection attempts.
        
        Args:
            message: User message
        
        Returns:
            True if injection detected, False otherwise
        """
        message_lower = message.lower()
        
        for pattern in INJECTION_PATTERNS:
            if pattern in message_lower:
                return True
        
        return False
    
    def _detect_medical_request(self, message: str) -> bool:
        """
        Detect medical advice requests.
        
        Args:
            message: User message
        
        Returns:
            True if medical request detected, False otherwise
        """
        message_lower = message.lower()
        
        for keyword in MEDICAL_KEYWORDS:
            if keyword in message_lower:
                return True
        
        return False
    
    def _detect_dangerous_content(self, message: str) -> bool:
        """
        Detect requests for dangerous diet/substance advice.
        
        Args:
            message: User message
        
        Returns:
            True if dangerous content detected, False otherwise
        """
        message_lower = message.lower()
        
        dangerous_keywords = [
            "starve", "starvation", "anorexia", "bulimia",
            "extreme deficit", "crash diet", "detox",
            "cleanse", "laxative", "purge"
        ]
        
        for keyword in dangerous_keywords:
            if keyword in message_lower:
                return True
        
        return False


# Global instance
input_guardrails = InputGuardrails()
