from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from typing import Dict, Any
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Set your API key for Gemini (ensure the API key is correctly set in the environment variable or hardcoded here)
#os.environ["GOOGLE_API_KEY"] = "AIzaSyBJn-qeW-_DXjc4fFoRGOBWMgAqsQzXKqo"

# Initialize the Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0.7,
    max_tokens=1000
)

# Knowledge base containing ethical standards
knowledge_base = {
    "mice count_max": 25,
    "rats count_max": 15,
    "rabbits count_max": 10,
    "wistar rat count_max": 40,
    "albino rat count_max": 40,
    "swiss mice count_max": 40,
    "weight_min": 180,
    "weight_max": 200,
    "cage_type": "plastic",
    "ventilation_temp": (28, 32),
    "light_dark_hours": 12,
    "water_access": "yes",
    "pellet_condition": "dry",
    "acclimatization_days": 15,
    "human_care_assurance": "yes"
}

# Function to extract and check compliance using LLM
#def analyze_proposal_with_llm(proposal: str) -> dict:
    prompt_template = PromptTemplate(
        input_variables=["proposal", "standards"],
        template="""
        You are an AI tasked with analyzing research proposals for ethical compliance in animal usage. Your job is to extract the required details exactly as they appear in the proposal and check compliance against the provided ethical standards.

        Required details to extract:
        Animal type and their count
        Weight of animals in grams
        Type of cage used
        Ventilation temperature in degrees Celsius
        Number of hours exposed to natural light and darkness
        Whether the animal had access to water (yes/no)
        Condition of animal pellet (dry/wet)
        Number of days of acclimatization
        Assurance of human care for the animal (yes/no)

        from the following proposal: {proposal}

        Compliance Check:
        Once the details are extracted, compare them strictly against the following ethical standards:
        {standards}
        Important Guidelines:
        Stick 100% to what is written in the proposal. Do not infer, assume, or modify any information.
        If any information is missing, explicitly state it as "Not Found".
        Perform compliance checks only on the extracted data—do not create missing values for compliance checking.
        include name of animal key in compliance report.
        Response Format:
        Provide the output as a valid JSON object with two main keys:

        "extracted_data" → Contains the extracted details exactly as they appear in the proposal.
        "compliance_report" → Indicates whether each parameter is "Compliant" or "Non-compliant" based on the given standards.
         Add reasons for compliance or non-compliance
        Example Output:

        ((
        "extracted_data": 
            "Animal type": "Wistar rats",  
            "Animal count": 30,  
            "Weight of animals in grams": 190,  
            "Type of cage used": "plastic cages",  
            "Ventilation temperature in degrees Celsius": 29,  
            "Number of hours exposed to natural light": 10,  
            "Number of hours exposed to darkness": "Not Found",  
            "Access to water": "yes",  
            "Condition of animal pellet": "dry",  
            "Number of days of acclimatization": 20,  
            "Assurance of human care for the animal": "yes"  
        )),  
        
            Extracted Data: (('Animal type': 'wistar rat', 'Animal count': 40, 'Weight of animals in grams': '180- 200 g', 'Type of cage used': 'rat cages', 'Ventilation temperature in degrees Celsius': '25 ± 2°C', 'Number of hours exposed to natural light': '12h', 'Number of hours exposed to darkness': '12h', 'Access to water': 'yes', 'Condition of animal pellet': 'dry', 'Number of days of acclimatization': 14, 'Assurance of human care for the animal': 'yes'))
            Compliance Report: (('Animal count': 'Compliant. The proposal specifies 40 wistar rats, which is within the allowed limit of 40.', 'Weight of animals in grams': 'Compliant. The weight range 180-200g falls within the specified range of 180-200g.', 'Type of cage used': "Non-compliant. The proposal mentions 'rat cages', while the standard specifies 'plastic'.", 'Ventilation temperature in degrees Celsius': 'Non-compliant.  The proposal states 25 ± 2°C.  This range (23-27°C) does not fall within the required range of 28-32°C.', 'Number of hours exposed to natural light': 'Compliant. The proposal specifies 12h of natural light, matching the standard of 12 hours.', 'Number of hours exposed to darkness': 'Compliant. The proposal specifies 12h of darkness, matching the standard of 12 hours (derived from the light hours).', 'Access to water': "Compliant. The proposal indicates free access to water, aligning with the 'yes' standard.", 'Condition of animal pellet': "Compliant.  The proposal specifies 'dry rat pellet', matching the 'dry' standard.", 'Number of days of acclimatization': 'Non-compliant. The proposal mentions 14 days of acclimatization, while the standard requires 15 days.', 'Assurance of human care for the animal': 'Compliant. The proposal explicitly states that the animals will receive humane care.'))
                                                                                                                                                                                                                

         
        ) )))

        """
    )
    
    formatted_prompt = prompt_template.format(proposal=proposal, standards=json.dumps(knowledge_base, indent=4))
    
    try:
        response = llm.invoke(formatted_prompt)
        content = response.content.strip('```json\n').strip('```')
        result = json.loads(content)
    except Exception as e:
        print(f"Error processing proposal: {e}")
        result = {}
    
    return result

# Example proposal
example_proposal = """
sixty adult wistar rat (180- 200 g) will be obtained for used in the course of the study. The rats 
will be kept in rat cages in well ventilated house, temperature of 25 ± 2°C, 12h natural light and 
12h darkness, with free access to tap water and dry rat pellet. They will be allowed to acclimatize 
for 14 days prior to the experiment. Ethical approval on the use of laboratory animals will be 
sought and all the animals will receive humane care in compliance with the institution’s guideline 
and criteria for humane care as outlined in the National Institute of Health Guidelines for the Care 
and Use of Laboratory Animals.
"""

#def main(proposal: str = example_proposal):

    # Example Proposal
    example_proposal = proposal
    
    # Analyze the proposal
    analysis_result = analyze_proposal_with_llm(example_proposal)

    # Output the result
    print("Extracted Data:", analysis_result.get("extracted_data", {}))
    print("Compliance Report:", analysis_result.get("compliance_report", {}))

    names = []

    for name in analysis_result.get("compliance_report", {}):
        names.append(name)

    return {
        'names': names,
        'extracted_data': analysis_result.get("extracted_data", {}),
        'compliance_report': analysis_result.get("compliance_report", {})
    }

if __name__ == '__main__':
    print(main())
