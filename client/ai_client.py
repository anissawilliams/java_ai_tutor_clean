"""
Simple OpenAI Client Wrapper
No CrewAI, no complex agent frameworks - just clean OpenAI API calls
"""

import os
import streamlit as st
from typing import Optional, List, Dict
from openai import OpenAI


class SimpleAIClient:
    """Handles all AI interactions with OpenAI"""
    
    def __init__(self):
        # Try Streamlit secrets first, then environment variable
        try:
            api_key = st.secrets["openai"]["api_key"]
        except:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            st.error("""
            OpenAI API key not found!
            
            **Add to `.streamlit/secrets.toml`:**
            ```
            [openai]
            api_key = "sk-..."
            ```
            
            **Or set environment variable:**
            ```
            export OPENAI_API_KEY="sk-..."
            ```
            """)
            raise ValueError("OPENAI_API_KEY not configured")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Fast and cost-effective for research
        
    def generate_response(self, system_prompt: str, user_message: str, 
                         conversation_history: Optional[List[Dict]] = None,
                         temperature: float = 0.9) -> str:
        """
        Generate a response from OpenAI.
        
        Args:
            system_prompt: Instructions for the AI
            user_message: The user's current message
            conversation_history: Previous messages for context
            temperature: Creativity level (0.0-2.0)
            
        Returns:
            The AI's response as a string
        """
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Basic validation
            if not result or len(result) < 10:
                raise ValueError("Response too short or empty")
                
            return result
            
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    def generate_initial_metaphor(self, character_prompt: str, 
                                  topic_prompt: str) -> str:
        """
        Generate the initial metaphor introduction.
        
        This is a specialized call for the first message.
        """
        full_prompt = f"""{character_prompt}

{topic_prompt}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": "Create the welcome message."}
                ],
                temperature=1.0,
                max_tokens=250
            )
            
            result = response.choices[0].message.content.strip()
            
            # Validate it's not too generic
            if len(result) < 30:
                raise ValueError("Response too short")
            
            # Check for overly generic starts
            generic_starts = ["greetings. i am", "hello. i am", "welcome. i am"]
            if any(result.lower().startswith(start) for start in generic_starts):
                raise ValueError("Response too generic")
                
            return result
            
        except Exception as e:
            # Return None to trigger fallback
            return None
