from enum import Enum

from pydantic import BaseModel
from metagpt.prompts.milestone import (
    ARCHITECTURE_DESIGN_PROMPTS,
    BUSINESS_PROBLEM_IDENTIFICATION_PROMPTS,
    DATA_REQUIREMENTS_ANALYSIS_PROMPTS,
    DATA_SOURCES_LOCATING_PROMPTS,
    DEFINE_TRANSFORMATION_AND_CLEANING_RULES_PROMPTS,
    DEFINE_FEATURE_ENGINEERING_RULES_PROMPTS,
    CONNECT_TO_RAW_DATA_PROMPTS,
    DATA_EXTRACTION_PROMPTS,
    DATA_TRANSFORMATION_AND_CLEANING_PROMPTS,
    FEATURE_ENGINEERING_PROMPTS,
    DATA_INGESTION_JOB_PROMPTS,
    FEEDBACK_LOOP_AND_RULE_UPDATES_PROMPTS,
    DATA_ANALYSIS_PROMPTS,
    DATA_PREPARATION_AND_VALIDATION_PROMPTS,
    ML_PROBLEM_DEFINITION_PROMPTS,
    MODEL_TRAINING_PROMPTS,
    MODEL_VALIDATION_PROMPTS,
    EXPORT_MODEL_PROMPTS,
    AUTOMATED_ML_WORKFLOW_PROMPTS,
    AUTOMATED_FEATURE_EXTRACTION_PROMPTS,
    AUTOMATED_DATA_PREPARATION_AND_VALIDATION_PROMPTS,
    AUTOMATED_MODEL_TRAINING_PROMPTS,
    AUTOMATED_MODEL_VALIDATION_PROMPTS,
    EXPORT_AND_REGISTER_MODEL_PROMPTS,
    CI_CD_PIPELINE_TRIGGER_PROMPTS,
    MODEL_SERVING_PROMPTS,
    MONITORING_AND_FEEDBACK_PROMPTS,
    CONTINUOUS_TRAINING_PROMPTS,
)
class MilestoneTypeDef(BaseModel):
    name: str
    desc: str = ""
    guidance: str = ""
    stage: str = ""

