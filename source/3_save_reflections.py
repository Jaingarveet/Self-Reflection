
# Key Points 


'''	•	The code performs reflection tasks for various models on different exams.
	•	Reflections (e.g., explanation, keywords, advice) are redacted and saved in different formats: section-based, composite, and unredacted.
	•	Logging is used throughout to record the process of generating and saving reflections, skipping problems that were answered correctly, and managing file I/O.
	•	Answer choices are redacted from the reflection to prevent revealing them in the saved files.
	•	The final reflection for each problem is saved in multiple formats (section-wise, composite, unredacted), stored in appropriate folders.'''







import os
from datetime import datetime
from logs.log import Log, LogLevel  # Handles logging and defines log levels
from problems.exam_reader import ExamReader  # Reads exam data
from details.details_reader import DetailsReader  # Reads details of exam results
from dialogs.dialog_reader import DialogReader  # Reads dialog files
from reflections.reflections_writer import ReflectionsWriter  # Writes reflections

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
]  # A list of models for which reflection tasks will be conducted

# Set the exam names and their corresponding topics
exam_names = {
    "comprehensive-100": "General Knowledge",
    "aqua-rat-100": "Math",
    "logiqa-en-100": "Logic",
    "lsat-ar-100": "Law",
    "lsat-lr-100": "Law",
    "lsat-rc-100": "Law",
    "sat-en-100": "English",
    "sat-math-100": "Math",
    "arc-challenge-100": "Science",
    "hella-swag-100": "General Knowledge",
    "med-mcqa-100": "Medicine"
}  # A dictionary mapping exam file names to their topics

# Set the attempt id
attempt_id = 1

# Define section headings for different types of reflections
section_headings = {
    "Explanation:": "explanation",
    "Error Keywords:": "keywords",
    "Solution:": "solution",
    "Instructions:": "instructions",
    "Advice:": "advice"
}  # Sections used to parse and organize the reflection content

# Set the logging level to DEBUG for detailed information
log_level = LogLevel.DEBUG

# Create the components needed for the task
exam_reader = ExamReader()  # Reads exam data from JSONL files
details_reader = DetailsReader()  # Reads past exam answers/results
dialog_reader = DialogReader()  # Reads dialog files from past tasks
reflection_writer = ReflectionsWriter()  # Writes reflection text into files

