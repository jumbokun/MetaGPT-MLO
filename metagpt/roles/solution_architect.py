from __future__ import annotations

import json
from typing import Literal

from pydantic import Field, model_validator

from metagpt.actions.add_requirement import UserRequirement
from metagpt.actions.di.ask_review import ReviewConst
from metagpt.actions.di.execute_nb_code import ExecuteNbCode
from metagpt.actions.di.write_analysis_code import CheckData, WriteAnalysisCode
from metagpt.logs import logger
from metagpt.prompts.di.write_analysis_code import DATA_INFO
from metagpt.roles import Role
from metagpt.schema import Message, Task, TaskResult
from metagpt.strategy.personal import Personal
from metagpt.tools.tool_recommend import BM25ToolRecommender, ToolRecommender
from metagpt.utils.common import CodeParser
from metagpt.actions.write_prd_MLOps import WritePRD
from metagpt.actions.review_prd import ReviewPRD, FeedbackHuman
from metagpt.actions.generate_init_sprint_plan import GenerateInitSprintPlan
from metagpt.actions.provide_feedback import ProvideFeedback
from metagpt.actions.publish_plan import PublishPlan
# from metagpt.actions.feedback_human import FeedbackHuman
from metagpt.strategy.personal import RoleType
SPRINT_THINK_PROMPT = """
# User Requirement
{user_requirement}

# Context/Current Plan
{context}

# MLOps Considerations
You are familiar with Machine Learning Operations (MLOps) and its phases, including project initiation, data engineering, model experimentation, and automated ML workflows. As a Solution Architect, your task is to translate the requirements into a structured sprint plan, considering the technical challenges and ensuring alignment with MLOps best practices.

# Step 1: Define Initial Sprint Goals
Based on the prioritized requirements and MLOps phases, divide the project into multiple sprints. For each sprint, provide the following details:
1. **Sprint Number**: The identifier for the sprint (e.g., Sprint 1, Sprint 2).
2. **Sprint Goal**: The main objective of this sprint, ensuring that it aligns with the overall MLOps workflow (e.g., data ingestion, model training, deployment).
3. **Deliverables**: What will be delivered at the end of this sprint (e.g., specific features, data pipelines, trained models, deployment scripts)?
4. **Assigned Requirements**: Which specific requirements will be addressed in this sprint? Ensure these requirements align with the MLOps phases and support continuous integration and deployment.

# Step 2: Address Technical Considerations
For each sprint, outline any technical considerations or challenges that need to be addressed, such as data availability, infrastructure needs, security concerns, or integration with existing systems. These should be factored into the sprint planning process.

# Output
The output should be structured as follows, please pay attention to the format requirement:
```json
{{
    "sprint_plan": [
        {{
            "sprint_number": "Sprint 1",
            "sprint_goal": "string",
            "deliverables": ["deliverable1", "deliverable2", ...],
            "assigned_requirements": ["requirement1", "requirement2", ...],
            "technical_considerations": ["consideration1", "consideration2", ...]
        }},
        ...
    ]
}}
"""

NEW_REQ_TEMPLATE = """
### Profile
{profile}

### Legacy Content
{old_plan}

### feedback
{context}

You are suggested to fit the sprint plan as given. 

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

DISPATCH_JOB_TEMPLATE = """
### Profile
{profile}

### plan
{plan}

### worth-to-know
{context}

### personal
{personal}


You are suggested to dispatch the job within a sprint as given. 

