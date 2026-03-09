import argparse
import random
from .simulator import ConsensusSimulator
from .agents import HonestAgent, ByzantineAgent
from .llm_provider import MockLLM
from .visualizer import plot_trajectories

def main():
    parser = argparse.ArgumentParser(description="Byzantine Consensus Simulator")
    parser.add_argument("--n-honest", type=int, default=3, help="Number of honest agents")
    parser.add_argument("--n-byzantine", type=int, default=1, help="Number of Byzantine agents")
    parser.add_argument("--max-rounds", type=int, default=10, help="Maximum rounds")
    parser.add_argument("--aware", action="store_true", help="Honest agents are aware of Byzantine presence")
    
    args = parser.parse_args()
    
    # Using MockLLM for demonstration
    llm = MockLLM()
    
    agents = []
    # Create Honest Agents
    for i in range(args.n_honest):
        initial_val = random.randint(0, 50)
        agents.append(HonestAgent(f"H{i}", llm, args.max_rounds, initial_val, aware_of_adversaries=args.aware))
        
    # Create Byzantine Agents
    for i in range(args.n_byzantine):
        agents.append(ByzantineAgent(f"B{i}", llm, args.max_rounds))
        
    # Run Simulation
    sim = ConsensusSimulator(agents, max_rounds=args.max_rounds)
    history = sim.run_all()
    
    # Plot results
    plot_trajectories(history)

if __name__ == "__main__":
    main()
