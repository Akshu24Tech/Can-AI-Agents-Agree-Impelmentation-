from typing import List, Dict, Any
from .agents import BaseAgent, HonestAgent, ByzantineAgent
from .llm_provider import LLMProvider

class ConsensusSimulator:
    def __init__(self, agents: List[BaseAgent], max_rounds: int = 15):
        self.agents = agents
        self.max_rounds = max_rounds
        self.current_round = 0
        self.history = []  # List of round data
        self.terminated = False
        self.final_consensus_value = None
        self.termination_type = "Timeout"  # Default

    def _get_history_summary(self) -> str:
        """
        Creates a compact textual summary of previous rounds for LLM context.
        Matches the paper's description: previous round's proposals and justifications.
        """
        if not self.history:
            return "(This is round 1 - no previous history)"
        
        last_round = self.history[-1]
        summary_lines = [f"Summary of Round {last_round['round']}:"]
        for prop in last_round['proposals']:
            summary_lines.append(f"- Agent {prop['agent_id']} proposed {prop['value']}: {prop['reasoning']}")
        
        return "\n".join(summary_lines)

    def _get_current_round_summary(self, proposals: List[Dict[str, Any]]) -> str:
        summary_lines = []
        for prop in proposals:
            summary_lines.append(f"- Agent {prop['agent_id']} proposed {prop['value']}")
        return "\n".join(summary_lines)

    def run_round(self):
        self.current_round += 1
        history_summary = self._get_history_summary()
        
        # 1. Collect Proposals
        proposals = []
        for agent in self.agents:
            prop = agent.generate_proposal(self.current_round, history_summary)
            proposals.append(prop)
            
        current_round_summary = self._get_current_round_summary(proposals)
        
        # 2. Collect Votes
        votes = []
        stop_count = 0
        for agent in self.agents:
            vote = agent.cast_vote(self.current_round, current_round_summary, history_summary)
            votes.append({"agent_id": agent.agent_id, "vote": vote})
            if vote == "stop":
                stop_count += 1
                
        # 3. Record Round
        round_data = {
            "round": self.current_round,
            "proposals": proposals,
            "votes": votes,
            "stop_count": stop_count
        }
        self.history.append(round_data)
        
        # 4. Check for Termination (2/3 supermajority)
        threshold = (2 * len(self.agents)) / 3
        if stop_count >= threshold:
            self.terminated = True
            self.termination_type = "Consensus Reached"
            # Check if all honest agents agree on the same value
            honest_values = [p['value'] for p in proposals if any(isinstance(a, HonestAgent) and a.agent_id == p['agent_id'] for a in self.agents)]
            if len(set(honest_values)) == 1:
                self.final_consensus_value = honest_values[0]
                self.termination_type = "Valid Consensus"
            else:
                self.termination_type = "Invalid Consensus (Disagreement)"
        
        elif self.current_round >= self.max_rounds:
            self.terminated = True
            self.termination_type = "Timeout (No Consensus)"

    def run_all(self):
        print(f"Starting simulation with {len(self.agents)} agents...")
        while not self.terminated:
            print(f"--- Round {self.current_round + 1} ---")
            self.run_round()
            last_round = self.history[-1]
            print(f"Stop votes: {last_round['stop_count']}/{len(self.agents)}")
            
        print(f"Simulation Terminated: {self.termination_type}")
        if self.final_consensus_value is not None:
             print(f"Final Value: {self.final_consensus_value}")
        return self.history
