# A
BUSINESS_PROBLEM_IDENTIFICATION_PROMPTS = """
The current task is about identifying a business problem that can be solved using ML, please note the following:
- Collaborate with stakeholders to thoroughly understand the business context and the challenges they face.
- Identify key performance indicators (KPIs) that the business aims to improve through the ML solution.
- Document the identified business problem, ensuring it is specific, measurable, and aligned with business goals.
- Validate the problem with relevant stakeholders to ensure it is a priority and worth solving with ML.
"""

ARCHITECTURE_DESIGN_PROMPTS = """
The current task is about designing the architecture for the ML system, please note the following:
- Conduct a thorough evaluation of potential technologies and tools that align with the project's requirements.
- Define the high-level architecture, ensuring scalability, reliability, and ease of integration with existing systems.
- Document the architecture design, including data flow diagrams, component interactions, and technology choices.
- Ensure that the design is reviewed and approved by relevant stakeholders, including data engineers, ML engineers, and IT teams.
"""

ML_PROBLEM_DEFINITION_PROMPTS = """
The current task is about defining the ML problem based on the business goal, please note the following:
- Analyze the business problem to determine the most appropriate ML approach, such as regression, classification, or clustering.
- Define the target variable and the type of supervised, unsupervised, or reinforcement learning approach to be used.
- Document the ML problem statement, including the rationale for the chosen approach and any assumptions made.
- Validate the problem definition with stakeholders to ensure it aligns with business objectives and is feasible given the available data.
"""

DATA_REQUIREMENTS_ANALYSIS_PROMPTS = """
The current task is about analyzing data requirements, please note the following:
- Collaborate with the data engineer to identify the types of data needed to solve the ML problem.
- Determine the volume, variety, and velocity of data required and the sources from which it can be obtained.
- Ensure that data quality is sufficient for ML purposes, considering factors like completeness, accuracy, and timeliness.
- Document the data requirements, including any specific preprocessing steps needed to prepare the data for analysis.
- Review and validate the data requirements with the broader project team to ensure they are comprehensive and realistic.
"""

DATA_SOURCES_LOCATING_PROMPTS = """
The current task is about locating and validating data sources, please note the following:
- Work with the data engineer to locate and access the raw data sources required for initial analysis.
- Perform an initial assessment of data distribution, quality, and completeness, checking for issues like missing values or outliers.
- Validate that the data is labeled correctly, especially for supervised ML tasks, ensuring the target variable is well-defined.
- Document the data sources, including their location, format, and any issues encountered during the validation process.
- Review the findings with the project team to ensure the data is suitable for the intended ML tasks.
"""

# B1
DEFINE_TRANSFORMATION_AND_CLEANING_RULES_PROMPTS = """
The current task is about defining data transformation and cleaning rules, please note the following:
- Ensure that transformation rules like normalization and aggregation are clearly defined and aligned with the data's intended use.
- Prioritize data integrity during cleaning, ensuring that missing values, outliers, and anomalies are handled appropriately.
- Consider the impact of each transformation and cleaning step on the dataset’s usability for downstream tasks.
- Document each transformation and cleaning rule thoroughly, including justifications for the chosen methods.
- Ensure that these rules are applicable and consistently enforced across both training and testing datasets.
- Always make a copy of the original data before applying transformations or cleaning operations.
"""

DEFINE_FEATURE_ENGINEERING_RULES_PROMPTS = """
The current task is about defining feature engineering rules, please note the following:
- Identify key features that can enhance model performance and define rules for their creation.
- Ensure that feature engineering rules are well-documented, including the rationale behind each feature's inclusion.
- Avoid features that could lead to data leakage or introduce bias into the model.
- Consider the scalability of features across different datasets, ensuring consistency between training and testing datasets.
- Always create a copy of the dataset before applying feature engineering operations to maintain data integrity.
- Continuously review and refine the feature engineering rules based on iterative feedback from model performance.
"""

# B2
CONNECT_TO_RAW_DATA_PROMPTS = """
The current task is about connecting to raw data sources, please note the following:
- Verify that all data sources (streaming, batch, or cloud storage) are accessible and correctly configured.
- Ensure secure and reliable connections to prevent data loss or corruption during extraction.
- Document the connection details for each data source, including any credentials or access keys used.
- Test the data connection with sample queries or data pulls to confirm data is being accessed as expected.
- Consider setting up monitoring or alert systems to track the connection status of each data source.
"""

DATA_EXTRACTION_PROMPTS = """
The current task is about data extraction, please note the following:
- Identify the specific data required from each source and outline the extraction logic clearly.
- Ensure that the data extraction process is efficient and minimizes system load or network latency.
- Consider implementing data validation checks during extraction to ensure data quality.
- Document the extraction process, including any scripts or tools used, to enable reproducibility.
- Test the extraction process thoroughly on a small scale before scaling it to full datasets.
"""

