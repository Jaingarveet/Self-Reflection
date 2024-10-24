# Key Points : 


'''	1.	Parameters and File Handling: The script loads the results from a CSV file, with options to modify which model, agent, or exam to focus on. Output directories for saving plots are also set up.
	2.	Data Loading and Filtering: Results are loaded from the CSV file, and there’s an option to filter based on a specific exam for debugging purposes. In the default state, it filters out the "comprehensive-100" exam data.
	3.	Data Processing: Custom functions from the shared module are used to add baseline results, set titles for models and agents, and sort the data to make it ready for visualization.
	4.	Custom Color Palette: A custom Seaborn color palette is created, with a specific modification that swaps the last two colors for better distinction.
	5.	Plotting Accuracy: The first plot shows accuracy for each model, broken down by agent types using a bar plot. The plot is saved as a PDF and displayed.
	6.	Plotting Improvement: The second plot shows the improvement percentage for each model, also broken down by agent types. This plot is similarly saved and displayed.
	7.	Visualization Settings: The plots use various settings like rotated x-axis labels, adjusted margins, and custom legends to make the plots more readable and visually clear. '''

















# Import the necessary packages
import os  # For handling file and directory operations
import re  # For regular expressions (not used here, but imported)
import pandas as pd  # For handling and processing CSV data
import matplotlib.pyplot as plt  # For plotting graphs
import seaborn as sns  # For enhanced data visualization (e.g., bar plots)
import shared  # Custom shared module for additional processing (likely custom code you've created)
import warnings  # To handle warnings in the code

# Ignore FutureWarnings in the output
warnings.simplefilter(action='ignore', category=FutureWarning)

# Set the parameters (model, agent, and exam names)
model_name = "gpt-4"  # Default model used for the analysis
# model_name = "gpt-35-turbo"  # Uncomment to use GPT-3.5 Turbo model
# model_name = "llama-2-7b-chat"  # Uncomment to use LLaMA-2 7B Chat model
# model_name = "llama-2-70b-chat"  # Uncomment to use LLaMA-2 70B Chat model
# model_name = "mistral-large"  # Uncomment to use Mistral-Large model
# model_name = "cohere-command-r-plus"  # Uncomment to use Cohere Command R Plus model
agent_name = None  # Default agent name is None (can be modified as needed)
exam_name = None  # Default exam name is None (can be modified)
input_file = f"../data/results/results.csv"  # File path to the results CSV file
output_folder = f"../data/plots"  # Folder where the output plots will be saved

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Load the data from the CSV file
results = pd.read_csv(input_file)

# DEBUG: Option to filter the results for debugging purposes (currently commented out)
# Uncomment to filter by a specific exam
# results = results[results["Exam Name"] == "comprehensive-100"]  
results = results[results["Exam Name"] != "comprehensive-100"]  # Exclude "comprehensive-100" exam data

# Process the results by applying custom functions (from the shared module)
results = shared.add_baseline_results(results)  # Add baseline results for comparison
results = shared.set_model_titles(results)  # Set the model titles for display purposes
results = shared.set_agent_titles(results)  # Set the agent titles for display purposes
results = shared.sort_by_agent(results)  # Sort the results by agent for better visualization
results = shared.sort_by_model(results)  # Sort the results by model for consistency

# Create a custom color palette for plotting (swap the last two colors)
palette = sns.color_palette("tab10")  # Use the "tab10" color palette from Seaborn
palette[7], palette[8] = palette[8], palette[7]  # Swap the colors for better distinction

# Plot the accuracy by model and agent (bar plot)
plt.figure(figsize=(10, 5))  # Set figure size
sns.barplot(
    x="Model Title",  # x-axis: Model names
    y="Accuracy",  # y-axis: Accuracy values
    hue="Agent Title",  # Different agents will be shown using different colors (hue)
    data=results,  # Data source for the plot
    ci=None,  # No confidence intervals displayed
    palette=palette  # Use the custom color palette
)
plt.title("Accuracy by Model and Agent")  # Set the plot title
plt.xlabel("Model")  # Set the x-axis label
plt.ylabel("Accuracy")  # Set the y-axis label
plt.ylim(0.0, 1.0)  # Set the y-axis range (0 to 1 for accuracy)
plt.xticks(rotation=15)  # Rotate x-axis labels by 15 degrees for readability
plt.subplots_adjust(bottom=0.2)  # Adjust the bottom margin to avoid label cutoff
plt.legend(title="Agent", loc="lower right")  # Set the legend location and title
plt.tight_layout()  # Ensure everything fits within the figure area
plt.savefig(f"{output_folder}/accuracy-by-model-and-agent.pdf")  # Save the plot as a PDF
plt.show()  # Display the plot

# Plot the improvement by model and agent (bar plot)
plt.figure(figsize=(10, 5))  # Set figure size
sns.barplot(
    x="Model Title",  # x-axis: Model names
    y="Improvement",  # y-axis: Improvement percentage
    hue="Agent Title",  # Different agents will be shown using different colors (hue)
    data=results,  # Data source for the plot
    ci=None,  # No confidence intervals displayed
    palette=palette  # Use the custom color palette
)
plt.title("Improvement by Model and Agent")  # Set the plot title
plt.xlabel("Model")  # Set the x-axis label
plt.ylabel("Improvement (%)")  # Set the y-axis label to show improvement in percentage
plt.ylim(0, 100)  # Set the y-axis range (0 to 100 for improvement percentage)
plt.xticks(rotation=15)  # Rotate x-axis labels by 15 degrees for readability
plt.subplots_adjust(bottom=0.2)  # Adjust the bottom margin to avoid label cutoff
plt.legend(title="Agent", loc="upper right")  # Set the legend location and title
plt.tight_layout()  # Ensure everything fits within the figure area
plt.savefig(f"{output_folder}/improvement-by-model-and-agent.pdf")  # Save the plot as a PDF
plt.show()  # Display the plot