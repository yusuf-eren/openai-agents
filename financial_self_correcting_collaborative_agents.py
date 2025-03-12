import asyncio
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field

from agents import Agent, Runner, ItemHelpers, trace, TResponseInputItem

"""
This example demonstrates the Self-Correcting Collaborative Agents pattern.
Multiple agents with different expertise collaborate on a task, monitor each other's work,
and intervene when they detect errors or areas for improvement.

The workflow:
1. A coordinator agent analyzes the task and assembles a team of specialized agents
2. All agents work in a shared "workspace" with visibility into each other's thought processes
3. Agents can flag issues in others' reasoning with confidence levels
4. A weighted voting mechanism resolves conflicts based on expertise
5. Agents can shift roles based on task needs and demonstrated performance

This example implements financial analysis with three expert agents:
- Accounting expert
- Industry analyst
- Risk assessment specialist
"""


class ExpertiseArea(str, Enum):
    ACCOUNTING = "accounting"
    INDUSTRY = "industry"
    RISK = "risk"


class AgentThought(BaseModel):
    reasoning: str = Field(description="The agent's reasoning process")
    conclusion: str = Field(description="The agent's conclusion based on the reasoning")
    confidence: float = Field(description="Confidence level from 0.0 to 1.0")


class AgentFeedback(BaseModel):
    target_agent: str = Field(description="The name of the agent receiving feedback")
    feedback: str = Field(description="Constructive feedback on the agent's work")
    suggested_correction: Optional[str] = Field(
        description="Suggested correction, if applicable"
    )
    confidence: float = Field(description="Confidence in this feedback from 0.0 to 1.0")


class CoordinatorOutput(BaseModel):
    task_analysis: str = Field(description="Analysis of the financial task")
    required_expertise: List[ExpertiseArea] = Field(
        description="Required areas of expertise"
    )
    accounting_weight: float = Field(
        description="Weight for accounting expertise",
    )
    industry_weight: float = Field(
        description="Weight for industry expertise",
    )
    risk_weight: float = Field(
        description="Weight for risk expertise",
    )


class ExpertAgentOutput(BaseModel):
    expertise_area: ExpertiseArea
    thoughts: AgentThought
    feedback_on_others: List[AgentFeedback] = Field(default_factory=list)


class FinalAnalysisOutput(BaseModel):
    integrated_analysis: str = Field(description="The final integrated analysis")
    confidence_level: float = Field(description="Overall confidence in the analysis")
    key_insights: List[str] = Field(description="Key insights from the analysis")
    dissenting_opinions: Optional[List[str]] = Field(
        description="Any significant dissenting opinions"
    )


# Define the agents
coordinator_agent = Agent(
    name="coordinator_agent",
    instructions=(
        "You analyze financial tasks and determine which expertise is needed. "
        "For each task, evaluate what mix of accounting, industry, and risk assessment expertise is required. "
        "Assign weights to each expertise area based on its importance to the task."
    ),
    output_type=CoordinatorOutput,
)

accounting_expert = Agent(
    name="accounting_expert",
    instructions=(
        "You are an expert in accounting and financial statements. "
        "Analyze the financial task from an accounting perspective. "
        "Review other experts' work and provide feedback when you see accounting errors. "
        "Be specific about accounting principles, financial reporting standards, and calculations."
    ),
    output_type=ExpertAgentOutput,
)

industry_expert = Agent(
    name="industry_expert",
    instructions=(
        "You are an expert in industry analysis and market trends. "
        "Analyze the financial task from an industry perspective. "
        "Review other experts' work and provide feedback when you see misconceptions about the industry. "
        "Be specific about industry benchmarks, trends, and competitive factors."
    ),
    output_type=ExpertAgentOutput,
)

risk_expert = Agent(
    name="risk_expert",
    instructions=(
        "You are an expert in risk assessment and financial risk management. "
        "Analyze the financial task from a risk management perspective. "
        "Review other experts' work and provide feedback when you see overlooked risks. "
        "Be specific about risk factors, probabilities, and potential mitigation strategies."
    ),
    output_type=ExpertAgentOutput,
)

integration_agent = Agent(
    name="integration_agent",
    instructions=(
        "You integrate the analyses and feedback from all expert agents. "
        "Weigh their inputs based on the expertise weights provided by the coordinator. "
        "Resolve conflicts by considering confidence levels and expertise relevance. "
        "Produce a comprehensive final analysis that incorporates all valid insights."
    ),
    output_type=FinalAnalysisOutput,
)


async def collect_expert_outputs(
    task_description: str, coordinator_output: CoordinatorOutput
) -> List[ExpertAgentOutput]:
    """Run all expert agents in parallel and collect their outputs."""
    expert_agents = {
        ExpertiseArea.ACCOUNTING: accounting_expert,
        ExpertiseArea.INDUSTRY: industry_expert,
        ExpertiseArea.RISK: risk_expert,
    }

    # Filter agents based on required expertise
    required_agents = [
        expert_agents[area] for area in coordinator_output.required_expertise
    ]

    # Create a shared workspace that includes the task and coordinator's assessment
    workspace = (
        f"Task: {task_description}\n\n"
        f"Task Analysis: {coordinator_output.task_analysis}\n\n"
        f"Required Expertise: {', '.join(coordinator_output.required_expertise)}\n\n"
    )

    # Run all required expert agents in parallel
    expert_tasks = [Runner.run(agent, workspace) for agent in required_agents]

    expert_results = await asyncio.gather(*expert_tasks)
    return [result.final_output_as(ExpertAgentOutput) for result in expert_results]


