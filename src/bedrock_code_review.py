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
        
        # Prepare the prompt for Llama 3 based on CodeGuru recommendations
        prompt = f"Here is the original code:\n\n{code}\n\n"
        prompt += "I want you to only make the changes based on the following CodeGuru recommendations:\n"
        for rec in recommendations['RecommendationSummaries']:
            prompt += f"- From line {rec['StartLine']} to {rec['EndLine']}: {rec['Description']}\n"
        
        corrected_code = invoke_llama3(prompt)

        # If corrections were made, write them back to the file
        if corrected_code and corrected_code != code:
            with open('src/master/java/com/shipmentEvents/handlers/EventHandler.java', 'w') as code_file:
                code_file.write(corrected_code)
            logging.info("Corrected code written back to the file.")
        else:
            logging.info("No corrections were made.")

    except Exception as e:
        logging.error(f"Error during code review: {str(e)}")
        exit(1)

def invoke_llama3(prompt):
    # Create a Bedrock Runtime client
    client = boto3.client("bedrock-runtime", region_name=REGION)

    # Prepare the request payload
    native_request = {
        "prompt": prompt,
        "max_gen_len": 2000,
        "temperature": 0.8,
    }

    # Send the request to Llama 3
    try:
        request = json.dumps(native_request)
        response = client.invoke_model(modelId=MODEL_ID, body=request)

        # Wait for Llama 3 to process the response
        logging.info("Waiting for Llama 3 to process the response...")
        time.sleep(5)  # Adjust the delay if necessary

        model_response = json.loads(response["body"].read())

        # Extract the generated corrected code from the response
        corrected_code = model_response["generation"]
        logging.info("Received corrected code from Llama 3.")
        return corrected_code

    except (ClientError, Exception) as e:
        logging.error(f"Failed to retrieve corrected code from Llama 3: {e}")
        return None

if __name__ == "__master__":
    logging.basicConfig(level=logging.INFO)
    analyze_and_correct_code()
