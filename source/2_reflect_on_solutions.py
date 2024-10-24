# Key Points : 





'''	•	The code performs a reflection-based experiment where the agent revisits problems that were not answered correctly in a previous experiment and attempts to correct them.
	•	It tracks the progress of different models (like GPT-4, Claude-3, etc.) on a variety of exams and logs the reflection process.
	•	The experiment checks if problems were already answered correctly and skips them, focusing only on problems that were incorrect.
	•	New dialogs and logs are created for the reflection process and saved for future analysis.
'''





# Import required packages
import os
import pandas as pd
import openai
from models.model_factory import ModelFactory  # Responsible for creating models based on the model name
from agents.agent_factory import AgentFactory  # Responsible for creating agents that interact with models and problems
from problems.exam_reader import ExamReader    # Reads exam data from files
from details.details_reader import DetailsReader  # Reads details such as previous answers from CSV
from dialogs.dialog_reader import DialogReader  # Reads dialog files from previous experiments
from dialogs.dialog_writer import DialogWriter  # Writes dialog (interaction between agent and system) to files
from logs.log import Log  # Handles logging for the experiment
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
]  # A list of various models to compare performance

# Set the agent name to be used in this run
agent_name = "reflection"  # This is the "reflection" agent that reviews previously given answers

# Set the exam names to be used in this run
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
]  # List of exam datasets the models will be tested on

# Set an attempt ID for tracking
attempt_id = 1

# Set the logging level to DEBUG for detailed logging
log_level = LogLevel.DEBUG

# Create instances of necessary components
model_factory = ModelFactory()  # Creates the models specified in the list
agent_factory = AgentFactory()  # Creates the agents based on agent_name
exam_reader = ExamReader()  # Reads exam data from JSONL files
details_reader = DetailsReader()  # Reads exam result details from CSV files
dialog_reader = DialogReader()  # Reads dialogs from previous runs
dialog_writer = DialogWriter()  # Writes the dialog files during reflection

# Loop through each model in the model_names list
for model_name in model_names:

    # Loop through each exam in the exam_names list
    for exam_name in exam_names:

        # Set file and folder paths
        start_time = pd.Timestamp.now()  # Capture the start time of the reflection experiment
        previous_experiment_name = f"{model_name} - baseline - {exam_name}"  # Name of the previous experiment (baseline agent)
        current_reflection_name = f"{model_name} - {agent_name} - {exam_name}"  # Name for the reflection experiment (reflection agent)
        exam_file_path = f"../data/exams/{exam_name}.jsonl"  # Path to the exam file
        details_file_path = f"../data/details/{previous_experiment_name}.csv"  # Path to the results from the previous experiment
        problem_dialogs_folder_path = f"../data/dialogs/{previous_experiment_name}"  # Folder with dialogs from the previous run
        reflection_dialogs_folder_path = f"../data/dialogs/{current_reflection_name}"  # Folder to save new reflection dialogs
        log_name_prefix = start_time.strftime("%Y-%m-%d %H-%M-%S")  # Prefix for log file names
        log_folder_path = f"../data/logs/{log_name_prefix} - {current_reflection_name}"  # Folder for reflection logs

        # Create necessary directories for saving reflection results
        os.makedirs(reflection_dialogs_folder_path, exist_ok=True)
        os.makedirs(log_folder_path, exist_ok=True)

        # Load the exam problems from the exam file
        exam = exam_reader.read(exam_file_path)

        # Loop through each problem in the exam
        for i, problem in enumerate(exam.problems):
            problem_id = i + 1  # Assign a problem ID

            # Optional: Answer only the first n problems (commented out here for full processing)
            # if i >= 10:
            #      break

            # Create the log file for the current problem
            log_file_path = f"{log_folder_path}/Problem {problem_id}.txt"
            log = Log(log_level)  # Initialize the log instance
            log.open(log_file_path)  # Open the log file for the current problem
            log.head(f"Model: {model_name} | Agent: {agent_name} | Exam: {exam_name} | Problem {problem_id} of {len(exam.problems)}")  # Log problem header

            # Skip the problem if it was already answered correctly in the previous experiment
            if details_reader.is_correct(details_file_path, problem_id):
                log.info(f"Skipping problem {problem_id} because it was already answered correctly.")
                log.close()  # Close log if the problem is skipped
                continue

            # Create the agent for reflection
            model = model_factory.create(model_name)  # Create the model instance
            reflect_agent = agent_factory.create(agent_name, model, problem.topic)  # Create the reflection agent instance

            # Create the new dialog (interaction for reflection)
            reflect_agent.create_dialog()  # Initialize the dialog for this problem
            log.subhead("System:")  # Log system interaction
            log.info(reflect_agent.dialog.get_all()[0].content)  # Log system response
            log.subhead("User 1:")  # Log user interaction
            log.info(reflect_agent.dialog.get_all()[1].content)  # Log user input
            log.subhead("Assistant 1:")  # Log assistant interaction
            log.info(reflect_agent.dialog.get_all()[2].content)  # Log assistant response

            # Load the previous dialog for this problem
            reflection_dialog_file_path = f"{problem_dialogs_folder_path}/Problem {problem_id}.json"
            dialog = dialog_reader.read(reflection_dialog_file_path)  # Load previous dialog from the baseline agent

            # Create the user prompt for reflection based on the problem and solution
            log.subhead("User 2:")  # Log second user interaction (reflection)
            problem_text = str(problem)  # Get the problem text
            solution_text = dialog.get_all()[4].content  # Get the solution text from the previous dialog
            correct_answer = problem.answer  # Get the correct answer for the problem
            user_prompt = problem_text + "\n"  # Combine problem and solution into user prompt
            user_prompt += solution_text + "\n"
            user_prompt += "\n --- \n"
            user_prompt += f"Correct Answer: {correct_answer}\n"  # Add correct answer to the prompt
            if not details_reader.has_agent_answer(details_file_path, problem_id):  # Check if the agent provided an answer in the previous run
                user_prompt += "Error: You did not provide your answer in the correct format.\n"  # Add error message for incorrect format
                user_prompt += "Your answer must be stated as 'Action: Answer(\"[ANSWER_CHOICE]\")';\n"  # Add correct format instructions
            log.info(user_prompt)  # Log the user prompt

            # Get the agent's reflection response
            log.subhead("Assistant 2:")  # Log second assistant interaction (reflection)
            reflection_response = reflect_agent.reflect(user_prompt)  # Get agent's reflection on the prompt
            log.info(f"Response:\n{reflection_response.text}")  # Log the reflection response

            # Save the reflection dialog
            reflection_dialog_file_path = f"{reflection_dialogs_folder_path}/Problem {problem_id}.json"
            dialog_writer.write(reflection_dialog_file_path, reflect_agent.dialog)  # Write the reflection dialog to file
            log.close()  # Close the log file for this problem