async def collaborative_feedback_round(
    expert_outputs: List[ExpertAgentOutput],
) -> List[ExpertAgentOutput]:
    """Run a round of collaborative feedback where experts review each other's work."""
    # Create a workspace with all expert thoughts visible to each other
    workspace = "SHARED WORKSPACE - EXPERT ANALYSES:\n\n"

    for output in expert_outputs:
        workspace += (
            f"--- {output.expertise_area.upper()} EXPERT ANALYSIS ---\n"
            f"Reasoning: {output.thoughts.reasoning}\n"
            f"Conclusion: {output.thoughts.conclusion}\n"
            f"Confidence: {output.thoughts.confidence}\n\n"
        )

    # Let each expert review the workspace and provide feedback
    feedback_tasks = []
    for i, output in enumerate(expert_outputs):
        # Create a special prompt for this expert to review others' work
        review_prompt = (
            f"{workspace}\n\n"
            f"You are the {output.expertise_area.upper()} EXPERT. "
            f"Review the analyses above and provide feedback on any errors or oversights "
            f"from your expertise perspective. Focus especially on areas where your "
            f"expertise gives you unique insight."
        )

        # Use the same expert agent, but with a modified prompt
        if output.expertise_area == ExpertiseArea.ACCOUNTING:
            feedback_tasks.append(Runner.run(accounting_expert, review_prompt))
        elif output.expertise_area == ExpertiseArea.INDUSTRY:
            feedback_tasks.append(Runner.run(industry_expert, review_prompt))
        elif output.expertise_area == ExpertiseArea.RISK:
            feedback_tasks.append(Runner.run(risk_expert, review_prompt))

    feedback_results = await asyncio.gather(*feedback_tasks)
    return [result.final_output_as(ExpertAgentOutput) for result in feedback_results]


async def main():
    # Get the financial analysis task from the user
    task_description = input(
        "Describe the financial analysis task you need help with: "
    )

    # We'll trace the entire workflow for better observability
    with trace("Self-Correcting Collaborative Agents"):
        # Step 1: Coordinator analyzes the task
        print("\nAnalyzing task requirements...")
        coordinator_result = await Runner.run(coordinator_agent, task_description)
        coordinator_output = coordinator_result.final_output_as(CoordinatorOutput)

        print(f"Required expertise: {', '.join(coordinator_output.required_expertise)}")
        print(
            f"Expertise weights: Accounting: {coordinator_output.accounting_weight}, Industry: {coordinator_output.industry_weight}, Risk: {coordinator_output.risk_weight}"
        )

        # Step 2: Expert agents analyze the task in parallel
        print("\nExperts analyzing the task...")
        expert_outputs = await collect_expert_outputs(
            task_description, coordinator_output
        )

        # Step 3: Collaborative feedback round
        print("\nExperts reviewing each other's work...")
        refined_expert_outputs = await collaborative_feedback_round(expert_outputs)

        # Step 4: Integration agent combines all analyses and feedback
        print("\nIntegrating analyses and feedback...")

        # Create an integration workspace with all expert analyses and feedback
        integration_workspace = (
            f"Task: {task_description}\n\n"
            f"Coordinator Analysis: {coordinator_output.task_analysis}\n\n"
            f"Expertise Weights: Accounting: {coordinator_output.accounting_weight}, Industry: {coordinator_output.industry_weight}, Risk: {coordinator_output.risk_weight}\n\n"
            "EXPERT ANALYSES AND FEEDBACK:\n\n"
        )

        for output in refined_expert_outputs:
            integration_workspace += (
                f"--- {output.expertise_area.upper()} EXPERT ---\n"
                f"Analysis: {output.thoughts.conclusion}\n"
                f"Confidence: {output.thoughts.confidence}\n"
                "Feedback on others:\n"
            )

            for feedback in output.feedback_on_others:
                integration_workspace += (
                    f"  - To {feedback.target_agent}: {feedback.feedback}\n"
                    f"    Suggested correction: {feedback.suggested_correction}\n"
                    f"    Confidence: {feedback.confidence}\n"
                )

            integration_workspace += "\n"

        integration_result = await Runner.run(integration_agent, integration_workspace)
        final_analysis = integration_result.final_output_as(FinalAnalysisOutput)

        # Display the final integrated analysis
        print("\n=== FINAL INTEGRATED ANALYSIS ===")
        print(f"\n{final_analysis.integrated_analysis}")
        print(f"\nConfidence Level: {final_analysis.confidence_level * 100:.1f}%")

        print("\nKey Insights:")
        for i, insight in enumerate(final_analysis.key_insights, 1):
            print(f"{i}. {insight}")

        if final_analysis.dissenting_opinions:
            print("\nDissenting Opinions:")
            for i, opinion in enumerate(final_analysis.dissenting_opinions, 1):
                print(f"{i}. {opinion}")


if __name__ == "__main__":
    asyncio.run(main())
