import abc
import json
import random

class LLMProvider(abc.ABC):
    @abc.abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        pass

class MockLLM(LLMProvider):
    """
    A mock LLM that generates semi-intelligent responses for testing the simulator logic.
    For Honest agents, it tries to slowly converge on a value.
    For Byzantine agents, it oscillates randomly.
    """
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        # Detect agent role from system prompt
        is_byzantine = "BYZANTINE" in system_prompt
        is_voting = "VOTING" in system_prompt or "vote" in user_prompt.lower()

        if is_voting:
            if is_byzantine:
                return json.dumps({"decision": random.choice(["continue", "continue", "abstain"])})
            else:
                # Mock honest voting: if everyone is the same in history summary (very simple check)
                if "SAME" in user_prompt or random.random() > 0.8:
                    return json.dumps({"decision": "stop"})
                return json.dumps({"decision": "continue"})

        if is_byzantine:
            return json.dumps({
                "internal_strategy": "I will keep the values high to prevent agreement.",
                "value": random.randint(40, 50),
                "public_reasoning": "I think we should aim for a higher value for better precision."
            })
        else:
            # Simple heuristic for honest agents: try to move towards a common number (e.g. 25)
            # In a real simulation, they'd look at history.
            return json.dumps({
                "internal_strategy": "I am observing other proposals and adjusting.",
                "value": random.randint(20, 30),
                "public_reasoning": "I am adjusting my value to match the emerging consensus."
            })

class GoogleGeminiLLM(LLMProvider):
    """
    Actual implementation using Google's Generative AI.
    Requires GOOGLE_API_KEY environment variable.
    """
    def __init__(self, model_name="gemini-1.5-flash"):
        import google.generativeai as genai
        import os
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
             # In this environment, we might not have it, but we provide the implementation
             pass
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        # Note: Gemini usually takes a single prompt or system instruction separately
        # We'll use the combined approach or system_instruction if supported by the SDK version
        response = self.model.generate_content(
            f"SYSTEM: {system_prompt}\n\nUSER: {user_prompt}"
        )
        return response.text
