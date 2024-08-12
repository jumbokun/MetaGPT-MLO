"""
Filename: MetaGPT/examples/build_customized_multi_agents.py
Created Date: Wednesday, November 15th 2023, 7:12:39 pm
Author: garylin2099
"""
import re

import fire

from metagpt.actions import Action, UserRequirement
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.team import Team
from metagpt.roles.stakeholder import Stakeholder
from metagpt.roles.solution_architect import SolutionArchtect
from metagpt.roles.data_engineer import DataEngineer
from metagpt.roles.data_scientist import DataScientist
from metagpt.roles.software_engineer import SoftwareEngineer
from metagpt.roles.ML_engineer import MLEngineer
from metagpt.roles.DevOps_engineer import DevOpsEngineer
async def main(
    idea: str = 
    """
# Overall
We are engaging in a competition named RSNA 2024 Lumbar Spine Degenerative Classification, we are suppose to write some code in notebook and execute it till we have the final result: submission.csv. 

# Data
Dataset Description
The goal of this competition is to identify medical conditions affecting the lumbar spine in MRI scans.

This competition uses a hidden test. When your submitted notebook is scored, the actual test data (including a full length sample submission) will be made available to your notebook.

Files
train.csv Labels for the train set.

study_id - The study ID. Each study may include multiple series of images.
[condition]_[level] - The target labels, such as spinal_canal_stenosis_l1_l2, with the severity levels of Normal/Mild, Moderate, or Severe. Some entries have incomplete labels.
train_label_coordinates.csv

study_id
series_id - The imagery series ID.
instance_number - The image's order number within the 3D stack.
condition - There are three core conditions: spinal canal stenosis, neural_foraminal_narrowing, and subarticular_stenosis. The latter two are considered for each side of the spine.
level - The relevant vertebrae, such as l3_l4
[x/y] - The x/y coordinates for the center of the area that defined the label.
sample_submission.csv

row_id - A slug of the study ID, condition, and level such as 12345_spinal_canal_stenosis_l3_l4.
[normal_mild/moderate/severe] - The three prediction columns.
[train/test]_images/[study_id]/[series_id]/[instance_number].dcm The imagery data.

[train/test]_series_descriptions.csv

study_id
series_id
series_description The scan's orientation.

# Description
Low back pain is the leading cause of disability worldwide, according to the World Health Organization, affecting 619 million people in 2020. Most people experience low back pain at some point in their lives, with the frequency increasing with age. Pain and restricted mobility are often symptoms of spondylosis, a set of degenerative spine conditions including degeneration of intervertebral discs and subsequent narrowing of the spinal canal (spinal stenosis), subarticular recesses, or neural foramen with associated compression or irritations of the nerves in the low back.

Magnetic resonance imaging (MRI) provides a detailed view of the lumbar spine vertebra, discs and nerves, enabling radiologists to assess the presence and severity of these conditions. Proper diagnosis and grading of these conditions help guide treatment and potential surgery to help alleviate back pain and improve overall health and quality of life for patients.

RSNA has teamed with the American Society of Neuroradiology (ASNR) to conduct this competition exploring whether artificial intelligence can be used to aid in the detection and classification of degenerative spine conditions using lumbar spine MR images.

The challenge will focus on the classification of five lumbar spine degenerative conditions: Left Neural Foraminal Narrowing, Right Neural Foraminal Narrowing, Left Subarticular Stenosis, Right Subarticular Stenosis, and Spinal Canal Stenosis. For each imaging study in the dataset, we’ve provided severity scores (Normal/Mild, Moderate, or Severe) for each of the five conditions across the intervertebral disc levels L1/L2, L2/L3, L3/L4, L4/L5, and L5/S1.

To create the ground truth dataset, the RSNA challenge planning task force collected imaging data sourced from eight sites on five continents. This multi-institutional, expertly curated dataset promises to improve standardized classification of degenerative lumbar spine conditions and enable development of tools to automate accurate and rapid disease classification.

Challenge winners will be recognized at an event during the RSNA 2024 annual meeting. For more information on the challenge, contact RSNA Informatics staff at informatics@rsna.org.

# Evaluation
Submissions are evaluated using the average of sample weighted log losses and an any_severe_spinal prediction generated by the metric. The metric notebook can be found here.

The sample weights are as follows:

1 for normal/mild.
2 for moderate.
4 for severe.
For each row ID in the test set, you must predict a probability for each of the different severity levels. The file should contain a header and have the following format:

row_id,normal_mild,moderate,severe
123456_left_neural_foraminal_narrowing_l1_l2,0.333,0.333,0.333
123456_left_neural_foraminal_narrowing_l2_l3,0.333,0.333,0.333
123456_left_neural_foraminal_narrowing_l3_l4,0.333,0.333,0.333
etc.
In rare cases the lowest vertebrae aren't visible in the imagery. You still need to make predictions (nulls will cause errors), but those rows will not be scored.

For this competition, the any_severe_scalar has been set to 1.0.

# Settings
The 
""",
    investment: float = 3.0,
    n_round: int = 5,
    add_human: bool = False,
):
    logger.info(idea)

    team = Team()
    team.hire(
        [
            Stakeholder(),
            SolutionArchtect(),
            DevOpsEngineer(),
            DataEngineer(),
            DataScientist(),
            SoftwareEngineer(),
            MLEngineer(),
        ]
    )

    team.invest(investment=investment)
    team.run_project(idea)
    await team.run(n_round=n_round)


if __name__ == "__main__":
    fire.Fire(main)