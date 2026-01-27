"""AI provider abstraction layer."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import openai
from anthropic import Anthropic

from code_sage.core.config import AIConfig
from code_sage.core.exceptions import AIProviderError
from code_sage.core.logger import get_logger


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, config: AIConfig):
        """
        Initialize AI provider.

        Args:
            config: AI configuration
        """
        self.config = config
        self.logger = get_logger()

    @abstractmethod
    def analyze_code(self, code: str, context: str, language: str) -> str:
        """
        Analyze code and provide suggestions.

        Args:
            code: Code snippet to analyze
            context: Additional context
            language: Programming language

        Returns:
            AI analysis and suggestions
        """
        pass

    @abstractmethod
    def explain_issue(self, issue_description: str, code: str, language: str) -> str:
        """
        Explain an issue in detail.

        Args:
            issue_description: Issue description
            code: Code snippet
            language: Programming language

        Returns:
            Detailed explanation
        """
        pass

    @abstractmethod
    def suggest_fix(self, issue_description: str, code: str, language: str) -> Dict[str, str]:
        """
        Suggest a fix for an issue.

        Args:
            issue_description: Issue description
            code: Code snippet
            language: Programming language

        Returns:
            Dictionary with 'explanation' and 'fixed_code' keys
        """
        pass


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider."""

    def __init__(self, config: AIConfig):
        """Initialize OpenAI provider."""
        super().__init__(config)
        
        if not config.openai_api_key:
            raise AIProviderError("OpenAI API key not configured")
        
        openai.api_key = config.openai_api_key
        self.model = config.openai_model

    def analyze_code(self, code: str, context: str, language: str) -> str:
        """Analyze code using GPT."""
        try:
            prompt = f"""Analyze this {language} code and identify potential issues, bugs, or improvements:

Context: {context}

Code:
```{language}
{code}
```

Provide a concise analysis focusing on:
1. Potential bugs or errors
2. Security vulnerabilities
3. Performance issues
4. Best practice violations
5. Suggested improvements
"""

            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer and static analysis tool."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout,
            )

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise AIProviderError(f"Failed to analyze code: {e}")

    def explain_issue(self, issue_description: str, code: str, language: str) -> str:
        """Explain issue using GPT."""
        try:
            prompt = f"""Explain this code issue in detail:

Issue: {issue_description}

Code ({language}):
```{language}
{code}
```

Provide:
1. Why this is an issue
2. Potential impact
3. How to fix it
4. Best practices to avoid it

Keep the explanation clear and concise."""

            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software engineer explaining code issues."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout,
            )

            return response.choices[0].message.content

        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise AIProviderError(f"Failed to explain issue: {e}")

    def suggest_fix(self, issue_description: str, code: str, language: str) -> Dict[str, str]:
        """Suggest fix using GPT."""
        try:
            prompt = f"""Suggest a fix for this code issue:

Issue: {issue_description}

Original Code ({language}):
```{language}
{code}
```

Provide:
1. Brief explanation of the fix
2. Fixed code

Format your response as:
EXPLANATION:
[your explanation]

FIXED_CODE:
```{language}
[fixed code]
```
"""

            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert programmer fixing code issues."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout,
            )

            content = response.choices[0].message.content
            return self._parse_fix_response(content)

        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise AIProviderError(f"Failed to suggest fix: {e}")

    def _parse_fix_response(self, response: str) -> Dict[str, str]:
        """Parse fix response."""
        parts = response.split("FIXED_CODE:")
        explanation = parts[0].replace("EXPLANATION:", "").strip()
        
        fixed_code = ""
        if len(parts) > 1:
            fixed_code = parts[1].strip()
            # Remove code fence markers
            fixed_code = fixed_code.replace("```python", "").replace("```javascript", "")
            fixed_code = fixed_code.replace("```typescript", "").replace("```", "")
            fixed_code = fixed_code.strip()

        return {
            "explanation": explanation,
            "fixed_code": fixed_code
        }


class ClaudeProvider(AIProvider):
    """Anthropic Claude provider."""

    def __init__(self, config: AIConfig):
        """Initialize Claude provider."""
        super().__init__(config)
        
        if not config.anthropic_api_key:
            raise AIProviderError("Anthropic API key not configured")
        
        self.client = Anthropic(api_key=config.anthropic_api_key)
        self.model = config.anthropic_model

    def analyze_code(self, code: str, context: str, language: str) -> str:
        """Analyze code using Claude."""
        try:
            prompt = f"""Analyze this {language} code and identify potential issues, bugs, or improvements:

Context: {context}

Code:
```{language}
{code}
```

Provide a concise analysis focusing on:
1. Potential bugs or errors
2. Security vulnerabilities
3. Performance issues
4. Best practice violations
5. Suggested improvements
"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            self.logger.error(f"Claude API error: {e}")
            raise AIProviderError(f"Failed to analyze code: {e}")

    def explain_issue(self, issue_description: str, code: str, language: str) -> str:
        """Explain issue using Claude."""
        try:
            prompt = f"""Explain this code issue in detail:

Issue: {issue_description}

Code ({language}):
```{language}
{code}
```

Provide:
1. Why this is an issue
2. Potential impact
3. How to fix it
4. Best practices to avoid it

Keep the explanation clear and concise."""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            self.logger.error(f"Claude API error: {e}")
            raise AIProviderError(f"Failed to explain issue: {e}")

    def suggest_fix(self, issue_description: str, code: str, language: str) -> Dict[str, str]:
        """Suggest fix using Claude."""
        try:
            prompt = f"""Suggest a fix for this code issue:

Issue: {issue_description}

Original Code ({language}):
```{language}
{code}
```

Provide:
1. Brief explanation of the fix
2. Fixed code

Format your response as:
EXPLANATION:
[your explanation]

FIXED_CODE:
```{language}
[fixed code]
```
"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            return self._parse_fix_response(content)

        except Exception as e:
            self.logger.error(f"Claude API error: {e}")
            raise AIProviderError(f"Failed to suggest fix: {e}")

    def _parse_fix_response(self, response: str) -> Dict[str, str]:
        """Parse fix response."""
        parts = response.split("FIXED_CODE:")
        explanation = parts[0].replace("EXPLANATION:", "").strip()
        
        fixed_code = ""
        if len(parts) > 1:
            fixed_code = parts[1].strip()
            # Remove code fence markers
            for lang in ["python", "javascript", "typescript", "java", "go"]:
                fixed_code = fixed_code.replace(f"```{lang}", "")
            fixed_code = fixed_code.replace("```", "").strip()

        return {
            "explanation": explanation,
            "fixed_code": fixed_code
        }


def get_ai_provider(config: AIConfig) -> Optional[AIProvider]:
    """
    Get AI provider based on configuration.

    Args:
        config: AI configuration

    Returns:
        AIProvider instance or None if not enabled
    """
    if not config.enabled:
        return None

    if config.provider == "openai":
        return OpenAIProvider(config)
    elif config.provider == "anthropic":
        return ClaudeProvider(config)
    else:
        raise AIProviderError(f"Unknown AI provider: {config.provider}")
