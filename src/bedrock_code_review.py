import boto3
import json
import logging
from botocore.exceptions import ClientError

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Constants for AWS Bedrock
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
        with open('src/main/java/com/shipmentEvents/handlers/EventHandler.java', 'r') as code_file:
            code = code_file.read()

        logging.info("Original code loaded for review.")
        
        # Pass the CodeGuru recommendations and code to Llama 3
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
    # Create a Bedrock Runtime client
    client = boto3.client("bedrock-runtime", region_name=REGION)

    # Prepare the prompt for Llama 3, including the CodeGuru recommendations
    logging.info("Sending code and CodeGuru recommendations to Llama 3 for corrections.")
    prompt = f"Here is the original Java code:\n\n{code}\n\n"
    prompt += "I want you to make corrections based on these specific CodeGuru recommendations:\n\n"
    prompt += json.dumps(recommendations, indent=2)
    
    # Format the request payload for Llama 3
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
        corrected_code = model_response.get('generation', '')
        if corrected_code:
            logging.info("Received corrected code from Llama 3.")
        else:
            logging.warning("No corrections were suggested by Llama 3.")
        
        return corrected_code

    # Combine these two exception types properly
    except ClientError as e:
        logging.error(f"ClientError: Failed to retrieve corrected code from Llama 3: {e}")
        return None
    except Exception as e:
        logging.error(f"Exception: Failed to retrieve corrected code from Llama 3: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyze_and_correct_code()



    except (ClientError, Exception) as e:
        logging.error(f"Failed to retrieve corrected code from Llama 3: {e}")
        return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyze_and_correct_code()

