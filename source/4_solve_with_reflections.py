

# Key Points 


'''•	Model and Agent Loop: The code iterates through each combination of model, agent, and exam to run experiments on each problem.
	•	Reflection Logic: If the agent type requires reflections (e.g., advice, explanation), the corresponding reflection file is loaded. If the agent is of type “retry”, no reflection is loaded.
	•	Exam Loading: For each exam, problems are processed sequentially, and agents attempt to solve the problems with either a retry or reflection-based approach.
	•	Logging: Logs are created for each problem, and each step (agent interaction, answers, etc.) is logged to file.
	•	Result Tracking: The experiment results are tracked, saved, and then compiled at the end of each experiment run.'''





# Import required packages
import os
from datetime import datetime
import pandas as pd
from models.model_factory import ModelFactory  # Creates model instances
from agents.agent_factory import AgentFactory  # Creates agent instances
from problems.exam_reader import ExamReader  # Reads exam problem data from files
from details.details_reader import DetailsReader  # Reads the details (answers/results) of previous experiments
from reflections.reflections_reader import ReflectionReader  # Reads reflection information for agents
from experiments.experiment import Experiment  # Handles experiment creation and tracking
from experiments.result import Result  # Manages experiment result computation
from experiments.experiments_file import ExperimentsFile  # Handles result file management
from details.details_writer import DetailsWriter  # Writes detailed experiment information
from details.details_row import DetailsRow  # Manages individual rows of detailed experiment data
from dialogs.dialog_writer import DialogWriter  # Writes out the dialog between user and agent
from models.pricing import get_pricing  # Retrieves pricing information for the model used
from logs.log import Log  # Handles logging functionality
from logs.log_level import LogLevel  # Defines levels for logging (DEBUG, INFO, etc.)

# Set the models to be used in the experiment
model_names = [
    "gpt-35-turbo",
    "gpt-4",
    "llama-2-7b-chat",
    "llama-2-70b-chat",
    "mistral-large",
    "cohere-command-r-plus",
    "gemini-1.0-pro",
    "gemini-1.5-pro-preview-0409",
    "claude-3-opus-20240229"
]  # A list of models to evaluate

# Set the baseline agents (used for initial comparison)
baseline_agent_names = [
    "baseline"
]  # The "baseline" agent type for comparison

# Set the agents for reflection and retry tasks
agent_names = [
    "retry",           # Retry agent if the problem was answered incorrectly
    "advice",          # Agent providing advice
    "instructions",    # Agent providing instructions
    "keywords",        # Agent providing keywords
    "explanation",     # Agent providing explanations
    "solution",        # Agent providing solutions
    "composite",       # Agent handling composite reflections
    "unredacted"       # Agent without any redactions
]  # Types of agents to evaluate in addition to the baseline

# Set the exams to be used in the experiment
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
]  # A list of exams that will be used for testing the agents

# Set the attempt ID for tracking the experiment
attempt_id = 2

# Set the logging level to DEBUG for detailed logging
log_level = LogLevel.DEBUG

# Create instances of the necessary components
model_factory = ModelFactory()  # Creates models
agent_factory = AgentFactory()  # Creates agents
exam_reader = ExamReader()  # Reads exam problem data
details_reader = DetailsReader()  # Reads past exam results
reflection_reader = ReflectionReader()  # Reads reflection data for agents
dialog_writer = DialogWriter()  # Writes dialog data

