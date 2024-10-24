# Key Points : 


'''1.	Data Loading: The code reads text files from a specified directory structure. These files contain “Error Keywords” and are processed to extract relevant keywords.
	2.	Keyword Cleaning and Remapping: Unwanted phrases/words are removed from the keywords, and certain keywords are standardized using a dictionary (remap_list).
	3.	Filtering: Only top-level keywords (first lines related to errors) are selected for analysis.
	4.	Keyword Aggregation: Keywords are grouped by model_name and keyword to count their occurrences and calculate their average depth (though depth is mostly 1 here).
	5.	Visualization: A horizontal bar chart is plotted to display the top N keywords, with different colors representing different models. The plot is stacked to show keyword occurrences for each model.

Adjustments:

	•	The code processes only files with the agent name “keywords” and skips files unless they are related to “comprehensive-100.”
	•	The horizontal bar chart is built to show how many times each error keyword appeared, categorized by the model.
'''







import os
import pandas as pd
import matplotlib.pyplot as plt

root_folder_path = "../data/reflections"
keywords = pd.DataFrame()

remove_list = [
    "* ",
    "$\\begin{array}{r}",
    "\\end{array}$",
    "error",
    "incorrectly",
    "incorrect",
    "incomplete",
    "lack of",
    "of the question",
    "of the problem",
    "the question",
    "the problem",
    "the argument"
]

remap_list = {
    "": "N/A",
    "misinterpretation": "interpretation",
    "misreading": "reading",
    "misunderstanding": "understanding",
    "attention to detail": "attention to detail",
    "attention to details": "attention to detail",
    "inattention to detail": "attention to detail",
    "inattention": "attention to detail",
    "knowledge gap": "knowledge",
    "failure to consider all possibilities": "consideration",
    "failure to consider all possible scenarios": "consideration",
    "logical": "logic",
    "logical reasoning": "logic",
}

for folder_name in os.listdir(root_folder_path):

    folder_path = root_folder_path + "/" + folder_name
    folder_name_parts = folder_name.split(" - ")
    model_name = folder_name_parts[0]
    agent_name = folder_name_parts[1]
    exam_name = folder_name_parts[2]

    if agent_name != "keywords":
        continue

    for file_name in os.listdir(folder_path):

        file_path = folder_path + "/" + file_name
        if not file_name.endswith(".txt"):
            continue

        if "comprehensive-100" not in file_path:
            continue

        print(file_path)

        with open(file_path, "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if line.startswith("Error Keywords:"):
                    continue

                keyword = line.strip()
                keyword = keyword.lower()
                keyword = keyword.replace("- ", "")

                for remove_words in remove_list:
                    keyword = keyword.replace(remove_words, "")

                keyword = keyword.strip()

                if keyword in remap_list:
                    keyword = remap_list[keyword]

                keyword_row = {
                    "model_name": model_name,
                    "keyword": keyword,
                    "depth": i}

                keywords = keywords._append(keyword_row, ignore_index=True)

keywords.reset_index()

# Filter in only top-level keywords
keywords = keywords[keywords["depth"] == 1]

# Group the unique keywords, count them, and average the depth
unique_keywords = keywords \
    .groupby(["model_name", "keyword"]) \
    .agg(count=("keyword", "count"),
        depth =("depth", "mean")) \
    .reset_index()

# Sort by count
unique_keywords = unique_keywords \
    .sort_values(by="count", ascending=False)

# Get the top n keywords
top_n = 100
top_keywords = unique_keywords.head(top_n)

# # Plot the top n keywords
# plt.figure(figsize=(10, 5))
# plt.barh(
#     top_keywords["keyword"],
#     top_keywords["count"])
# plt.title(f"Top {top_n} Error Keywords")
# plt.xlabel("Count")
# plt.ylabel("Keyword")
# plt.gca().invert_yaxis()
# plt.subplots_adjust(left=0.2)
# plt.show()

# Plot the top n keywords as a stacked barchart by model_name
plt.figure(figsize=(10, 10))
plt.barh(
    top_keywords["keyword"],
    top_keywords["count"],
    color="gray")
for i, model_name in enumerate(top_keywords["model_name"].unique()):
    model_keywords = top_keywords[top_keywords["model_name"] == model_name]
    plt.barh(
        model_keywords["keyword"],
        model_keywords["count"],
        color=f"C{i}",
        label=model_name)
plt.title(f"Top {top_n} Error Keywords by Model")
plt.xlabel("Count")
plt.ylabel("Keyword")
plt.gca().invert_yaxis()
plt.subplots_adjust(left=0.2)
plt.legend(title="Model")
plt.show()



