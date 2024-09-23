from metagpt.actions import Action, ActionOutput
from metagpt.logs import logger

SELECT_TECH_STACK_PROMPT = """
Based on the following project requirements and stakeholder suggestions, suggest the most appropriate frameworks and technologies to use in the MLOps pipeline.

# User Requirements:
{requirements}

# Stakeholder Suggestions:
{suggestions}

Please provide the output as a newline-separated list of technologies/frameworks. Each technology should be on a new line. For example:

PyTorch==1.9.0
Kubernetes==1.18.0
Airflow==2.0.1

Make sure the output follows this exact format.
"""

class SelectTechStack(Action):
    """Select the tech stack for the project based on user requirements and stakeholder suggestions."""
    
    async def run(self, requirements: str, stakeholder_suggestions: str) -> ActionOutput:
        prompt = SELECT_TECH_STACK_PROMPT.format(requirements=requirements, suggestions=stakeholder_suggestions)
        tech_stack = await self.llm.aask(prompt)
        
        tech_stack_list = tech_stack.strip().split("\n")  # 使用换行符分隔列表
        logger.info(f"Selected tech stack: {tech_stack_list}")
        
        return ActionOutput(content=tech_stack, instruct_content=tech_stack_list)