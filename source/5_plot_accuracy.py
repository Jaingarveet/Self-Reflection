# Key Points:
'''1.	Data Filtering: The results dataset is filtered to remove data related to the "comprehensive-100" exam, and further filters can be applied for debugging specific models or exams (currently commented out).
	2.	Data Summarization: Using groupby, the results are summarized by Model Name and Agent Name to compute aggregate values like total questions, correct/incorrect counts, and average accuracy.
	3.	Shared Module: Several helper functions (e.g., add_baseline_results, set_agent_titles) are called from the shared module, which likely helps in adding additional data or adjusting formatting.
	4.	Plotting Accuracy: A bar plot is created to visualize the accuracy of different agents for each model. The plot is saved as a PDF and shown using matplotlib and seaborn.
	5.	Plotting Improvement: A similar bar plot is created to show the percentage improvement by different agents for each model, also saved and displayed.
'''





# Import the necessary packages
import os  # For handling file and directory operations
import pandas as pd  # For handling and processing CSV data
import matplotlib.pyplot as plt  # For plotting graphs
import seaborn as sns  # For enhanced data visualization (e.g., bar plots)
import shared  # Custom shared module for additional processing (likely custom code you've created)
import warnings  # To handle warnings in the code

# Ignore FutureWarnings in the output
warnings.simplefilter(action='ignore', category=FutureWarning)

# Set the model names to be analyzed
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
]  # List of models whose performance will be analyzed

# Set parameters (agent_name and exam_name are set to None as defaults)
agent_name = None
exam_name = None
input_file = f"../data/results/results.csv"  # File path to the results CSV file

# Load the data from the CSV file
results = pd.read_csv(input_file)

# DEBUG: Filter the results based on model or exam (currently commented out)
# These lines can be uncommented if you want to debug specific results.
# results = results[results["Model Name"] == "gpt-35-turbo"]  # Debug specific model results
# results = results[results["Exam Name"] == "comprehensive-100"]  # Debug specific exam results
results = results[results["Exam Name"] != "comprehensive-100"]  # Filter out "comprehensive-100" exam results

# Filter for retry agent results only
retry_results = results[results["Agent Name"] == "retry"]

# Summarize the metrics: group data by "Model Name" and "Agent Name"
summary = results.groupby(["Model Name", "Agent Name"]).agg({
    "Questions": "sum",    # Total number of questions
    "Correct": "sum",      # Total number of correct answers
    "Incorrect": "sum",    # Total number of incorrect answers
    "Num Errors": "sum",   # Total number of errors
    "Accuracy": "mean"     # Average accuracy
}).reset_index()  # Reset index to get a proper DataFrame

# Process the data by adding additional information
summary = shared.add_baseline_results(summary)  # Add baseline results (function likely in shared module)
summary = shared.set_agent_titles(summary)  # Set agent titles for display purposes
summary = shared.sort_by_agent(summary)  # Sort the data by agent for better visualization

# Loop through each model in the model_names list
for model_name in model_names:

    # Create an output folder for saving the plots for this model
    output_folder = f"../data/plots/{model_name}"  # Folder to save the plots for this model
    os.makedirs(output_folder, exist_ok=True)  # Create the folder if it doesn't exist

    # Filter the summary for the current model
    model_summary = summary[summary["Model Name"] == model_name]

    # Plot the accuracy by agent type (bar plot)
    plt.figure(figsize=(10, 5))  # Set figure size
    barplot = sns.barplot(
        x="Agent Title",  # x-axis: Agent type
        y="Accuracy",  # y-axis: Accuracy
        data=model_summary,  # Data source
        color=sns.color_palette()[0])  # Set bar color using default color palette
    plt.title(f"Accuracy by Agent for {shared.get_model_title(model_name)}")  # Set the plot title
    plt.xlabel("Agent")  # x-axis label
    plt.ylabel("Accuracy")  # y-axis label
    plt.xticks(rotation=15, ha="right")  # Rotate the x-axis labels for better readability
    plt.ylim(0.0, 1.1)  # Set y-axis limits from 0 to 1.1
    for p in barplot.patches:  # Annotate each bar with its value
        barplot.annotate(
            format(p.get_height(), '.2f'),  # Format the height (accuracy) of each bar to two decimal points
            (p.get_x() + p.get_width() / 2., p.get_height()),  # Position the annotation on the bar
            ha='center',  # Center horizontally
            va='center',  # Center vertically
            xytext=(0, 7),  # Offset the text by 7 points vertically
            textcoords='offset points')
    plt.tight_layout()  # Adjust layout to avoid cutting off labels
    plt.savefig(f"{output_folder}/accuracy-by-agent.pdf")  # Save the plot as a PDF in the output folder
    plt.show()  # Show the plot

    # Plot the improvement by agent type (bar plot)
    plt.figure(figsize=(10, 5))  # Set figure size
    barplot = sns.barplot(
        x="Agent Title",  # x-axis: Agent type
        y="Improvement",  # y-axis: Improvement percentage
        data=model_summary,  # Data source
        color=sns.color_palette()[0])  # Set bar color using default color palette
    plt.title(f"Improvement by Agent for {shared.get_model_title(model_name)}")  # Set the plot title
    plt.xlabel("Agent")  # x-axis label
    plt.ylabel("Improvement (%)")  # y-axis label
    plt.xticks(rotation=15, ha="right")  # Rotate the x-axis labels for better readability
    plt.ylim(0, 100)  # Set y-axis limits from 0 to 100 (percentage improvement)
    for p in barplot.patches:  # Annotate each bar with its value
        barplot.annotate(
            format(p.get_height(), '.2f'),  # Format the height (improvement) of each bar to two decimal points
            (p.get_x() + p.get_width() / 2., p.get_height()),  # Position the annotation on the bar
            ha='center',  # Center horizontally
            va='center',  # Center vertically
            xytext=(0, 7),  # Offset the text by 7 points vertically
            textcoords='offset points')
    plt.tight_layout()  # Adjust layout to avoid cutting off labels
    plt.savefig(f"{output_folder}/improvement-by-agent.pdf")  # Save the plot as a PDF in the output folder
    plt.show()  # Show the plot