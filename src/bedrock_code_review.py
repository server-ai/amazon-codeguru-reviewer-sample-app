import boto3
import json
import logging
from botocore.exceptions import ClientError

# Set the correct model ID (change to an always available one like Claude)
MODEL_ID = "anthropic.claude-v2:1"
REGION = "us-east-1"

def analyze_and_correct_code():
    try:
        # Load the CodeGuru recommendations from the JSON file
        logging.info("Loading CodeGuru recommendations...")
        with open('codeguru_results.json', 'r') as file:
            recommendations = json.load(file)
        
        logging.info(f"Recommendations loaded: {json.dumps(recommendations, indent=2)}")

        # Open the original code file (correct path: 'src/main')
        with open('src/main/java/com/shipmentEvents/handlers/EventHandler.java', 'r') as code_file:
            code = code_file.read()

        logging.info("Original code loaded for review.")
        
        # Ask Llama 3 (or any other available model) to explain what it sees in the CodeGuru payload
        explanation = get_model_explanation(recommendations)
        logging.info(f"Model's explanation of the CodeGuru recommendations:\n{explanation}")
        
        # Continue to apply the corrections
        corrected_code = correct_code_with_model(code, recommendations)
        
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

def get_model_explanation(recommendations):
    client = boto3.client("bedrock-runtime", region_name=REGION)

    prompt = f"Here is a JSON payload from CodeGuru containing code recommendations:\n\n{json.dumps(recommendations, indent=2)}\n\n"
    prompt += "Can you explain what this payload represents and summarize the key points?"

    native_request = {
        "prompt": prompt,
        "max_gen_len": 2000,
        "temperature": 0.7,
    }

    try:
        request = json.dumps(native_request)
        response = client.invoke_model(modelId=MODEL_ID, body=request)
        model_response = json.loads(response["body"].read())
        explanation = model_response.get("generation", "No explanation received.")
        return explanation

    except (ClientError, Exception) as e:
        logging.error(f"Failed to retrieve explanation from model: {e}")
        return None

def correct_code_with_model(code, recommendations):
    client = boto3.client("bedrock-runtime", region_name=REGION)

    prompt = f"Here is the original code:\n\n{code}\n\n"
    prompt += "I want you to only make the changes based on the following CodeGuru recommendations:\n"
    prompt += json.dumps(recommendations, indent=2)

    native_request = {
        "prompt": prompt,
        "max_gen_len": 2000,
        "temperature": 0.7,
    }

    try:
        request = json.dumps(native_request)
        response = client.invoke_model(modelId=MODEL_ID, body=request)
        model_response = json.loads(response["body"].read())
        
        corrected_code = model_response.get("generation", "")
        logging.info("Received corrected code from the model.")
        return corrected_code

    except (ClientError, Exception) as e:
        logging.error(f"Failed to retrieve corrected code from model: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyze_and_correct_code()


