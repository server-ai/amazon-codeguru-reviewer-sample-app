import boto3
import json
import logging
from botocore.exceptions import ClientError

# Constants for AWS Bedrock
MODEL_ID = "meta.llama3-70b-instruct-v1:0"  # LLaMA 3 Model ID
REGION = "us-east-1"

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

        # Send code and CodeGuru recommendations to LLaMA 3 via Bedrock
        corrected_code = correct_code_with_llama3(code, recommendations)
        
        if corrected_code and corrected_code != code:
            # Write the corrected code back to the file
            with open('src/main/java/com/shipmentEvents/handlers/EventHandler.java', 'w') as code_file:
                code_file.write(corrected_code)
            logging.info("Corrected code written back to the file.")
        else:
            logging.info("No corrections were made.")
            
    except Exception as e:
        logging.error(f"Error during code review: {str(e)}")
        exit(1)

def correct_code_with_llama3(code, recommendations):
    # Create a Bedrock client
    client = boto3.client("bedrock-runtime", region_name=REGION)

    # Prepare the prompt for LLaMA 3 with CodeGuru recommendations
    logging.info("Sending code and CodeGuru recommendations to LLaMA 3 for corrections.")
    prompt = f"Here is the original code:\n\n{code}\n\n"
    prompt += "Please apply the following CodeGuru recommendations:\n"
    prompt += json.dumps(recommendations, indent=2)
    
    # Create the Bedrock model request payload
    native_request = {
        "prompt": prompt,
        "max_gen_len": 1024,  # Adjust based on expected output
        "temperature": 0.5
    }

    # Send the request to LLaMA 3
    try:
        request = json.dumps(native_request)
        response = client.invoke_model(modelId=MODEL_ID, contentType='application/json', body=request)
        model_response = json.loads(response['body'].read())

        # Extract the generated corrected code from the response
        corrected_code = model_response.get("generation", "")
        logging.info("Received corrected code from LLaMA 3.")
        return corrected_code

    except ClientError as e:
        logging.error(f"ClientError: Failed to retrieve corrected code from LLaMA 3: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyze_and_correct_code()




