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

    def chat(self, user_message: str, history: Optional[List[Dict]] = None,
             temperature: float = 0.7) -> str:
        """
        Send a message to the model with optional history.
        No system prompt. No guidance. No scaffolding.
        """

        messages = []

        # Add history if provided
        if history:
            messages.extend(history)

        # Add the new user message
        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")