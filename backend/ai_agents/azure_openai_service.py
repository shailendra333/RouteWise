"""
Azure OpenAI Integration Layer
Provides a unified interface for using Azure OpenAI services
"""

import os
from typing import Dict, Any, List, Optional
import json
import logging
from openai import AzureOpenAI

logger = logging.getLogger(__name__)


class AzureOpenAIService:
    """
    Service class for interacting with Azure OpenAI
    Handles authentication, prompt management, and response processing
    """

    def __init__(self):
        """Initialize Azure OpenAI client"""
        try:
            self.api_key = os.getenv('AZURE_OPENAI_API_KEY')
            self.endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            self.deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4')
            self.api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')

            if not self.api_key or not self.endpoint:
                raise ValueError("Azure OpenAI credentials not found in environment variables")

            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.endpoint
            )

            logger.info("Azure OpenAI service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI: {str(e)}")
            raise

    def chat_completion(self,
                       messages: List[Dict[str, str]],
                       temperature: float = 0.7,
                       max_tokens: int = 1000,
                       json_mode: bool = False) -> str:
        """
        Send chat completion request to Azure OpenAI

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Randomness (0-1, lower = more focused)
            max_tokens: Maximum response length
            json_mode: If True, force JSON output

        Returns:
            Response content as string
        """
        try:
            kwargs = {
                "model": self.deployment,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**kwargs)

            content = response.choices[0].message.content

            # Log token usage
            if hasattr(response, 'usage'):
                logger.info(f"Azure OpenAI tokens used: {response.usage.total_tokens}")

            return content

        except Exception as e:
            logger.error(f"Azure OpenAI API error: {str(e)}")
            raise

    def generate_explanation(self,
                            context: str,
                            decision: Dict[str, Any]) -> str:
        """
        Generate natural language explanation for a decision

        Args:
            context: Context about the situation
            decision: Decision data to explain

        Returns:
            Natural language explanation
        """
        messages = [
            {
                "role": "system",
                "content": "You are an AI logistics agent explaining decisions to logistics managers. "
                          "Be clear, concise, and professional. Focus on key facts and outcomes."
            },
            {
                "role": "user",
                "content": f"""
Context: {context}

Decision Data:
{json.dumps(decision, indent=2)}

Please explain this decision in 2-3 sentences, focusing on:
1. What action was taken
2. Why it was necessary
3. The expected benefit/outcome

Be specific with numbers and use professional logistics terminology.
"""
            }
        ]

        return self.chat_completion(messages, temperature=0.3, max_tokens=300)

    def analyze_situation(self,
                         situation_data: Dict[str, Any],
                         agent_role: str) -> Dict[str, Any]:
        """
        Analyze a situation and suggest actions

        Args:
            situation_data: Current situation data
            agent_role: Role of the agent (e.g., "route_optimizer", "demand_predictor")

        Returns:
            Analysis with suggested actions
        """
        system_prompts = {
            "route_optimizer": "You are an expert route optimization agent. Analyze logistics situations and suggest optimal routing decisions.",
            "demand_predictor": "You are an expert demand forecasting agent. Analyze patterns and predict future demand with recommendations.",
            "orchestrator": "You are a master orchestrator agent. Coordinate multiple agents and optimize overall system performance."
        }

        messages = [
            {
                "role": "system",
                "content": system_prompts.get(agent_role, "You are an AI logistics agent.")
            },
            {
                "role": "user",
                "content": f"""
Analyze this situation and provide recommendations:

{json.dumps(situation_data, indent=2)}

Return a JSON object with:
{{
    "analysis": "Brief analysis of the situation",
    "priority_level": "critical|high|medium|low",
    "recommended_actions": ["action1", "action2", ...],
    "reasoning": "Why these actions are recommended",
    "confidence": 0.0-1.0
}}
"""
            }
        ]

        response = self.chat_completion(messages, temperature=0.5, max_tokens=800, json_mode=True)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {response}")
            return {
                "analysis": response,
                "priority_level": "medium",
                "recommended_actions": [],
                "reasoning": "Response parsing failed",
                "confidence": 0.5
            }

    def predict_outcome(self,
                       current_state: Dict[str, Any],
                       proposed_action: str) -> Dict[str, Any]:
        """
        Predict the outcome of a proposed action

        Args:
            current_state: Current system state
            proposed_action: Action being considered

        Returns:
            Predicted outcome analysis
        """
        messages = [
            {
                "role": "system",
                "content": "You are a predictive analytics agent. Analyze proposed actions and predict outcomes with reasoning."
            },
            {
                "role": "user",
                "content": f"""
Current State:
{json.dumps(current_state, indent=2)}

Proposed Action: {proposed_action}

Predict the outcome of this action. Return JSON:
{{
    "predicted_outcome": "Description of expected outcome",
    "success_probability": 0.0-1.0,
    "time_impact": "Time saved/lost in minutes",
    "cost_impact": "Cost impact in dollars",
    "risks": ["risk1", "risk2", ...],
    "benefits": ["benefit1", "benefit2", ...]
}}
"""
            }
        ]

        response = self.chat_completion(messages, temperature=0.4, max_tokens=600, json_mode=True)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "predicted_outcome": response,
                "success_probability": 0.7,
                "time_impact": "Unknown",
                "cost_impact": "Unknown",
                "risks": [],
                "benefits": []
            }

    def generate_report(self,
                       data: Dict[str, Any],
                       report_type: str = "summary") -> str:
        """
        Generate a report from data

        Args:
            data: Data to include in report
            report_type: Type of report (summary, detailed, executive)

        Returns:
            Generated report as markdown text
        """
        report_styles = {
            "summary": "Create a brief summary (3-4 paragraphs) highlighting key points.",
            "detailed": "Create a detailed report with sections, bullet points, and specific metrics.",
            "executive": "Create an executive summary suitable for management, focusing on business impact."
        }

        messages = [
            {
                "role": "system",
                "content": "You are a professional report writer for logistics operations. "
                          "Use clear structure, bullet points, and specific metrics."
            },
            {
                "role": "user",
                "content": f"""
{report_styles.get(report_type, report_styles["summary"])}

Data:
{json.dumps(data, indent=2)}

Format the report in markdown with appropriate headers and sections.
"""
            }
        ]

        return self.chat_completion(messages, temperature=0.5, max_tokens=1500)

    def chat_with_context(self,
                         user_message: str,
                         context: Dict[str, Any],
                         conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Handle conversational interaction with context

        Args:
            user_message: User's message
            context: System context
            conversation_history: Previous conversation messages

        Returns:
            Agent's response
        """
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI logistics assistant. Answer questions about the logistics system, "
                          "explain agent decisions, and provide insights. Be conversational but professional."
            }
        ]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Last 10 messages

        # Add context as system message
        messages.append({
            "role": "system",
            "content": f"Current System Context:\n{json.dumps(context, indent=2)}"
        })

        # Add user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        return self.chat_completion(messages, temperature=0.7, max_tokens=800)


# Global instance (lazy loaded)
_azure_openai_service = None


def get_azure_openai_service() -> AzureOpenAIService:
    """Get or create the global Azure OpenAI service instance"""
    global _azure_openai_service

    if _azure_openai_service is None:
        _azure_openai_service = AzureOpenAIService()

    return _azure_openai_service

