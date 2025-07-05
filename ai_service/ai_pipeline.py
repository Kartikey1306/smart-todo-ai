import openai
from django.conf import settings
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

class AIPipeline:
    """
    A comprehensive AI pipeline for intelligent task management.

    This class encapsulates all interactions with the OpenAI API. It follows
    Object-Oriented principles by grouping related AI functionalities into a
    single, cohesive unit. Each method has a distinct responsibility, such as
    processing a new task, analyzing context, or generating recommendations.

    Attributes:
        user_id (int): The ID of the user for whom the pipeline is running.
        client (openai.OpenAI): The OpenAI API client instance.
        model (str): The specific GPT model to be used for requests.
    """

    def __init__(self, user_id: int):
        """
        Initializes the AIPipeline for a specific user.

        Args:
            user_id: The ID of the user.
        """
        self.user_id = user_id
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"

    def _make_request(self, system_prompt: str, user_prompt: str, temperature: float = 0.3, max_tokens: int = 1024) -> Optional[Dict[str, Any]]:
        """
        A private helper method to make requests to the OpenAI API.

        This centralizes API call logic, including error handling and JSON parsing,
        to keep other methods clean and focused on their specific tasks.

        Args:
            system_prompt: The system-level instruction for the AI model.
            user_prompt: The user-specific prompt containing the data to be processed.
            temperature: The creativity of the AI's response (0.0 to 2.0).
            max_tokens: The maximum number of tokens in the response.

        Returns:
            A dictionary containing the parsed JSON response from the AI,
            or None if an error occurs.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=max_tokens
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI API request failed for user {self.user_id}: {e}")
            return None

    def process_new_task(
        self,
        task_details: Dict[str, Any],
        daily_context: List[Dict],
        current_task_load: Dict,
        user_preferences: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Processes a new task using AI, providing a full suite of enhancements.

        This is the core function for task creation. It synthesizes multiple
        data points (task details, user context, workload) to produce a
        richly detailed and intelligent task object.

        Args:
            task_details: The initial details of the task provided by the user.
            daily_context: A list of recent context entries (emails, notes).
            current_task_load: A summary of the user's current tasks.
            user_preferences: Optional user settings (e.g., work hours).

        Returns:
            A dictionary with AI-enhanced task fields. Returns a fallback
            dictionary if the AI processing fails.
        """
        system_prompt = (
            "You are an expert productivity assistant. Your goal is to take a user's task input "
            "and enrich it with intelligent suggestions based on their context, workload, and preferences. "
            "Analyze all provided information to generate a comprehensive, structured JSON response."
        )

        user_prompt = f"""
        Please analyze the provided information and generate a fully enhanced task object in JSON format.

        **Input Task Details:**
        - Title: "{task_details.get('title', '')}"
        - Description: "{task_details.get('description', '')}"

        **User's Daily Context (Recent Messages, Emails, Notes):**
        {json.dumps(daily_context, indent=2)}

        **User's Current Task Load:**
        {json.dumps(current_task_load, indent=2)}

        **User Preferences (Optional):**
        {json.dumps(user_preferences or {}, indent=2)}

        **Your Task:**
        Generate a JSON object with the following fields:
        1.  `title`: A clear, actionable, and concise version of the user's title.
        2.  `enhanced_description`: An improved task description, incorporating relevant details from the context.
        3.  `priority`: An integer score (1=High, 2=Medium, 3=Low) based on urgency, importance, and context.
        4.  `deadline`: A suggested realistic deadline in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
        5.  `suggested_categories`: An array of relevant category names (e.g., "Work", "Personal", "Finance").
        6.  `context_tags`: An array of specific, granular tags derived from the task and context.
        7.  `reasoning`: A brief explanation for your priority and deadline suggestions.
        """

        result = self._make_request(system_prompt, user_prompt)

        if result:
            # Validate and format the deadline to prevent errors
            if 'deadline' in result and result['deadline']:
                try:
                    datetime.fromisoformat(result['deadline'].replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    result['deadline'] = None  # Invalidate incorrect format
            return result

        # Fallback in case of API error to ensure graceful failure
        return {
            "title": task_details.get('title'),
            "enhanced_description": task_details.get('description'),
            "priority": task_details.get('priority', 3),
            "deadline": None,
            "suggested_categories": [],
            "context_tags": [],
            "reasoning": "AI processing failed. Using user-provided details."
        }

    def analyze_context_entry(self, content: str, entry_type: str) -> Dict[str, Any]:
        """
        Analyzes a single piece of daily context to extract actionable intelligence.

        This method performs advanced analysis, including sentiment and keyword
        extraction, to turn unstructured text into structured, useful data.

        Args:
            content: The text content of the context entry (e.g., email body).
            entry_type: The type of the context entry (e.g., 'email', 'note').

        Returns:
            A dictionary with structured data extracted from the content.
        """
        system_prompt = (
            "You are an AI information extraction engine. Your job is to analyze text from a user's "
            "daily life and extract structured, actionable data. Always respond with a valid JSON object."
        )

        user_prompt = f"""
        Please analyze the following context entry and extract key information.

        **Entry Type:** {entry_type}
        **Content:**
        ---
        {content}
        ---

        **Your Task:**
        Generate a JSON object with the following fields:
        1.  `summary`: A one-sentence summary of the content.
        2.  `importance_score`: A float between 0.0 and 1.0 indicating how important or actionable this is.
        3.  `sentiment`: A string, either "positive", "negative", or "neutral".
        4.  `keywords`: An array of the 3-5 most important keywords or phrases.
        5.  `potential_tasks`: An array of strings, where each string is a potential task for a to-do list.
        6.  `mentioned_deadlines`: An array of strings for any dates or deadlines mentioned.
        7.  `mentioned_people`: An array of names of people mentioned.
        """

        result = self._make_request(system_prompt, user_prompt, temperature=0.2, max_tokens=600)

        return result or {
            "summary": "Could not analyze content.",
            "importance_score": 0.5,
            "sentiment": "neutral",
            "keywords": [],
            "potential_tasks": [],
            "mentioned_deadlines": [],
            "mentioned_people": [],
        }

    def generate_task_recommendations(self, daily_context: List[Dict], existing_tasks: List[Dict]) -> List[Dict]:
        """
        Generates personalized task recommendations based on recent context.

        This method acts proactively by anticipating user needs and suggesting
        tasks, preventing things from falling through the cracks.

        Args:
            daily_context: A list of recent context entries.
            existing_tasks: A list of current tasks to avoid duplication.

        Returns:
            A list of dictionaries, where each dictionary is a new task recommendation.
        """
        system_prompt = (
            "You are a proactive AI assistant. Your job is to anticipate the user's needs by "
            "analyzing their recent communications and current to-do list, then recommending new tasks. "
            "Do not suggest tasks that are already on the user's list. Respond with a valid JSON object."
        )

        user_prompt = f"""
        Based on the user's recent context and existing tasks, please generate a list of new task recommendations.

        **Recent Context:**
        {json.dumps(daily_context, indent=2)}

        **Existing Task Titles (to avoid duplication):**
        {[task.get('title') for task in existing_tasks]}

        **Your Task:**
        Generate a JSON object containing a single key, "recommendations", which is an array of task objects.
        Each task object should have:
        - `title`: The suggested task title.
        - `description`: A detailed description of why this task is needed.
        - `priority`: An integer score (1-3).
        - `reasoning`: A brief explanation for the recommendation.
        - `confidence_score`: A float (0.0-1.0) of your confidence in this suggestion.
        - `suggested_categories`: An array of relevant category names.
        """

        result = self._make_request(system_prompt, user_prompt, temperature=0.5, max_tokens=1200)
        return result.get("recommendations", []) if result else []
