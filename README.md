# Byzantine Consensus Game Simulator (A2A-Sim)

This project is a Python-based implementation of the "Byzantine Consensus Game" as described in the research paper **"Can AI Agents Agree?"** (Berdoz et al., 2026).

It simulates a multi-agent environment where Large Language Model (LLM) agents attempt to reach a consensus on a scalar value, even in the presence of **Byzantine (malicious)** agents who try to disrupt the agreement.

## 🚀 Key Features
- **A2A-Sim Protocol**: Full synchronous all-to-all communication simulation.
- **Agent Roles**: Support for **Honest** (cooperative) and **Byzantine** (adversarial) agents.
- **Research Prompts**: Includes exact prompt templates from the ETH Zurich paper (Figures 5–14).
- **Consensus Logic**: Implements the **2/3 supermajority** voting rule for termination.
- **Visualization**: Generates consumption trajectory plots showing agent proposals over time.

## 📁 Project Structure
- `consensus_sim/`: Core package.
  - `agents.py`: LLM-based agent logic (Honest vs Byzantine).
  - `simulator.py`: Orchestration of rounds and voting.
  - `prompts.py`: Prompt templates used for communication and voting.
  - `llm_provider.py`: Abstraction for LLM backends (Mock support + Gemini).
  - `visualizer.py`: Tool for plotting consensus trajectories.
- `main.py`: CLI entry point to run simulations.
- `2603.01213v1.pdf`: The original research paper.
- `consensus_trajectory.png`: Generated visual output of the latest run.

## 🛠️ Usage

### Prerequisites
- Python 3.8+
- Requirements: `matplotlib`, `google-generativeai` (for Gemini provider)

### Running a Simulation
You can run a simulation with configurable agent counts. By default, it uses a `MockLLM` for demonstration without needing an API key.

```bash
# Example: 4 honest agents, 1 byzantine agent, 15 rounds max
python -m consensus_sim.main --n-honest 4 --n-byzantine 1 --max-rounds 15
```

### Options
- `--n-honest`: Number of cooperative agents.
- `--n-byzantine`: Number of malicious agents.
- `--max-rounds`: Maximum number of rounds before timeout.
- `--aware`: If set, honest agents are warned that Byzantine peers may exist (matching "Adversary-Aware" experiments in the paper).

## 📊 Findings from the Paper
- **Fragility**: LLMs lack deterministic guarantees, making consensus an emergent but unstable property.
- **Scalability**: Success rates drop significantly as the number of agents increases.
- **Byzantine Impact**: Even one malicious agent can effectively stall consensus by causing timeouts.
- **Awareness Cost**: Mentioning adversaries in prompts often *harms* consensus by making honest agents too cautious.

## 🔗 Related Artifacts
- [Paper Summary](file:///C:/Users/techl/.gemini/antigravity/brain/59dae66f-fb83-4a91-9b95-610fbf5b8d49/paper_summary.md)
- [Implementation Walkthrough](file:///C:/Users/techl/.gemini/antigravity/brain/59dae66f-fb83-4a91-9b95-610fbf5b8d49/walkthrough.md)
