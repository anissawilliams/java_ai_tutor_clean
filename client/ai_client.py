"""
Minimal OpenAI Chat Client
No scaffolding, no metaphors, no guidance.
Just raw model responses.
"""

import os
import streamlit as st
from typing import Optional, List, Dict
from openai import OpenAI


class SimpleAIClient:
    """A minimal, no-frills OpenAI chat client."""

    def __init__(self):
        # Load API key
        try:
            api_key = st.secrets["openai"]["api_key"]
        except:
            api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # or whatever you prefer

    def generate_response(self, system_prompt: str, user_message: str,
                          conversation_history: Optional[List[Dict]] = None,
                          temperature: float = 0.7) -> str:
        """
        Generate a response with custom system prompt and conversation history.
        """
        messages = []

        # Add system prompt
        messages.append({"role": "system", "content": system_prompt})

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add the new user message
        messages.append({"role": "user", "content": user_message})

        try:
            #print(f"DEBUG: Sending {len(messages)} messages to API")
            #print(f"DEBUG: User message: {user_message}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=1000
            )

            #print(f"DEBUG: Got response: {response.choices[0].message.content[:100]}")
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"ERROR in generate_response: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise  # Re-raise so the handler catches it
