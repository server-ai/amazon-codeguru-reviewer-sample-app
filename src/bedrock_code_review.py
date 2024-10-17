import json
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Load the Llama model and tokenizer (You can update this with the correct model)
MODEL_NAME = "meta-llama/Llama-2-7b-hf"  # Example Llama model; replace with an actual Llama 3 model if available
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

def analyze_and_correct_code():
    try:
        # Load the CodeGuru recommendations from the JSON file
        logging.info("Loading CodeGuru recommendations...")
        with open('codeguru_results.json', 'r') as file:
            recommendations = json.load(file)

        logging.info(f"Recommendations loaded: {json.dumps(recommendations, indent=2)}")

        # Open the original code file
        with open('src/main/java/com/shipmentEvents/handlers/EventHandler.java', 'r') as code_file:
            code = code_file.read()

        logging.info("Original code loaded for review.")
        
        # Ask Llama to explain what it sees in the CodeGuru payload
        explanation = get_llama_explanation(recommendations)
        logging.info(f"Llama's explanation of the CodeGuru recommendations:\n{explanation}")
        
        # Continue to apply the corrections
        corrected_code = correct_code_with_llama(code, recommendations)
        
        if corrected_code and corrected_code != code:
            # Write the corrected code to the same file
            with open('src/main/java/com/shipmentEvents/handlers/EventHandler.java', 'w') as code_file:
                code_file.write(corrected_code)
            logging.info("Corrected code written back to the file.")
        else:
            logging.info("No corrections were made.")
            
    except Exception as e:
        logging.error(f"Error during code review: {str(e)}")
        exit(1)

def get_llama_explanation(recommendations):
    # Prepare a prompt asking Llama to explain the recommendations
    prompt = f"Here is a JSON payload from CodeGuru containing code recommendations:\n\n{json.dumps(recommendations, indent=2)}\n\n"
    prompt += "Can you explain what this payload represents and summarize the key points?"

    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs)
    explanation = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return explanation

def correct_code_with_llama(code, recommendations):
    # Prepare the prompt for Llama with CodeGuru recommendations
    logging.info("Sending code to Llama for corrections based on CodeGuru recommendations.")
    prompt = f"Here is the original code:\n\n{code}\n\n"
    prompt += "I want you to only make the changes based on the following CodeGuru recommendations:\n"
    prompt += json.dumps(recommendations, indent=2)

    # Tokenize and generate the corrected code using Llama
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=1024)

    # Extract the generated corrected code from the response
    corrected_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    logging.info("Received corrected code from Llama.")
    return corrected_code

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyze_and_correct_code()