# Loop through each model in the model_names list
for model_name in model_names:

    # Loop through each agent in the agent_names list
    for agent_name in agent_names:

        # Loop through each exam in the exam_names list
        for exam_name in exam_names:

            # Set the experiment parameters
            start_time = pd.Timestamp.now()  # Capture the start time of the experiment
            experiment = Experiment(model_name, agent_name, exam_name, attempt_id)  # Create a new experiment instance
            experiment.start(start_time)  # Start the experiment

            # Set file and folder paths
            exam_path = f"../data/exams/{exam_name}.jsonl"  # Path to the exam file
            previous_details_file_path = f"../data/details/{model_name} - baseline - {exam_name}.csv"  # Path to the baseline experiment results
            reflections_folder_path = f"../data/reflections/{model_name} - {agent_name} - {exam_name}"  # Folder for reflection files
            dialogs_folder_path = f"../data/dialogs/{experiment.name}"  # Folder to save the new dialog files
            details_file_path = f"../data/details/{experiment.name}.csv"  # File to store experiment details
            results_file_path = f"../data/results/results.csv"  # Path for storing experiment results
            log_name_prefix = start_time.strftime("%Y-%m-%d %H-%M-%S")  # Prefix for log file names
            log_folder_path = f"../data/logs/{log_name_prefix} - {experiment.name}"  # Folder for logging

            # Create the necessary folders if they don't exist
            os.makedirs(dialogs_folder_path, exist_ok=True)
            os.makedirs(os.path.dirname(details_file_path), exist_ok=True)
            os.makedirs(os.path.dirname(results_file_path), exist_ok=True)
            os.makedirs(log_folder_path, exist_ok=True)

            # Create an empty list to store details of the experiment
            details = []

            # Load the exam data from the file
            exam = exam_reader.read(exam_path)

            # Loop through each problem in the exam
            for i, problem in enumerate(exam.problems):
                problem_id = i + 1  # Assign a problem ID

                # Optional: Limit to processing a specific number of problems (commented for full processing)
                # if i >= 10:
                #      break

                # Create the log file for the current problem
                log_file_path = f"{log_folder_path}/Problem {problem_id}.txt"  # Log file path for the current problem
                log = Log(log_level)  # Create log instance
                log.open(log_file_path)  # Open log file
                log.head(f"Model: {experiment.model_name} | Agent: {experiment.agent_name} | Exam: {experiment.exam_name} | Problem {i + 1} of {len(exam.problems)}")  # Log experiment details

                # Skip the problem if it was already answered correctly in the baseline experiment
                if details_reader.is_correct(previous_details_file_path, problem_id):
                    log.info(f"Skipping problem {problem_id} because it was already answered correctly.")  # Log skipped problem
                    log.close()  # Close log
                    continue  # Skip to the next problem

                # Load the reflection for the current problem (if agent is not "retry")
                if agent_name == "retry":
                    reflection = "No reflection information provided."  # Default reflection for retry agent
                else:
                    reflection_file_path = f"{reflections_folder_path}/Problem {problem_id}.txt"  # Path to reflection file
                    reflection = reflection_reader.read(reflection_file_path)  # Read the reflection file

                # Create a details row for tracking this problem
                details_row = DetailsRow()
                episode_start_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')  # Capture episode start time
                details_row.create(problem_id, episode_start_time, experiment, problem)  # Create the row

                # Create the agent for the current problem
                model = model_factory.create(experiment.model_name)  # Create the model instance
                agent = agent_factory.create(experiment.agent_name, model, problem.topic)  # Create the agent instance

                # Generate the initial dialog for this problem
                log.subhead("System:")
                agent.create_dialog()  # Initialize dialog
                log.info(agent.dialog.get_all()[0].content)  # Log system message
                log.subhead("User 1:")
                log.info(agent.dialog.get_all()[1].content)  # Log user message
                log.subhead("Assistant 1:")
                log.info(agent.dialog.get_all()[2].content)  # Log assistant message

                # Set the problem and reflection information in the agent
                log.subhead("User 2:")
                agent.set_problem(problem)  # Set the current problem
                agent.set_reflection(reflection)  # Set the reflection for the agent
                log.info(agent.dialog.get_all()[3].content)  # Log updated user message

                # Get the agent's answer for the problem
                log.subhead("Assistant 2:")
                answer_response = agent.get_answer()  # Agent generates an answer
                answer = agent.get_answer_choice(answer_response.text)  # Get the answer choice from the response
                log.info(agent.dialog.get_all()[4].content)  # Log the assistant's answer

                # Log the result (whether the agent's answer was correct)
                log.subhead("Result:")
                is_correct = answer == problem.answer  # Check if the agent's answer is correct
                score = 1 if is_correct else 0  # Assign score based on correctness
                details_row.update_answer(answer_response, answer, score)  # Update the details row with the result
                log.info(f"Agent Answer: {answer}")
                log.info(f"Correct Answer: {problem.answer}")
                log.info(f"Score: {score}")

                # Save the dialog to a file
                dialog_file_path = f"{dialogs_folder_path}/Problem {problem_id}.json"  # Path to save the dialog
                dialog_writer.write(dialog_file_path, agent.dialog)  # Write the dialog to file
                details.append(details_row)  # Append the details row to the list

            # End the experiment and log the end time
            experiment.end(datetime.now())
            details_table = pd.DataFrame(details)  # Convert the details list to a DataFrame
            pricing = get_pricing(model_name)  # Get pricing information for the model used
            results = Result(experiment, details_table, pricing)  # Create the result object

            # Record the experiment details in a CSV file
            details_writer = DetailsWriter()
            details_writer.write(details, details_file_path)  # Write the details to file

            # Record the experiment results
            experiments = ExperimentsFile()
            experiments.load(results_file_path)  # Load the results file
            experiments.add_row(experiment, results)  # Add the current experiment's results
            experiments.save(results_file_path)  # Save the updated results

            # Log the final results of the experiment
            log_file_path = f"{log_folder_path}/Results.txt"  # Path to save the results log
            log = Log(LogLevel.INFO)  # Create log instance for final results
            log.open(log_file_path)  # Open log file
            log.head("Results")  # Add heading for results
            log.object(results)  # Log the results object
            log.close()  # Close the log file