# Import necessary libraries
import openai
import os
import dotenv
import random
from pymongo import MongoClient
from openai import OpenAI

dotenv.load_dotenv()

client = OpenAI()

# Variables
openai.api_key = os.getenv("OPENAI_API_KEY")
mongoId= os.getenv("mongoclient")
database = str(os.getenv("db"))
data_collection=os.getenv("collection")

# Set up MongoDB connection
clientId = MongoClient(mongoId)
db = clientId[database]
collection = db[data_collection]

# List of project categories
project_categories = [
    "Project Management", "HR and Talent",
    "Sales and Marketing", "Creative and Content",
    "Entrepreneur"
]

project_type = [
    "single", "collaborative"
]

# Main loop for automation
while True:

    # Randomly select a project category
    selected_category = random.choice(project_categories)

    selected_type = random.choice(project_type)

    # Add variability to the prompt
    prompt_prefix = [
        "Generate a project idea for a",
        "I need a project suggestion related to",
        "Imagine a project in the domain of",
        "Here's a challenge: come up with a project for",
        "Let's brainstorm a project for"
    ]
    
    prompt_suffix = [
        "Make it unique and innovative.",
        "Ensure it aligns with industry standards.",
        "Consider the latest technologies for implementation.",
        "Think about potential user needs and pain points.",
        "Make sure it stands out from existing solutions."
    ]
    
    # Combine prefix, category, and suffix randomly
    prompt = random.choice(prompt_prefix) + f" {selected_category}. " + random.choice(prompt_suffix)

    if selected_type == "single":
        prompt += "\nProject Type: Single\n"
    else:
        prompt += "\nProject Type: Collaborative\n"

    prompt += "Project Title:\nCreate a compelling title for the project.\nProject Description:\nProvide a detailed description outlining the purpose, functionality, and goals of the project.\nTechnologies to Use:\nList a tech stack based on the project category. Provide a detailed list of the tech stacks.\nFeatures:\nEnumerate key features aligning with the project's goals. Give the feature title and description and do not include any numbering in the features.\nTimeFrame:\nDefine an estimated timeframe for project completion, considering the scope and complexity."

    
    response = client.chat.completions.create(
            model='gpt-4',
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
            n=1,
            stop=None,
            temperature=random.uniform(0.5, 1.0),
            top_p=random.uniform(0.7, 1.0)
        )

    reply = response.choices[0].message
    
    content = reply.content

    def extract_value(header, end_header, content):
        start_pos = content.find(header) + len(header)
        end_pos = content.find(end_header)
        return content[start_pos:end_pos].strip()

    # Function to extract features as a list
    def extract_features(features_text):
        features_list = features_text.split('\n')
        features_list = [feature.strip() for feature in features_list if feature.strip()]
        return features_list

    # Extracting values
    project_title = extract_value("Project Title:", "Project Description:", content)
    description = extract_value("Project Description:", "Technologies to Use:", content)
    tech_stack_text = extract_value("Technologies to Use:", "Features:", content)
    features_text = extract_value("Features:", "TimeFrame", content)

    tech_stack_lines = tech_stack_text.split('\n')
    tech_stack = [line.split('.')[1].strip() for line in tech_stack_lines if line.strip()]

    features_list = features_text.split('\n')
    features = [{"title": feature.split(':')[0].strip(), "description": feature.split(':')[1].strip(), "submitFeature": []} for feature in features_list if feature.strip()]

    # Check if the project already exists in the database before inserting
    existing_project = collection.find_one({"projectTitle": project_title, "projectType": selected_type, "category": selected_category})

    if not existing_project:
        collection.insert_one({
            "projectTitle": project_title,
            "projectType": selected_type,
            "description": description,
            "category": selected_category,
            "features": features,
            "techStack": tech_stack
        })