import os
import requests
import json

# Hugging Face API URL and headers
API_URL = "https://api-inference.huggingface.co/models/meta-llama/LLaMA-2-70b-chat-hf"  # Adjust for LLaMA or Claude
HEADERS = {
    "Authorization": f"Bearer {os.getenv('HUGGING_FACE_API_KEY')}"
}

def correct_code_with_huggingface(code):
    # Prepare the payload for Hugging Face's Inference API
    prompt = f"Review the following code and correct any issues or inefficiencies:\n\n{code}\n\n"

    data = {
        "inputs": prompt
    }

    # Send the request to Hugging Face Inference API
    response = requests.post(API_URL, headers=HEADERS, json=data)

    # Check the response
    if response.status_code == 200:
        corrected_code = response.json()[0]['generated_text']
        return corrected_code
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def analyze_and_correct_code():
    # Load the code from the file
    with open('src/main/java/com/shipmentEvents/handlers/EventHandler.java', 'r') as file:
        code = file.read()

    # Get the corrected code from Hugging Face
    corrected_code = correct_code_with_huggingface(code)

    # Save the corrected code back to the file
    if corrected_code and corrected_code != code:
        with open('src/main/java/com/shipmentEvents/handlers/EventHandler.java', 'w') as file:
            file.write(corrected_code)
        print("Corrected code written back to the file.")
    else:
        print("No corrections were made.")

if __name__ == "__main__":
    analyze_and_correct_code()