DATA_TRANSFORMATION_AND_CLEANING_PROMPTS = """
The current task is about data transformation and cleaning, please note the following:
- Follow the predefined transformation rules for tasks such as normalization, data type conversion, and handling missing values.
- Ensure that data cleaning processes do not inadvertently remove or distort critical data points.
- Regularly review and refine cleaning rules based on the quality of the data and feedback from downstream processes.
- Document each transformation and cleaning step, including any justifications for the methods chosen.
- Apply transformation and cleaning operations consistently across both training and testing datasets.
"""

FEATURE_ENGINEERING_PROMPTS = """
The current task is about feature engineering, please note the following:
- Generate new features that are likely to improve model performance, considering both domain knowledge and data patterns.
- Apply feature selection techniques to identify the most relevant features while avoiding overfitting.
- Ensure that feature engineering is performed consistently across training and testing datasets to avoid data leakage.
- Document the feature engineering process, including the methods and tools used.
- Continuously iterate on feature engineering rules based on feedback from model performance.
"""

DATA_INGESTION_JOB_PROMPTS = """
The current task is about data ingestion, please note the following:
- Ensure that the ingestion pipeline is capable of handling both batch and streaming data as required.
- Implement data validation checks during ingestion to catch any discrepancies or errors.
- Ensure that data is ingested into the correct environment and is ready for subsequent processing stages.
- Document the data ingestion process, including any automation or orchestration components used.
- Test the ingestion pipeline thoroughly to ensure it can handle the expected data load and volume.
"""

FEEDBACK_LOOP_AND_RULE_UPDATES_PROMPTS = """
The current task is about feedback loops and rule updates, please note the following:
- Regularly collect feedback from model performance metrics and monitoring systems to inform rule updates.
- Analyze the feedback to identify patterns or issues that may require changes in data transformation, cleaning, or feature engineering rules.
- Implement a systematic approach for updating rules and configurations, ensuring that changes are documented and communicated across the team.
- Test any rule updates in a controlled environment before applying them to the full pipeline.
- Ensure that the feedback loop is robust and capable of providing timely insights to prevent degradation in model performance.
"""

# C Experimentation
DATA_ANALYSIS_PROMPTS = """
The current task is about data analysis, please note the following:
- Connect to the feature store system or raw data for an initial exploratory data analysis (EDA).
- Identify and understand the data types, distributions, and relationships between variables.
- Report any data quality issues or necessary adjustments to the data engineering team for remediation.
- Document findings from the data analysis phase, which will guide subsequent modeling and feature engineering efforts.
- Use visualizations and statistical summaries to communicate key insights from the data.
"""

DATA_PREPARATION_AND_VALIDATION_PROMPTS = """
The current task is about data preparation and validation, please note the following:
- Prepare the data from the feature store system, ensuring it is properly formatted for model training.
- Create train and test splits, ensuring that they are representative and prevent data leakage.
- Validate the data to ensure it meets the quality standards required for reliable model training.
- Document the data preparation steps, including any transformations applied, to ensure reproducibility.
- Test the prepared data to ensure it aligns with the requirements of the subsequent modeling steps.
"""

MODEL_TRAINING_PROMPTS = """
The current task is about model training, please note the following:
- Select the best-performing algorithm and set the appropriate hyperparameters based on prior experimentation.
- Collaborate with the software engineer to write efficient and scalable model training code.
- Ensure the training process is reproducible and well-documented, including any changes to hyperparameters or algorithms.
- Monitor the training process for signs of overfitting or underfitting, adjusting the approach as necessary.
- Use cross-validation or other robust validation techniques to ensure the model's generalizability.
"""

MODEL_VALIDATION_PROMPTS = """
The current task is about model validation, please note the following:
- Test the model with different sets of parameters and validate its performance on holdout datasets.
- Use appropriate metrics to evaluate model performance, ensuring that they align with the project's goals.
- Iterate on model training and validation until performance metrics reach a satisfactory level.
- Document the validation process, including the performance metrics achieved and any adjustments made during tuning.
- Prepare the validated model for export if it meets the performance requirements.
"""

EXPORT_MODEL_PROMPTS = """
The current task is about exporting the model, please note the following:
- Ensure the model is finalized and performs well on both training and validation datasets.
- Export the model in a format that is compatible with the deployment environment, including all necessary configurations.
- Commit the trained model and corresponding code to the version control repository, ensuring that all related metadata is included.
- Document the export process, including the version and configuration details of the model.
- Prepare the model for deployment by ensuring it meets all requirements for integration with the production environment.
"""

AUTOMATED_ML_WORKFLOW_PROMPTS = """
The current task is about automating the ML workflow, please note the following:
- Develop and commit the code for the automated ML workflow pipeline, ensuring it integrates smoothly with CI/CD processes.
- Ensure the workflow orchestration component is set up to manage the sequence of tasks in the pipeline.
- Validate that the workflow automates the key processes, such as data extraction, preprocessing, model training, and evaluation.
- Document the automated workflow, including any dependencies and configuration settings.
- Test the automated workflow in a controlled environment to ensure it functions as expected before full deployment.
"""

