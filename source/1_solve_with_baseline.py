# Key Points : 


'''	•	The code sets up experiments involving a model (like GPT-4) and an agent to solve exam problems and log the results.
	•	It tracks the experiment’s start and end times and logs the dialog between the user and the agent.
	•	The code creates various files for logging, saving dialogs, experiment details, and final results.
	•	It processes only the first 10 problems per exam for debugging purposes (this can be changed by removing or modifying the condition).
	•	The process is repeated for each combination of model and exam, and the results are recorded for further analysis.'''






# Import required packages
import os
from datetime import datetime
import pandas as pd
from models.model_factory import ModelFactory  # Creates models based on the name provided
from agents.agent_factory import AgentFactory  # Creates agents that interact with models and problems
from problems.exam_reader import ExamReader    # Reads exam data from files
from experiments.experiment import Experiment  # Handles experiment creation and tracking
from experiments.result import Result  # Handles experiment results
from experiments.experiments_file import ExperimentsFile  # Manages experiment result file
from details.details_writer import DetailsWriter  # Writes details of the experiment
from details.details_row import DetailsRow  # Manages the individual rows for experiment details
from dialogs.dialog_writer import DialogWriter  # Writes dialogs (interaction between agent and system)
from models.pricing import get_pricing  # Retrieves pricing details based on model used
from logs.log import Log  # Handles logging
from logs.log_level import LogLevel  # Defines the levels for logging (INFO, DEBUG, etc.)

# Set the models to be used in the experiment
model_names = ["gpt-4"]  # You are using the GPT-4 model for this experiment

# Set the agent to be used
agent_name = "baseline"  # The baseline agent that interacts with the models

# Set the exam names to be used
exam_names = [
    "comprehensive-100",
    "aqua-rat-100",
    "logiqa-en-100",
    "lsat-ar-100",
    "lsat-lr-100",
    "lsat-rc-100",
    "sat-en-100",
    "sat-math-100",
    "arc-challenge-100",
    "hella-swag-100",
    "med-mcqa-100"
]

# Set an ID for the experiment attempt
attempt_id = 1

# Set the logging level to DEBUG for detailed output
log_level = LogLevel.DEBUG

# Create instances for factories and components
model_factory = ModelFactory()  # Responsible for creating models
agent_factory = AgentFactory()  # Responsible for creating agents
exam_reader = ExamReader()  # Responsible for reading exam problems
dialog_writer = DialogWriter()  # Responsible for writing out dialog during the experiment

# Loop through each model in the model_names list
for model_name in model_names:

    # Loop through each exam in the exam_names list
    for exam_name in exam_names:

        # Set the experiment parameters
        start_time = pd.Timestamp.now()  # Capture the start time of the experiment
        experiment = Experiment(model_name, agent_name, exam_name, attempt_id)  # Create the experiment instance
        experiment.start(start_time)  # Start the experiment and log the start time

        # Define file and folder paths for saving data and results
        exam_path = f"./data/exams/{exam_name}.jsonl"  # Path to the exam file
        dialogs_folder_path = f"./data/dialogs/{experiment.name}"  # Folder for saving dialogs
        details_file_path = f"./data/details/{experiment.name}.csv"  # Path to save experiment details
        results_file_path = f"./data/results/results.csv"  # Path for saving overall experiment results
        log_name_prefix = start_time.strftime("%Y-%m-%d %H-%M-%S")  # Prefix for log file names
        log_folder_path = f"./data/logs/{log_name_prefix} - {experiment.name}"  # Folder for logs

        # Create necessary directories for saving data
        os.makedirs(dialogs_folder_path, exist_ok=True)
        os.makedirs(os.path.dirname(details_file_path), exist_ok=True)
        os.makedirs(os.path.dirname(results_file_path), exist_ok=True)
        os.makedirs(log_folder_path, exist_ok=True)

        # Initialize a list to store experiment details
        details = []

        # Read the exam problems from the exam file
        exam = exam_reader.read(exam_path)

        # Loop through each problem in the exam
        for i, problem in enumerate(exam.problems):
            problem_id = i + 1  # Assign a problem ID

            # Debugging purpose: Answer only the first 10 problems, break after 10
            if i >= 10:
                 break

            # Create the log file for the current problem
            log_file_path = f"{log_folder_path}/Problem {problem_id}.txt"
            log = Log(log_level)  # Create log instance
            log.open(log_file_path)  # Open the log file
            log.head(f"Model: {experiment.model_name} | Agent: {experiment.agent_name} | Exam: {experiment.exam_name} | Problem {i + 1} of {len(exam.problems)}")  # Log the problem header

            # Create a new row for this problem's details
            details_row = DetailsRow()
            episode_start_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')  # Capture episode start time
            details_row.create(problem_id, episode_start_time, experiment, problem)  # Create a row entry for this problem

            # Create the agent and model for solving the problem
            model = model_factory.create(experiment.model_name)  # Create the model instance
            agent = agent_factory.create(experiment.agent_name, model, problem.topic)  # Create the agent instance

            # Generate the dialog (interaction between agent and system)
            log.subhead("System:")
            agent.create_dialog()  # Create the initial dialog
            log.info(agent.dialog.get_all()[0].content)  # Log the initial system content
            log.subhead("User 1:")
            log.info(agent.dialog.get_all()[1].content)  # Log user interaction
            log.subhead("Assistant 1:")
            log.info(agent.dialog.get_all()[2].content)  # Log assistant interaction

            # Present the problem to the agent
            log.subhead("User 2:")
            agent.set_problem(problem)  # Set the exam problem to the agent
            log.info(agent.dialog.get_all()[3].content)  # Log the problem presented

            # Get the agent's answer
            log.subhead("Assistant 2:")
            answer_response = agent.get_answer()  # Get agent's response to the problem
            answer = agent.get_answer_choice(answer_response.text)  # Extract the final answer
            log.info(agent.dialog.get_all()[4].content)  # Log the answer

            # Log whether the answer was correct
            log.subhead("Result:")
            is_correct = answer == problem.answer  # Check if the agent's answer is correct
            score = 1 if is_correct else 0  # Assign score based on correctness
            details_row.update_answer(answer_response, answer, score)  # Update the details row with answer information
            log.info(f"Agent Answer: {answer}")
            log.info(f"Correct Answer: {problem.answer}")
            log.info(f"Score: {score}")

            # Save the dialog to a file
            dialog_file_path = f"{dialogs_folder_path}/Problem {problem_id}.json"
            dialog_writer.write(dialog_file_path, agent.dialog)  # Write the dialog to file
            details.append(details_row)  # Append the details row to the list

        # End the experiment and log the end time
        experiment.end(datetime.now())
        details_table = pd.DataFrame(details)  # Convert the details list to a DataFrame
        pricing = get_pricing(experiment.model_name)  # Retrieve pricing for the model
        results = Result(experiment, details_table, pricing)  # Create the experiment result

        # Write experiment details to a CSV file
        details_writer = DetailsWriter()
        details_writer.write(details, details_file_path)  # Write details to file

        # Record the overall experiment results
        experiments = ExperimentsFile()
        experiments.load(results_file_path)  # Load existing results file
        experiments.add_row(experiment, results)  # Add current experiment results
        experiments.save(results_file_path)  # Save the updated results

        # Log the final results to a log file
        log_file_path = f"{log_folder_path}/Results.txt"
        log = Log(LogLevel.INFO)
        log.open(log_file_path)  # Open the results log file
        log.head("Results")  # Add header
        log.object(results)  # Log the result object
        log.close()  # Close the log file