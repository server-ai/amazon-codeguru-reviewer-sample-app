import boto3
import json
import logging
import time
from botocore.exceptions import ClientError

# Set the correct model ID for Llama 3.
MODEL_ID = "meta.llama3-70b-instruct-v1:0"
REGION = "us-east-1"

def analyze_and_correct_code():
    try:
        # Load the CodeGuru recommendations from the JSON file
        logging.info("Loading CodeGuru recommendations...")
        with open('codeguru_results.json', 'r') as file:
            recommendations = json.load(file)
        
        logging.info(f"Recommendations loaded: {json.dumps(recommendations, indent=2)}")

        # Open the original code file
        with open('src/master/java/com/shipmentEvents/handlers/EventHandler.java', 'r') as code_file:
            code = code_file.read()

        logging.info("Original code loaded for review.")
        
        # Ask Llama 3 to explain what it sees in the CodeGuru payload
        explanation = get_llama3_explanation(recommendations)
        logging.info(f"Llama 3's explanation of the CodeGuru recommendations:\n{explanation}")
        
        # Continue to apply the corrections
        corrected_code = correct_code_with_llama3(code, recommendations)
        
        if corrected_code and corrected_code != code:
            # Write the corrected code to the same file
            with open('src/master/java/com/shipmentEvents/handlers/EventHandler.java', 'w') as code_file:
                code_file.write(corrected_code)
            logging.info("Corrected code written back to the file.")
        else:
            logging.info("No corrections were made.")
            
    except Exception as e:
        logging.error(f"Error during code review: {str(e)}")
        exit(1)

def get_llama3_explanation(recommendations):
    # Create a Bedrock Runtime client
    client = boto3.client("bedrock-runtime", region_name=REGION)
    
    # Prepare a prompt asking Llama 3 to explain the recommendations
    prompt = f"Here is a JSON payload from CodeGuru containing code recommendations:\n\n{json.dumps(recommendations, indent=2)}\n\n"
    prompt += "Can you explain what this payload represents and summarize the key points?"

    # Format the request payload
    formatted_prompt = f"""
    <|begin_of_text|><|start_header_id|>user<|end_header_id|>
    {prompt}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """

    native_request = {
        "prompt": formatted_prompt,
        "max_gen_len": 512,
        "temperature": 0.5,
    }

    try:
        request = json.dumps(native_request)
        response = client.invoke_model(modelId=MODEL_ID, body=request)
        model_response = json.loads(response["body"].read())
        explanation = model_response.get("generation", "No explanation received.")
        return explanation

    except (ClientError, Exception) as e:
        logging.error(f"Failed to retrieve explanation from Llama 3: {e}")
        return None

def correct_code_with_llama3(code, recommendations):
    # Create a Bedrock Runtime client
    client = boto3.client("bedrock-runtime", region_name=REGION)

    # Prepare the prompt for Llama 3 with CodeGuru recommendations
    logging.info("Sending code to Llama 3 for corrections based on CodeGuru recommendations.")
    prompt = f"Here is the original code:\n\n{code}\n\n"
    prompt += "I want you to only make the changes based on the following CodeGuru recommendations:\n"
    prompt += json.dumps(recommendations, indent=2)
    
    # Format the request payload
    formatted_prompt = f"""
    <|begin_of_text|><|start_header_id|>user<|end_header_id|>
    {prompt}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """

    native_request = {
        "prompt": formatted_prompt,
        "max_gen_len": 1024,  # Adjust length based on expected output
        "temperature": 0.5,
    }

    # Send the request to Llama 3
    try:
        request = json.dumps(native_request)
        response = client.invoke_model(modelId=MODEL_ID, body=request)
        model_response = json.loads(response["body"].read())
        
        # Extract the generated corrected code from the response
        corrected_code = model_response.get("generation", "")
        logging.info("Received corrected code from Llama 3.")
        return corrected_code

    except (ClientError, Exception) as e:
        logging.error(f"Failed to retrieve corrected code from Llama 3: {e}")
        return None

if __name__ == "__master__":
    logging.basicConfig(level=logging.INFO)
    analyze_and_correct_code()
