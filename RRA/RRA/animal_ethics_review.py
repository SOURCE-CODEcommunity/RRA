from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from typing import Dict, Any
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain import PromptTemplate

# Set your API key for Gemini (ensure the API key is correctly set in the environment variable or hardcoded here)
os.environ["GOOGLE_API_KEY"] = "AIzaSyAr7AUSEW_3n4lHcF8IliLmdVb-IjenoNY"

# Initialize the Gemini model using ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",  # Specify the desired model version
    temperature=0.7,         # Adjust creativity level
    max_tokens=1000          # Set maximum tokens per response
)

# Load the knowledge base with animal usage standards
knowledge_base = {
    "mice": 25,
    "rats": 15,
    "rabbits": 10
}

# Function to extract animal count from proposal using the LLM
def extract_animal_count(proposal: str) -> Dict[str, int]:
    # Define the prompt for extracting animal counts
    extract_prompt = PromptTemplate(
        input_variables=["proposal"],
        template="""You are an AI tasked with analyzing research proposals for ethical compliance in animal usage.
        Extract the number and type of animals mentioned in the following proposal:
        {proposal}

        Provide the response as a JSON object where the keys are animal types and values are their counts."""
    )

    # Format the input using the prompt template
    formatted_prompt = extract_prompt.format(proposal=proposal)
    
    # Use LangChain's new 'invoke' method with the formatted prompt string
    try:
        response = llm.invoke(formatted_prompt)
        print("Response from Gemini:", response)  # Debugging the raw response
        
        # Access the content directly (no need for `.get()`)
        content = response.content  # Directly access the content attribute

        # The content should be JSON but wrapped with markdown syntax
        json_str = content.strip('```json\n').strip('```')  # Remove ```json and the closing ```

        # Parse the JSON string into a dictionary
        try:
            animal_counts = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            animal_counts = {}

    except Exception as e:
        print(f"Error with the model invocation: {e}")
        animal_counts = {}

    return animal_counts

# Function to check compliance with the knowledge base
def check_compliance(animal_counts: Dict[str, int], knowledge_base: Dict[str, int]) -> Dict[str, Any]:
    compliance_report = {}

    for animal, count in animal_counts.items():
        standard = knowledge_base.get(animal.lower(), None)
        if standard is None:
            compliance_report[animal] = "No standard available"
        elif count > standard:
            compliance_report[animal] = f"Exceeds standard (Allowed: {standard}, Found: {count})"
        else:
            compliance_report[animal] = "Compliant"

    return compliance_report

# Function to review a research proposal
def review_proposal(proposal: str):
    print("Extracting animal counts from the proposal...")
    animal_counts = extract_animal_count(proposal)

    print("Checking compliance with ethical standards...")
    compliance_report = check_compliance(animal_counts, knowledge_base)

    return {
        "animal_counts": animal_counts,
        "compliance_report": compliance_report
    }


def main(proposal: str = "This study will use 25 mice and 10 rabbits to test the effects of a new drug."):

    # Example Proposal
    example_proposal = proposal

    # Review the proposal
    review_result = review_proposal(example_proposal)

    # Output the result
    print("Animal Counts:", review_result["animal_counts"])
    print("Compliance Report:", review_result["compliance_report"])

    names = []

    for name in review_result["animal_counts"]:
        names.append(name)

    return {
        'names': names,
        'animal_count': review_result["animal_counts"],
        'compliance_report': review_result["compliance_report"]
    }

if __name__ == '__main__':
    print(main())