# D Automated ML workflow pipeline
AUTOMATED_FEATURE_EXTRACTION_PROMPTS = """
The current task is about automated feature extraction, please note the following:
- Automate the retrieval of versioned features from the designated data stores, whether offline or online databases.
- Ensure that the correct version of features is pulled and that the process is reliable and repeatable.
- Validate the extracted features to ensure they meet the requirements for subsequent model training.
- Document the feature extraction process, including any configurations or parameters used.
- Test the automated feature extraction to ensure it functions correctly across different datasets.
"""

AUTOMATED_DATA_PREPARATION_AND_VALIDATION_PROMPTS = """
The current task is about automated data preparation and validation, please note the following:
- Automate the preparation and validation of data, including the creation of train and test splits.
- Ensure that the data preparation process is consistent with the manual processes used during experimentation.
- Validate that the automated process maintains data integrity and meets quality standards.
- Document the automated preparation and validation steps, including any rules or scripts used.
- Test the automation on sample datasets to ensure it functions as expected in a live environment.
"""

AUTOMATED_MODEL_TRAINING_PROMPTS = """
The current task is about automated model training, please note the following:
- Automate the model training process using the predefined algorithm and hyperparameters from the experimentation stage.
- Ensure that the automation handles unseen data effectively, retraining and refining the model as needed.
- Monitor the automated training for any issues, such as overfitting or data drift, and adjust the process accordingly.
- Document the automated training process, including any configurations or scripts used.
- Test the automated model training pipeline to ensure it delivers consistent and accurate results.
"""

AUTOMATED_MODEL_VALIDATION_PROMPTS = """
The current task is about automated model validation, please note the following:
- Automate the model evaluation process, iterating on hyperparameter adjustments as necessary to improve performance.
- Ensure that the automated validation is consistent with the manual processes used during experimentation.
- Monitor the validation results and refine the model until performance metrics meet the required thresholds.
- Document the automated validation process, including any configurations or scripts used.
- Test the automated validation on sample models to ensure it functions correctly before full deployment.
"""

EXPORT_AND_REGISTER_MODEL_PROMPTS = """
The current task is about exporting and registering the model, please note the following:
- Ensure that the final model is exported correctly and includes all necessary configuration and environment files.
- Register the model in the model registry, documenting the version, metadata, and associated files.
- Ensure the model is stored in a way that supports easy retrieval and deployment in different environments.
- Document the export and registration process, including any dependencies or configurations required.
- Test the exported model to ensure it can be deployed and used effectively in production.
"""

CI_CD_PIPELINE_TRIGGER_PROMPTS = """
The current task is about triggering the CI/CD pipeline, please note the following:
- Ensure the CI/CD pipeline is configured to automatically trigger upon model status changes or code updates.
- Validate that the pipeline correctly handles the build, test, and deployment steps for the ML model and related code.
- Monitor the CI/CD process to ensure it completes successfully without errors or issues.
- Document the CI/CD pipeline configuration and any custom steps or scripts used in the process.
- Test the pipeline with a staging environment to ensure it functions correctly before deploying to production.
"""

MODEL_SERVING_PROMPTS = """
The current task is about model serving, please note the following:
- Configure the model serving environment to handle prediction requests via REST API, supporting both online and batch inference.
- Ensure that the serving environment is optimized for the expected workload, whether real-time or batch processing.
- Monitor the model serving process to ensure predictions are accurate and delivered within acceptable timeframes.
- Document the model serving configuration, including the setup of any containers or infrastructure components.
- Test the model serving setup with sample prediction requests to ensure it functions correctly before going live.
"""

MONITORING_AND_FEEDBACK_PROMPTS = """
The current task is about monitoring and feedback, please note the following:
- Continuously monitor the model-serving performance and underlying infrastructure in real-time.
- Set up alerts and feedback mechanisms to trigger retraining or adjustments when performance thresholds are breached.
- Document the monitoring setup, including metrics tracked and alert thresholds.
- Ensure that the feedback loop is robust and provides timely insights for continuous model improvement.
- Test the monitoring system to ensure it functions correctly and that feedback is correctly routed to the appropriate teams.
"""

CONTINUOUS_TRAINING_PROMPTS = """
The current task is about continuous training, please note the following:
- Automate the retraining process based on triggers from the monitoring component, such as detection of concept drift.
- Ensure that retraining is conducted using the latest data and adheres to the same standards as initial model training.
- Document the continuous training process, including any configurations or dependencies.
- Test the continuous training pipeline to ensure it functions correctly and maintains model accuracy over time.
- Set up periodic reviews of the retrained model to ensure it continues to meet performance expectations.
"""

