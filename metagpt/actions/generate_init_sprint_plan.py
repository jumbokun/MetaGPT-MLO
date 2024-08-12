from metagpt.actions.action import Action
from metagpt.schema import Message, Task, TaskResult
from metagpt.utils.common import CodeParser
from metagpt.logs import logger

SPRINT_THINK_PROMPT = """
# User Requirement
{user_requirement}

# Context/current plan
{context}

# Step 1: Define Initial Sprint Goals
Based on the prioritized requirements, divide the project into multiple sprints. For each sprint, provide the following details:
1. **Sprint Number**: The identifier for the sprint (e.g., Sprint 1, Sprint 2).
2. **Sprint Goal**: The main objective of this sprint.
3. **Deliverables**: What will be delivered at the end of this sprint (e.g., specific features, modules)?
4. **Assigned Requirements**: Which specific requirements will be addressed in this sprint?

# Output
The output should be structured as follows, please pay attention to the format requirement:
```json
{{
    "sprint_plan": [
        {{
            "sprint_number": "Sprint 1",
            "sprint_goal": "string",
            "deliverables": ["deliverable1", "deliverable2", ...],
            "assigned_requirements": ["requirement1", "requirement2", ...]
        }},
        ...
    ]
}}
"""

class GenerateInitSprintPlan(Action):
    async def run(self, user_requirement, context, **kwargs) -> str:
        """
        Generate improvement suggestions for the provided business requirement document.
        :return: JSON string containing improvement suggestions.
        """
        prompt = SPRINT_THINK_PROMPT.format(user_requirement=user_requirement, context=context)
        response = await self.llm.aask(prompt)
        return response

class FeedbackHuman(Action):
    async def run(self, plan, **kwargs) -> str:
       
        print("Please review the following update and provide your feedback:")
        print(plan)

        rsp = input("Enter your feedback:")

        return rsp