class MilestonesMLOps(Enum):
    """By identifying specific types of tasks in MLOps, we can inject human priors (guidance) to help task solving"""

    BUSINESS_PROBLEM_IDENTIFICATION = MilestoneTypeDef(
        name="business problem identification",
        desc="The business stakeholder analyzes the business and identifies a potential business problem that can be solved using ML.",
        guidance=BUSINESS_PROBLEM_IDENTIFICATION_PROMPTS,
        stage="A"
    )

    ARCHITECTURE_DESIGN = MilestoneTypeDef(
        name="architecture design",
        desc="The solution architect defines the architecture design for the overall ML system and decides on the technologies to be used after a thorough evaluation.",
        guidance=ARCHITECTURE_DESIGN_PROMPTS,
        stage="A"
    )

    ML_PROBLEM_DEFINITION = MilestoneTypeDef(
        name="ML problem definition",
        desc="The data scientist derives an ML problem—such as whether regression or classification should be used—from the business goal.",
        guidance=ML_PROBLEM_DEFINITION_PROMPTS,
        stage="A"
    )

    DATA_REQUIREMENTS_ANALYSIS = MilestoneTypeDef(
        name="data requirements analysis",
        desc="The data engineer and the data scientist work together to understand which data is required to solve the ML problem.",
        guidance=DATA_REQUIREMENTS_ANALYSIS_PROMPTS,
        stage="A"
    )

    DATA_SOURCES_LOCATING = MilestoneTypeDef(
        name="data sources locating",
        desc="The data engineer and data scientist collaborate to locate the raw data sources for the initial data analysis, checking the distribution and quality of the data, and performing validation checks.",
        guidance=DATA_SOURCES_LOCATING_PROMPTS,
        stage="A"
    )


    # B1 Requirements for feature engineering pipeline
    DEFINE_TRANSFORMATION_AND_CLEANING_RULES = MilestoneTypeDef(
        name="define data cleaning rules",
        desc="Defines the data transformation rules (normalization, aggregations) and cleaning rules to bring the data into a usable format.",
        guidance=DEFINE_TRANSFORMATION_AND_CLEANING_RULES_PROMPTS,
        stage="B1"
    )

    DEFINE_FEATURE_ENGINEERING_RULES = MilestoneTypeDef(
        name="define feature engineering rules",
        desc="Define the feature engineering rules, such as the calculation of new and more advanced features based on other features.",
        guidance=DEFINE_FEATURE_ENGINEERING_RULES_PROMPTS,
        stage="B1"
    )

    # B2 Feature Engineering Pipeline
    CONNECT_TO_RAW_DATA = MilestoneTypeDef(
        name="connect to raw data",
        desc="The feature engineering pipeline first needs to connect to various data sources, including streaming data, static batch data, or data stored in cloud storage.",
        guidance=CONNECT_TO_RAW_DATA_PROMPTS,
        stage="B2"
    )

    DATA_EXTRACTION = MilestoneTypeDef(
        name="data extraction",
        desc="Extract data from the connected data sources, which is the first operational step of the feature engineering pipeline.",
        guidance=DATA_EXTRACTION_PROMPTS,
        stage="B2"
    )

    DATA_TRANSFORMATION_AND_CLEANING = MilestoneTypeDef(
        name="data transformation and cleaning",
        desc="Preprocess the extracted data, beginning with data transformation and cleaning tasks, to convert the data into a usable format.",
        guidance=DATA_TRANSFORMATION_AND_CLEANING_PROMPTS,
        stage="B2"
    )

    FEATURE_ENGINEERING = MilestoneTypeDef(
        name="feature engineering",
        desc="Perform feature engineering, such as calculating new features or modifying existing ones to ensure the data is suitable for model training.",
        guidance=FEATURE_ENGINEERING_PROMPTS,
        stage="B2"
    )

    DATA_INGESTION_JOB = MilestoneTypeDef(
        name="data ingestion job (batch or streaming)",
        desc="Ingest the processed data into the next stage, which could be in the form of batch processing or streaming.",
        guidance=DATA_INGESTION_JOB_PROMPTS,
        stage="B2"
    )

    FEEDBACK_LOOP_AND_RULE_UPDATES = MilestoneTypeDef(
        name="feedback loop and rule updates",
        desc="Update the feature engineering rules based on feedback from the experimental model engineering stage or from the monitoring component that observes the model’s performance in production.",
        guidance=FEEDBACK_LOOP_AND_RULE_UPDATES_PROMPTS,
        stage="B2"
    )

    # C Experimentation
    DATA_ANALYSIS = MilestoneTypeDef(
        name="data analysis",
        desc="The data scientist connects to the feature store system for data analysis. Alternatively, the data scientist can also connect to the raw data for an initial analysis. If data adjustments are required, the data scientist reports the necessary changes back to the data engineering zone.",
        guidance=DATA_ANALYSIS_PROMPTS,
        stage="C"
    )

    DATA_PREPARATION_AND_VALIDATION = MilestoneTypeDef(
        name="data preparation and validation",
        desc="Preparation and validation of data from the feature store system, including train and test split dataset creation.",
        guidance=DATA_PREPARATION_AND_VALIDATION_PROMPTS,
        stage="C"
    )

    MODEL_TRAINING = MilestoneTypeDef(
        name="model training",
        desc="The data scientist estimates the best-performing algorithm and hyperparameters. Model training is then triggered with the training data. The software engineer supports the creation of well-engineered model training code.",
        guidance=MODEL_TRAINING_PROMPTS,
        stage="C"
    )

    MODEL_VALIDATION = MilestoneTypeDef(
        name="model validation",
        desc="Different model parameters are tested and validated interactively during several rounds of model training. Iterative training continues until performance metrics indicate satisfactory results. The best-performing model parameters are identified via parameter tuning.",
        guidance=MODEL_VALIDATION_PROMPTS,
        stage="C"
    )

    EXPORT_MODEL = MilestoneTypeDef(
        name="export model",
        desc="The data scientist exports the model and commits the code to the repository.",
        guidance=EXPORT_MODEL_PROMPTS,
        stage="C"
    )

    AUTOMATED_ML_WORKFLOW = MilestoneTypeDef(
        name="automated ML workflow",
        desc="The DevOps engineer or the ML engineer defines the code for the automated ML workflow pipeline and commits it to the repository. The CI/CD component detects updated code and triggers the CI/CD pipeline, carrying out the build, test, and delivery steps.",
        guidance=AUTOMATED_ML_WORKFLOW_PROMPTS,
        stage="C"
    )

    # D Automated ML workflow pipeline
    AUTOMATED_FEATURE_EXTRACTION = MilestoneTypeDef(
        name="automated feature extraction",
        desc="Automated pulling of the versioned features from the feature store systems (data extraction). Depending on the use case, features are extracted from either the offline or online database (or any kind of data store).",
        guidance=AUTOMATED_FEATURE_EXTRACTION_PROMPTS,
        stage="D"
    )

    AUTOMATED_DATA_PREPARATION_AND_VALIDATION = MilestoneTypeDef(
        name="automated data preparation and validation",
        desc="Automated data preparation and validation, including the automated definition of train and test splits.",
        guidance=AUTOMATED_DATA_PREPARATION_AND_VALIDATION_PROMPTS,
        stage="D"
    )

    AUTOMATED_MODEL_TRAINING = MilestoneTypeDef(
        name="automated model training",
        desc="Automated final model training on new unseen data (versioned features). The algorithm and hyperparameters are predefined based on the settings of the previous experimentation stage. The model is retrained and refined.",
        guidance=AUTOMATED_MODEL_TRAINING_PROMPTS,
        stage="D"
    )

    AUTOMATED_MODEL_VALIDATION = MilestoneTypeDef(
        name="automated model validation",
        desc="Automated model evaluation and iterative adjustments of hyperparameters are executed, if required. Training and validation are iterated until performance metrics indicate satisfactory results.",
        guidance=AUTOMATED_MODEL_VALIDATION_PROMPTS,
        stage="D"
    )

    EXPORT_AND_REGISTER_MODEL = MilestoneTypeDef(
        name="export and register model",
        desc="The trained model is exported and pushed to the model registry, where it is stored with its associated configuration and environment files.",
        guidance=EXPORT_AND_REGISTER_MODEL_PROMPTS,
        stage="D"
    )

    CI_CD_PIPELINE_TRIGGER = MilestoneTypeDef(
        name="CI/CD pipeline trigger",
        desc="Once the status of a well-performing model is switched from staging to production, the CI/CD component triggers the continuous deployment pipeline, handling the build, test, and deployment steps.",
        guidance=CI_CD_PIPELINE_TRIGGER_PROMPTS,
        stage="D"
    )

    MODEL_SERVING = MilestoneTypeDef(
        name="model serving",
        desc="The model serving component makes predictions on new, unseen data from the feature store system. This component supports both online inference for real-time predictions and batch inference for large volumes of input data.",
        guidance=MODEL_SERVING_PROMPTS,
        stage="D"
    )

    MONITORING_AND_FEEDBACK = MilestoneTypeDef(
        name="monitoring and feedback",
        desc="The monitoring component observes model-serving performance and infrastructure in real-time. Feedback is provided when certain thresholds, like low prediction accuracy, are reached, enabling continuous improvement.",
        guidance=MONITORING_AND_FEEDBACK_PROMPTS,
        stage="D"
    )

    CONTINUOUS_TRAINING = MilestoneTypeDef(
        name="continuous training",
        desc="Continuous training is triggered based on feedback from the monitoring component, such as detection of concept drift. Retraining can be triggered automatically, when new feature data is available, or scheduled periodically.",
        guidance=CONTINUOUS_TRAINING_PROMPTS,
        stage="D"
    )
    
    @property
    def type_name(self):
        return self.value.name

    @classmethod
    def get_type(cls, type_name):
        for member in cls:
            if member.type_name == type_name:
                return member.value
        return None