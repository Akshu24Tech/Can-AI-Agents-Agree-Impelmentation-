import matplotlib.pyplot as plt
from typing import List, Dict, Any

def plot_trajectories(history: List[Dict[str, Any]], output_file: str = "consensus_trajectory.png"):
    """
    Plots the trajectories of agents' proposals over rounds, similar to Figure 4 in the paper.
    """
    rounds = [r['round'] for r in history]
    agent_ids = [p['agent_id'] for p in history[0]['proposals']]
    
    plt.figure(figsize=(10, 6))
    
    for agent_id in agent_ids:
        values = []
        for r in history:
            # Find proposal for this agent
            val = next((p['value'] for p in r['proposals'] if p['agent_id'] == agent_id), None)
            # Handle "abstain" or None
            if val == "abstain":
                val = None
            values.append(val)
            
        plt.plot(rounds, values, marker='o', label=f"Agent {agent_id}")
    
    plt.title("Byzantine Consensus Trajectory")
    plt.xlabel("Round")
    plt.ylabel("Proposed Value")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.ylim(-5, 55)
    
    plt.savefig(output_file)
    print(f"Trajectory plot saved to {output_file}")
    plt.close()
