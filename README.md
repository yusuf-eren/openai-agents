# Self-Correcting Collaborative Agents

A powerful AI agent pattern built with OpenAI Agents for complex tasks requiring multiple expertise domains.

## Overview

The Self-Correcting Collaborative Agents pattern leverages OpenAI Agents to enable multiple specialized AI agents to work together on complex tasks, while monitoring each other's work and providing real-time feedback. Unlike sequential agent patterns or parallelization with result selection, this pattern creates a true collaborative environment where agents can detect and correct each other's errors throughout the analysis process.

## Key Features

- **Multi-expert collaboration**: Employs multiple specialized agents with different domain expertise
- **Shared workspace concept**: Agents work in a common environment with visibility into each other's reasoning
- **Real-time feedback mechanism**: Experts review and correct each other's work during the analysis
- **Weighted expertise integration**: Coordinator determines relative importance of different expertise areas
- **Conflict resolution**: Handles disagreements through confidence scoring and expertise weighting
- **Dissenting opinion preservation**: Maintains alternative viewpoints when significant

## Use Cases

This pattern is especially valuable for complex analyses requiring multiple types of expertise:

- **Financial Analysis**: Combining accounting, industry, and risk assessment perspectives
- **Medical Diagnosis**: Integrating input from different medical specialties
- **Legal Document Preparation**: Merging expertise from different legal domains
- **Research Synthesis**: Combining scientific, statistical, and domain-specific knowledge
- **Product Development**: Integrating technical, design, and market perspectives

## How It Works

1. **Task Analysis**: A coordinator agent analyzes the task and determines which expertise areas are needed
2. **Team Assembly**: Specialized agents are selected based on required expertise
3. **Initial Analysis**: Each expert analyzes the task from their perspective
4. **Collaborative Review**: Experts review each other's work and provide feedback
5. **Integration**: An integration agent combines all analyses, weighing inputs based on expertise relevance
6. **Final Output**: Comprehensive analysis with key insights and any significant dissenting opinions

## Implementation Example

The repository includes a complete implementation using OpenAI Agents for financial analysis with:

- Coordinator agent for task analysis powered by OpenAI
- Specialized OpenAI Agents for accounting, industry, and risk assessment
- Feedback mechanisms for inter-agent correction using OpenAI's capabilities
- Integration process for producing final analysis with weighted expertise

## Advantages Over Other Patterns

| Pattern | Advantage of Collaborative Agents |
|---------|-----------------------------------|
| Deterministic Flow | Real-time corrections vs. sequential steps |
| Parallelization | Synthesis of expertise vs. choosing best result |
| LLM-as-Judge | Ongoing feedback vs. post-completion review |
| Routing | Simultaneous collaboration vs. handoffs |

## Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY=your_api_key_here
```

3. Run the example:
```bash
python self_correcting_collaborative_agents.py
```

4. Enter your financial analysis task when prompted

## Customizing for Other Domains

The OpenAI Agents pattern can be adapted to other domains by:

1. Defining domain-specific expertise areas
2. Creating specialized OpenAI Agents with appropriate instructions
3. Adjusting the integration logic to suit domain requirements
4. Leveraging OpenAI's capabilities for domain-specific reasoning

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.