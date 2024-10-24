# Key Points: 

'''	1.	Data Loading and Filtering: The code loads results from a CSV file and has optional filters for specific models or exams (currently commented out). It excludes results from the "comprehensive-100" exam.
	2.	Data Processing: The shared module functions are used to add baseline results, set titles for models, agents, and exams, and sort the results to make them ready for visualization.
	3.	Custom Color Palette: A custom color palette is created using Seaborn’s “tab10” palette, and the 8th and 9th colors are swapped for better color distinction.
	4.	Plotting Accuracy: For each model, a bar plot is created to visualize the accuracy of different agents across various exams. The plot is saved as a PDF and also displayed using matplotlib.
	5.	Pivot Table for Accuracy: A pivot table is generated with agent types as rows and exam titles as columns, displaying the mean accuracy for each combination. This table is saved as a CSV file.
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
]  # List of models for which results will be visualized and processed

# Set parameters (agent_name and exam_name can be set if needed)
agent_name = None  # Default agent name is None
exam_name = None  # Default exam name is None
input_file = f"../data/results/results.csv"  # File path to the results CSV file

# Load the results data from the CSV file
results = pd.read_csv(input_file)

# DEBUG: Filter results for specific model or exam (currently commented out)
# Uncomment to filter by a specific model or exam
# results = results[results["Model Name"] == "gpt-35-turbo"]  # Filter results for GPT-3.5 Turbo model
# results = results[results["Exam Name"] == "comprehensive-100"]  # Filter results for the "comprehensive-100" exam
results = results[results["Exam Name"] != "comprehensive-100"]  # Exclude "comprehensive-100" exam from results

# Process the results by applying custom functions (from the shared module)
results = shared.add_baseline_results(results)  # Add baseline results to the dataset
results = shared.set_model_titles(results)  # Set model titles for visualization
results = shared.set_agent_titles(results)  # Set agent titles for visualization
results = shared.set_exam_titles(results)  # Set exam titles for visualization
results = shared.sort_by_agent(results)  # Sort the results by agent type
results = shared.sort_by_model(results)  # Sort the results by model

# Create a custom color palette (swap the last two colors for better distinction)
palette = sns.color_palette("tab10")  # Use the "tab10" color palette from Seaborn
palette[7], palette[8] = palette[8], palette[7]  # Swap the 8th and 9th colors in the palette

# Loop through each model in the model_names list
for model_name in model_names:

    # Create the output folder for saving plots related to this model
    output_folder = f"../data/plots/{model_name}"  # Define the output folder for plots
    os.makedirs(output_folder, exist_ok=True)  # Create the folder if it doesn't exist

    # Filter the results to only include data for the current model
    model_results = results[results["Model Name"] == model_name]

    # Plot the accuracy by agent and exam (bar plot)
    plt.figure(figsize=(10, 5))  # Set figure size
    sns.barplot(
        x="Exam Title",  # x-axis: Exam names
        y="Accuracy",  # y-axis: Accuracy values
        hue="Agent Title",  # Different agents shown using different colors (hue)
        data=model_results,  # Data source for the plot
        ci=None,  # No confidence intervals displayed
        palette=palette  # Use the custom color palette
    )
    plt.title(f"Accuracy by Exam and Agent for {shared.get_model_title(model_name)}")  # Set the plot title
    plt.xlabel("Exam")  # Set the x-axis label
    plt.ylabel("Accuracy")  # Set the y-axis label
    plt.xticks(rotation=15, ha="right")  # Rotate x-axis labels by 15 degrees and align to the right
    plt.ylim(0, 1.1)  # Set y-axis limits from 0 to 1.1 for better visualization
    plt.legend(loc="lower right")  # Place the legend in the lower right corner
    plt.tight_layout()  # Adjust layout to avoid cutting off labels
    plt.savefig(f"{output_folder}/accuracy-by-exam-and-agent.pdf")  # Save the plot as a PDF
    plt.show()  # Display the plot

    # Create a table of accuracy by exam and agent, with agents as rows and exams as columns

    # Create a pivot table for accuracy values
    pivot_table = model_results.pivot_table(
        index="Agent Title",  # Rows: Agent types
        columns="Exam Title",  # Columns: Exam titles
        values="Accuracy",  # Values: Accuracy for each agent-exam pair
        aggfunc="mean"  # Aggregation function: Compute the mean accuracy for each pair
    )

    # Save the pivot table to a CSV file
    pivot_table.to_csv(f"../data/tables/accuracy-by-exam-and-agent-for-{model_name}.csv")  # Save as CSV