# Output
The output should be structured as follows, please pay attention to the format requirement:
```json
{{
    "current_sprint_plan": [
        {{
            "sprint_number": "Sprint 1",
            "sprint_goal": "string",
            "assigned_requirements": ["requirement1", "requirement2", ...],
            "assigned_personal": ["personal1", "personal2", ...]
        }},
        ...
    ]
}}
"""

test_result = """{
    "sprint_plan": [
        {
            "sprint_number": "Sprint 1",
            "sprint_goal": "Develop the classification module for lumbar spine degenerative conditions",
            "deliverables": ["Classification algorithm", "Data preprocessing module"],
            "assigned_requirements": ["Classify five lumbar spine degenerative conditions"]
        },
        {
            "sprint_number": "Sprint 2",
            "sprint_goal": "Develop the severity scoring module for each condition across intervertebral disc levels",
            "deliverables": ["Severity scoring algorithm", "Data visualization module"],
            "assigned_requirements": ["Provide severity scores for each of the five conditions across the intervertebral disc levels"]
        },
        {
            "sprint_number": "Sprint 3",
            "sprint_goal": "Improve system scalability and performance",
            "deliverables": ["Optimized database schema", "Caching mechanism"],
            "assigned_requirements": ["The system should be able to process a large dataset of images"]
        },
        {
            "sprint_number": "Sprint 4",
            "sprint_goal": "Enhance user experience and provide accurate results in a timely manner",
            "deliverables": ["User interface improvements", "Result validation module"],
            "assigned_requirements": ["The system should provide accurate results in a timely manner"]
        }
    ]
}
"""
class SolutionArchitect(Role):
    name: str = "SolutionArchtect"
    profile: str = "Designs system architecture, evaluates technical feasibility, and ensures seamless integration of all system components."
    scrum_profile: str = "Scrum Master"
    MLOps_profile: str = "Solution Architect"
    auto_run: bool = True
    use_plan: bool = True
    use_reflection: bool = False
    init: bool = True
    execute_code: ExecuteNbCode = Field(default_factory=ExecuteNbCode, exclude=True)
    tools: list[str] = []  # Use special symbol ["<all>"] to indicate use of all registered tools
    tool_recommender: ToolRecommender = None
    react_mode: Literal["plan_and_act", "react"] = "react"
    max_react_loop: int = 10  # used for react mode
    user_requirement: str = "None"
    reviewed: int = 0
    ask_round: int = 0
    feedback_collected: int = 0
    sprint_plan = ""
    @property
    def working_memory(self):

        return self.rc.working_memory

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Initialize actions specific to the Architect role
        self.set_actions([ReviewPRD, PublishPlan, GenerateInitSprintPlan])
        self._watch([UserRequirement, WritePRD, ProvideFeedback])


    @property
    def working_memory(self):
        return self.rc.working_memory
    
    # async def _observe(self, ignore_memory=False) -> int:
    #     """Deal with news"""
    #     return await super()._observe(ignore_memory)


    async def _think(self) -> bool:
        """Decide self.rc.todo in think"""
        news = self.rc.news[-1]
        logger.info(f"{self.name} got news, thingking. News from {news.cause_by}, news be like: {news.content[-20]}")

        if news.cause_by == self.rc.watch[0]:
            self.working_memory.add(news)
            # logger.info(f"Get users requirement: {news}")
            self.user_requirement = news
            return False
        
        # auto generate
        # if news.cause_by == self.rc.watch[1]:
        #     logger.info(f"{self.name} got info from {self.rc.watch[1]}")
        #     self.rc.todo = ReviewPRD
        #     return True

        
        if news.cause_by == self.rc.watch[1]:
            if self.reviewed < self.ask_round:
                self.rc.todo = FeedbackHuman
                return True
            else:
                self.rc.todo = GenerateInitSprintPlan
                return True
        
        if news.cause_by == self.rc.watch[2]:

            logger.info(f"{self.name} got info {self.rc.news[-5:-1]}")
            self.rc.todo = PublishPlan
            return True
        return False


    async def _act(self) -> Message:
        """Once todo decided in think, act."""
        
        # Feedback, and generate initial sprint plan
        logger.info(f"{self.name} is acting")
        if self.reviewed < self.ask_round:
            # give feedback
            if self.rc.todo == ReviewPRD or self.rc.todo == FeedbackHuman:
                logger.info(f"{self.name} is working on {self.rc.todo}")
                user_requirement = self.user_requirement
                plan = self.get_memories()[-1].content
                working_logs = self.working_memory.get()
                change_log = ""
                for m in working_logs:
                    if m.cause_by == ReviewPRD:
                        change_log += f"Changes: {m.content}\n"
                rsp = await self.rc.todo.run(self, user_requirement=user_requirement, plan=plan, change_log=change_log)
                print(rsp)
                self.working_memory.add(Message(content=rsp, role="assistant",cause_by=ReviewPRD)) 
                self.reviewed = self.reviewed + 1
                return Message(content=rsp, role="assistant", cause_by=ReviewPRD)

        else: 
            # generate init sprint plan
            if self.rc.todo == GenerateInitSprintPlan:
                user_requirement = self.user_requirement
                plan = self.get_memories()[-1].content
                working_logs = self.working_memory.get()
                
                # TODO: autogen
                # sprint_plan = await self.rc.todo.run(self, user_requirement=user_requirement, context=plan)
                sprint_plan = test_result

                msg = Message(content=sprint_plan, role="assistant", cause_by=GenerateInitSprintPlan)
                self.working_memory.clear()
                self.working_memory.add(msg)
                print(f"publishing message {msg}")
                return msg

        # publish sprint plan
        if self.rc.todo == PublishPlan:
            initial_plan = self.working_memory.get()[0]
            feedback = self.rc.news[-5:-1]
            prompt = NEW_REQ_TEMPLATE.format(profile=self.profile, context=feedback, old_plan=initial_plan)
            # logger.info(prompt)
            response = await self.llm.aask(prompt)
            rsp_json = json.loads(response)
            msg = Message(content=response, role="assistant", cause_by=PublishPlan)
            self.sprint_plan = rsp_json
            # start first sprint from here
            self.start_sprint(self, self.sprint_plan, 1)
            


    async def start_sprint(self, sprint_plan, sprint_number):
        """Assign personnel and tasks for the first sprint using GPT"""
        per = Personal()
        dev_team_str = per.generate_dev_team_string()
        dispatch_prompt = DISPATCH_JOB_TEMPLATE.format(
            profile=self.profile,
            plan=sprint_plan[sprint_number-1],
            context="This is about to start the sprint {sprint_number}",
            personal=dev_team_str
        )

        response = await self.llm.aask(dispatch_prompt)
        assigned_plan = json.loads(response)
        
        # Log assigned personnel for each task
        for sprint_detail in assigned_plan['current_sprint_plan']:
            sprint_goal = sprint_detail['sprint_goal']
            assigned_personal = sprint_detail['assigned_personal']
            logger.info(f"Assigned for Sprint Goal '{sprint_goal}': {assigned_personal}")

        # TODO: Start Sprint Meeting

    