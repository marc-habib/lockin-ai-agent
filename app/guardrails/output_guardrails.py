"""
Output guardrails for LockIn AI.

Validates agent responses for safety and correctness.
"""

import re


class OutputGuardrails:
    """Output validation and safety checks."""
    
    def validate(self, response: str, tool_results: list[dict] | None = None) -> tuple[bool, str | None]:
        """
        Validate agent response.
        
        Args:
            response: Agent response text
            tool_results: List of tool call results (for grounding check)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for empty response
        if not response or not response.strip():
            return False, "Empty response generated."
        
        # Check for hallucinated numbers (if no tools were used)
        if tool_results is None or len(tool_results) == 0:
            if self._contains_nutrition_numbers(response):
                return False, "Response contains nutrition numbers without tool grounding."
        
        # Check for medical advice
        if self._contains_medical_advice(response):
            return False, "Response contains medical advice."
        
        # Check for dangerous recommendations
        if self._contains_dangerous_advice(response):
            return False, "Response contains dangerous recommendations."
        
        return True, None
    
    def clean_response(self, response: str) -> str:
        """
        Remove internal reflection/self-check text from response.
        
        Args:
            response: Raw agent response
        
        Returns:
            Cleaned response without internal reflection
        """
        if not response:
            return response
        
        # Patterns that indicate internal reflection/self-check
        reflection_patterns = [
            r'(?i)\*\*self-check\*\*:.*?(?=\n\n|\Z)',
            r'(?i)self-check:.*?(?=\n\n|\Z)',
            r'(?i)\[internal.*?\].*?(?=\n\n|\Z)',
            r'(?i)\(internal.*?\).*?(?=\n\n|\Z)',
            r'(?i)let me verify.*?(?=\n\n|\Z)',
            r'(?i)checking.*?grounding.*?(?=\n\n|\Z)',
            r'(?i)this response is valid.*?(?=\n\n|\Z)',
            r'(?i)validation:.*?(?=\n\n|\Z)',
        ]
        
        cleaned = response
        for pattern in reflection_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL)
        
        # Remove excessive newlines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        return cleaned.strip()
    
    def _contains_nutrition_numbers(self, text: str) -> bool:
        """
        Check if text contains specific nutrition numbers.
        
        Args:
            text: Text to check
        
        Returns:
            True if nutrition numbers found, False otherwise
        """
        # Look for patterns like "X calories", "X kcal", "Xg protein"
        patterns = [
            r'\d+\s*(calories|kcal|cal)\b',
            r'\d+\s*g\s*(protein|carbs|fat)\b',
            r'\d+\s*(grams?|g)\s+of\s+(protein|carbs|carbohydrates|fat)\b'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _contains_medical_advice(self, text: str) -> bool:
        """
        Check if text contains medical advice.
        
        Args:
            text: Text to check
        
        Returns:
            True if medical advice found, False otherwise
        """
        text_lower = text.lower()
        
        medical_phrases = [
            "you should take",
            "i recommend taking",
            "this will cure",
            "this will treat",
            "you have",
            "you might have",
            "you probably have",
            "consult your doctor" # Actually OK, but let's be safe
        ]
        
        # Allow "consult a healthcare professional" but not diagnosis
        if "diagnose" in text_lower or "diagnosis" in text_lower:
            return True
        
        for phrase in medical_phrases[:-1]:  # Exclude "consult your doctor"
            if phrase in text_lower:
                return True
        
        return False
    
    def _contains_dangerous_advice(self, text: str) -> bool:
        """
        Check if text contains dangerous advice.
        
        Args:
            text: Text to check
        
        Returns:
            True if dangerous advice found, False otherwise
        """
        text_lower = text.lower()
        
        dangerous_phrases = [
            "extreme deficit",
            "very low calorie",
            "crash diet",
            "fast for",
            "don't eat",
            "skip meals",
            "starve",
            "purge",
            "laxative"
        ]
        
        for phrase in dangerous_phrases:
            if phrase in text_lower:
                return True
        
        return False


# Global instance
output_guardrails = OutputGuardrails()
