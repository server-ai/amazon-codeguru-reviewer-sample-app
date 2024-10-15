import json
import boto3
import os

# Initialize AWS Bedrock client
bedrock_client = boto3.client('bedrock', region_name=os.getenv('AWS_REGION'))

# Load CodeGuru results
def load_codeguru_results(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Send prompt to Llama 3 and get the response
def get_llama3_suggestions(issue_description, code_snippet):
    prompt = f"Here is a code issue found by CodeGuru: {issue_description}. Here is the code:\n{code_snippet}\nHow can this be fixed?"
    
    response = bedrock_client.invoke_model(
        modelId='llama-3',
        body={
            'prompt': prompt,
            'maxTokens': 512
        }
    )
    
    return response['body']['text']

# Main function
def main(codeguru_results_path):
    # Load the CodeGuru results
    codeguru_results = load_codeguru_results(codeguru_results_path)

    for recommendation in codeguru_results.get('recommendations', []):
        issue = recommendation['recommendationSummary']
        code_snippet = recommendation['codeLine']
        
        # Get suggestions from Llama 3
        suggestion = get_llama3_suggestions(issue, code_snippet)
        
        print(f"CodeGuru issue: {issue}")
        print(f"Llama 3 suggestion: {suggestion}")
        
        # Here, implement logic to apply the suggestion back to the code files
        
        # Example: Write suggestion back to the file (this requires custom parsing and code modification logic)
        # with open(recommendation['filePath'], 'r+') as code_file:
        #     code = code_file.read()
        #     fixed_code = apply_suggestion(code, suggestion)  # Custom logic needed
        #     code_file.seek(0)
        #     code_file.write(fixed_code)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python bedrock_code_review.py <path_to_codeguru_results>")
        sys.exit(1)
    
    codeguru_results_path = sys.argv[1]
    main(codeguru_results_path)
