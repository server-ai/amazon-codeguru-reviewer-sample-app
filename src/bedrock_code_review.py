import boto3
import json
import logging
from botocore.exceptions import ClientError

# Set the correct model ID for Llama 3.
MODEL_ID = "meta.llama3-70b-instruct-v1:0"  # Ensure this is the correct model ID
REGION = "us-east-1"  # Specify the correct region

def analyze_and_correct_code():
    try:
        # Load the CodeGuru results
        with open('codeguru_results.json', 'r') as file:
            recommendations = json.load(file)
        logging.info("Loaded CodeGuru recommendations.")

        # Read the code from the file that CodeGuru reviewed
        with open('src/master/java/com/shipmentEvents/handlers/EventHandler.java', 'r') as file:
            code = file.read()

        # Correct the code with Llama 3 based on CodeGuru recommendations
        corrected_code = correct_code_with_llama3(code, recommendations)

        if corrected_code and corrected_code != code:
            # Write the corrected code back to the file
            with open('src/master/java/com/shipmentEvents/handlers/EventHandler.java', 'w') as file:
                file.write(corrected_code)
            logging.info("Corrected code written back to the file.")
        else:
            logging.info("No corrections were made.")

    except Exception as e:
        logging.error(f"Error during code review: {str(e)}")
        exit(1)

def correct_code_with_llama3(code, recommendations):
    # Create a Bedrock Runtime client
    client = boto3.client("bedrock-runtime", region_name=REGION)

    # Build the prompt from the CodeGuru recommendations
    prompt = f"The following Java code needs corrections based on the recommendations:\n\n{code}\n\n"
    for rec in recommendations["RecommendationSummaries"]:
        file_path = rec.get("FilePath")
        start_line = rec.get("StartLine")
        end_line = rec.get("EndLine")
        description = rec.get("Description")

        # Only include recommendations for the specified file
        if file_path == 'src/master/java/com/shipmentEvents/handlers/EventHandler.java':
            prompt += f"Please modify the code from line {start_line} to {end_line} with the following recommendation:\n{description}\n"

    prompt += "Only change the specified lines and ensure the rest of the code remains intact.\n"

    logging.info("Sending code to Llama 3 for corrections based on CodeGuru recommendations.")

    # Prepare the request payload
    formatted_prompt = f"""
    <|begin_of_text|><|start_header_id|>user<|end_header_id|>
    {prompt}
    <|eot_id|>
    <|start_header_id|>assistant<|end_header_id|>
    """

    native_request = {
        "prompt": formatted_prompt,
        "max_gen_len": 3500,
        "temperature": 0.8,
    }

    # Send the request to Llama 3
    try:
        request = json.dumps(native_request)
        response = client.invoke_model(modelId=MODEL_ID, body=request)
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


