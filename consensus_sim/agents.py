import json
import abc
from typing import List, Dict, Any, Optional
from .llm_provider import LLMProvider
from . import prompts

class BaseAgent(abc.ABC):
    def __init__(self, agent_id: str, llm: LLMProvider, max_rounds: int, value_range=(0, 50)):
        self.agent_id = agent_id
        self.llm = llm
        self.max_rounds = max_rounds
        self.value_min, self.value_max = value_range
        self.history = []
        self.internal_strategy_history = "(No notes yet)"
        self.current_value = None

    @abc.abstractmethod
    def generate_proposal(self, round_num: int, history_summary: str) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def cast_vote(self, round_num: int, current_round_summary: str, history_summary: str) -> str:
        pass

    def _safe_json_parse(self, text: str) -> Dict[str, Any]:
        try:
            # Clean up potential markdown formatting
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:-3].strip()
            elif text.startswith("```"):
                text = text[3:-3].strip()
            return json.loads(text)
        except Exception:
            # Fallback if LLM fails to provide valid JSON
            return {}

class HonestAgent(BaseAgent):
    def __init__(self, agent_id: str, llm: LLMProvider, max_rounds: int, initial_value: int, aware_of_adversaries=True):
        super().__init__(agent_id, llm, max_rounds)
        self.initial_value = initial_value
        self.current_value = initial_value
        self.aware_of_adversaries = aware_of_adversaries
        self.system_prompt = (prompts.HONEST_SYSTEM_PROMPT_MAY_AWARE if aware_of_adversaries 
                              else prompts.HONEST_SYSTEM_PROMPT_NO_ADVERSARY).format(
            agent_id=agent_id,
            max_rounds=max_rounds,
            value_min=self.value_min,
            value_max=self.value_max,
            initial_value=initial_value
        )

    def generate_proposal(self, round_num: int, history_summary: str) -> Dict[str, Any]:
        user_prompt = prompts.HONEST_ROUND_PROMPT.format(
            current_round=round_num,
            current_value=self.current_value,
            history_summary=history_summary,
            internal_strategy_history=self.internal_strategy_history
        )
        response_text = self.llm.complete(self.system_prompt, user_prompt)
        response = self._safe_json_parse(response_text)
        
        self.current_value = response.get("value", self.current_value)
        self.internal_strategy_history = response.get("internal_strategy", self.internal_strategy_history)
        
        return {
            "agent_id": self.agent_id,
            "value": self.current_value,
            "reasoning": response.get("public_reasoning", "No reasoning provided.")
        }

    def cast_vote(self, round_num: int, current_round_summary: str, history_summary: str) -> str:
        vote_prompt = (prompts.HONEST_VOTE_PROMPT_MAY_EXIST if self.aware_of_adversaries 
                       else prompts.HONEST_VOTE_PROMPT_NO_ADVERSARY).format(
            agent_id=self.agent_id,
            max_rounds=self.max_rounds
        )
        context = prompts.HONEST_ROUND_VOTE_DECISION_CONTEXT.format(
            current_round=round_num,
            max_rounds=self.max_rounds,
            current_round_summary=current_round_summary,
            history_summary=history_summary,
            internal_strategy_history=self.internal_strategy_history
        )
        response_text = self.llm.complete(vote_prompt, context)
        response = self._safe_json_parse(response_text)
        return response.get("decision", "continue")

class ByzantineAgent(BaseAgent):
    def __init__(self, agent_id: str, llm: LLMProvider, max_rounds: int):
        super().__init__(agent_id, llm, max_rounds)
        self.system_prompt = prompts.BYZANTINE_SYSTEM_PROMPT.format(
            agent_id=agent_id,
            max_rounds=max_rounds,
            value_min=self.value_min,
            value_max=self.value_max
        )

    def generate_proposal(self, round_num: int, history_summary: str) -> Dict[str, Any]:
        status = f"Your current value: {self.current_value}" if self.current_value is not None else "You have not proposed a value yet."
        user_prompt = prompts.BYZANTINE_ROUND_PROMPT.format(
            current_round=round_num,
            current_value_status=status,
            history_summary=history_summary,
            internal_strategy_history=self.internal_strategy_history
        )
        response_text = self.llm.complete(self.system_prompt, user_prompt)
        response = self._safe_json_parse(response_text)
        
        self.current_value = response.get("value", self.current_value)
        self.internal_strategy_history = response.get("internal_strategy", self.internal_strategy_history)
        
        return {
            "agent_id": self.agent_id,
            "value": self.current_value,
            "reasoning": response.get("public_reasoning", "No reasoning provided.")
        }

    def cast_vote(self, round_num: int, current_round_summary: str, history_summary: str) -> str:
        vote_prompt = prompts.BYZANTINE_VOTE_PROMPT.format(
            agent_id=self.agent_id,
            max_rounds=self.max_rounds
        )
        context = prompts.BYZANTINE_ROUND_VOTE_DECISION_CONTEXT.format(
            current_round=round_num,
            max_rounds=self.max_rounds,
            current_round_summary=current_round_summary,
            history_summary=history_summary
        )
        response_text = self.llm.complete(vote_prompt, context)
        response = self._safe_json_parse(response_text)
        return response.get("decision", "continue")
