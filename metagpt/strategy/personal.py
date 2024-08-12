from enum import Enum
from pydantic import BaseModel
from metagpt.roles.stakeholder import Stakeholder
from metagpt.roles.solution_architect import SolutionArchitect
from metagpt.roles.data_scientist import DataScientist
from metagpt.roles.data_engineer import DataEngineer
from metagpt.roles.software_engineer import SoftwareEngineer
from metagpt.roles.DevOps_engineer import DevOpsEngineer
from metagpt.roles.ML_engineer import MLEngineer

class RoleTypeDef(BaseModel):
    name: str
    desc: str = ""
    guidance: str = ""
    role: type = None  # 添加role字段的类型提示

class Personal(Enum):
    """Defines roles in the project with specific responsibilities and perspectives"""

    BUSINESS_STAKEHOLDER = RoleTypeDef(
        name="Business Stakeholder",
        desc="Focuses on aligning business goals with technical solutions, prioritizes ROI, and ensures clear communication of business requirements.",
        guidance="Ensure that all business goals are clearly communicated and that they align with the project's technical capabilities.",
        role=Stakeholder
    )
    SOLUTION_ARCHITECT = RoleTypeDef(
        name="Solution Architect",
        desc="Designs system architecture, evaluates technical feasibility, and ensures seamless integration of all system components.",
        guidance="Focus on the overall system design, making sure that the architecture supports scalability, performance, and security.",
        role=SolutionArchitect
    )
    DATA_SCIENTIST = RoleTypeDef(
        name="Data Scientist",
        desc="Applies data-driven approaches to solve business problems, focuses on model performance, and ensures data quality.",
        guidance="Select appropriate models and algorithms that best fit the problem, and ensure data quality through rigorous preprocessing.",
        role=DataScientist
    )
    DATA_ENGINEER = RoleTypeDef(
        name="Data Engineer",
        desc="Builds and optimizes data pipelines, ensures data flow and quality, and collaborates closely with Data Scientists for seamless data integration.",
        guidance="Focus on building robust data pipelines that can handle large-scale data efficiently, ensuring that data is clean and ready for analysis.",
        role=DataEngineer
    )
    SOFTWARE_ENGINEER = RoleTypeDef(
        name="Software Engineer",
        desc="Implements software solutions, integrates models into systems, and ensures code quality and system reliability.",
        guidance="Ensure that all code follows best practices for software development, including testing, documentation, and optimization for performance.",
        role=SoftwareEngineer
    )
    DEVOPS_ENGINEER = RoleTypeDef(
        name="DevOps Engineer",
        desc="Manages CI/CD pipelines, automates deployments, and monitors production environments for stability and performance.",
        guidance="Automate as much of the deployment and monitoring process as possible, focusing on stability and quick recovery from issues.",
        role=DevOpsEngineer
    )
    MLOPS_ENGINEER = RoleTypeDef(
        name="ML Engineer / MLOps Engineer",
        desc="Integrates and manages ML infrastructure, automates workflows, and monitors models in production to ensure high availability and performance.",
        guidance="Ensure that ML models are well-integrated into the production environment, with automated workflows for deployment and monitoring.",
        role=MLEngineer
    )

    def get_developer_team():
        """
        Returns all Personal roles except Solution Architect and Business Stakeholder.
        """
        excluded_roles = {"SOLUTION_ARCHITECT", "BUSINESS_STAKEHOLDER"}
        return [role for role in Personal if role.name not in excluded_roles]
    def generate_dev_team_string(self):
        """
        Generates a string listing the name and description of each role in the developer team.
        """
        developer_team = self.get_developer_team()
        team_string = ""
        
        for role in developer_team:
            team_string += f"{role.value.name}: {role.value.desc}\n"
        
        return team_string