# Loop through each model in the model_names list
for model_name in model_names:

    # Loop through each exam in the exam_names dictionary
    for exam_name_and_topic in exam_names:

        # Get the exam name and topic
        exam_name = exam_name_and_topic  # The name of the exam file
        topic = exam_names[exam_name_and_topic]  # The topic corresponding to the exam

        # Set file and folder paths
        exam_file_path = f"../data/exams/{exam_name}.jsonl"  # Path to the exam file
        details_file_path = f"../data/details/{model_name} - baseline - {exam_name}.csv"  # Path to the results of the baseline task
        dialogs_folder_path = f"../data/dialogs/{model_name} - reflection - {exam_name}"  # Folder where the dialog for reflection is stored
        reflections_folder_root = f"../data/reflections"  # Root folder where reflection files will be saved
        file_date_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")  # Timestamp for creating unique file/folder names
        log_folder_path = f"../data/logs/{file_date_time} - {model_name} - save_reflections - {exam_name}"  # Folder for saving logs
        os.makedirs(log_folder_path, exist_ok=True)  # Ensure that the log folder exists

        # Load the exam problems from the exam file
        exam = exam_reader.read(exam_file_path)

        # Loop through each problem in the exam
        for i, problem in enumerate(exam.problems):
            problem_id = i + 1  # Assign a problem ID

            # Optional: Limit processing to a certain number of problems for debugging purposes
            # if i >= 10:
            #     break

            # Create the log file for the current problem
            log_file_path = f"{log_folder_path}/Problem {problem_id}.txt"  # Path for the log file for this problem
            log = Log(log_level)  # Initialize a log instance
            log.open(log_file_path)  # Open the log file for writing
            log.head(f"Model: {model_name} | Task: save_reflection | Exam: {exam_name} | Problem {i + 1} of {len(exam.problems)}")  # Log problem details

            # Skip problems that were already answered correctly
            if details_reader.is_correct(details_file_path, problem_id):
                log.info(f"Skipping problem {problem_id} because it was already answered correctly.")  # Log the skip
                log.close()  # Close the log file
                continue

            # Load the dialog associated with the problem
            dialog_file_path = f"{dialogs_folder_path}/Problem {problem_id}.json"  # Path to the dialog file
            dialog = dialog_reader.read(dialog_file_path)  # Load the dialog

            # Extract the reflection content from the dialog
            log.subhead("Get Reflection:")
            unredacted_message = dialog.get_all()[4].content  # Get the original unredacted reflection message
            reflection_message = unredacted_message  # Set the reflection message (initially unredacted)
            log.info(reflection_message)  # Log the reflection message

            # Redact the answer choices from the reflection content
            for choice in problem.choices:  # Loop through each possible answer choice
                choice_text = problem.choices[choice]  # Get the actual text of the answer choice
                reflection_message = reflection_message.replace(choice + " ", "[REDACTED] ")  # Redact choice letters
                reflection_message = reflection_message.replace(choice + "\"", "[REDACTED]\"")  # Redact choice letters followed by quotes
                reflection_message = reflection_message.replace(choice + ".", "[REDACTED].")  # Redact choice letters followed by periods
                reflection_message = reflection_message.replace(choice + ",", "[REDACTED],")  # Redact choice letters followed by commas
                reflection_message = reflection_message.replace(choice + ":", "[REDACTED]:")  # Redact choice letters followed by colons
                reflection_message = reflection_message.replace(choice + ";", "[REDACTED];")  # Redact choice letters followed by semicolons
                reflection_message = reflection_message.replace(choice_text, "[REDACTED]")  # Redact the entire answer text

            # Parse the reflection message into sections (e.g., Explanation, Keywords)
            log.subhead("Parse Reflections:")
            section_contents = {heading: "" for heading in section_headings}  # Initialize sections
            current_section = None  # Track which section we're currently filling
            lines = reflection_message.split("\n")  # Split the reflection message into lines
            for line in lines:
                trimmed_line = line.strip()  # Trim whitespace
                if trimmed_line in section_headings:
                    current_section = trimmed_line  # Update current section based on the heading
                elif current_section:
                    section_contents[current_section] += line + "\n"  # Append line to the current section

            # Save each section of the reflection
            log.subhead("Save Reflections:")
            for section in section_contents:
                reflection_name = section_headings[section]  # Get the reflection type (e.g., explanation, keywords)
                reflection_file_name = f"Problem {problem_id}.txt"  # Filename for the reflection
                reflections_folder_name = f"{model_name} - {reflection_name} - {exam_name}"  # Folder for saving this reflection
                reflections_folder_path = f"{reflections_folder_root}/{reflections_folder_name}"  # Path to the reflection folder
                os.makedirs(reflections_folder_path, exist_ok=True)  # Ensure the reflection folder exists
                log.info(f"Saving {reflection_name} reflection")  # Log the saving process
                content = section_contents[section]  # Get the reflection content for this section
                reflection_writer.write(reflection_file_path, section, content)  # Write the section to a file

            # Save the composite reflection (combining all sections)
            log.info("Saving composite reflection")
            composite_reflection = ""
            for section in section_contents:
                composite_reflection += f"{section}\n{section_contents[section]}"  # Combine all sections into one text
            reflection_file_name = f"Problem {problem_id}.txt"  # Filename for the composite reflection
            reflections_folder_name = f"{model_name} - composite - {exam_name}"  # Folder for saving composite reflections
            reflections_folder_path = f"{reflections_folder_root}/{reflections_folder_name}"  # Path to composite reflection folder
            reflection_file_path = f"{reflections_folder_path}/{reflection_file_name}"  # Path to save composite reflection
            os.makedirs(reflections_folder_path, exist_ok=True)  # Ensure the folder exists
            with open(reflection_file_path, "w", encoding="utf-8") as file:
                file.write(composite_reflection)  # Write the composite reflection to a file

            # Save the unredacted reflection
            log.info("Saving unredacted reflection")
            reflection_file_name = f"Problem {problem_id}.txt"  # Filename for the unredacted reflection
            reflections_folder_name = f"{model_name} - unredacted - {exam_name}"  # Folder for unredacted reflections
            reflections_folder_path = f"{reflections_folder_root}/{reflections_folder_name}"  # Path to unredacted reflection folder
            reflection_file_path = f"{reflections_folder_path}/{reflection_file_name}"  # Path for saving unredacted reflection
            os.makedirs(reflections_folder_path, exist_ok=True)  # Ensure folder exists
            with open(reflection_file_path, "w", encoding="utf-8") as file:
                file.write(unredacted_message)  # Write the unredacted reflection to a file

            log.close()  # Close the log for this problem