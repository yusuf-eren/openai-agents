from agents import Agent, Runner, function_tool, WebSearchTool
from pydantic import BaseModel


class AgentOutput(BaseModel):
    final_output: str

# Custom Tool Example
@function_tool
def weather_search(location: str) -> str:
    return f"The weather in {location} is sunny"

# Agent Declaration
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model="gpt-4o",
    tools=[
        WebSearchTool(
            user_location={
                "type": "approximate",
                "city": "Istanbul",
                "country": "TR",
                "region": "Istanbul",
                "timezone": "Europe/Istanbul",
            }
        ),
        weather_search,
    ],
    output_type=AgentOutput,
)

result = Runner.run_sync(agent, "How is the weather today in Istanbul?")
print(result.final_output)
