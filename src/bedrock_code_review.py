import os
import json
import boto3

# Load the CodeGuru recommendations from codeguru_results.json
def load_codeguru_results():
    with open('codeguru_results.json', 'r') as f:
        recommendations = json.load(f)
    return recommendations

# Function to apply fixes to the code file based on recommendations
def apply_fixes_to_code(code_file, recommendations):
    # Read the original code
    with open(code_file, 'r') as f:
        code_lines = f.readlines()

    # Process recommendations and apply fixes
    for rec in recommendations['recommendations']:
        issue = rec['description']  # e.g., the description of the issue
        location = rec['filePath']  # path to the file
        start_line = rec['startLine'] - 1  # code line where issue is
        end_line = rec['endLine'] - 1  # end line of the issue
        suggested_fix = rec['suggestedFixes'][0]['content']

        # Log the issue and suggested fix
        print(f"Fixing issue at {start_line + 1} to {end_line + 1}: {issue}")

        # Apply the fix by replacing the relevant lines
        code_lines[start_line:end_line + 1] = [suggested_fix + '\n']

    # Write the modified code back to the file
    with open(code_file, 'w') as f:
        f.writelines(code_lines)

# Main function
def main():
    # Ensure that the recommendations are read correctly
    recommendations = load_codeguru_results()
    
    # Define the path to the code file
    code_file = 'src/main/java/com/shipmentEvents/handlers/EventHandler.java'

    # Apply fixes to the code file based on the recommendations
    apply_fixes_to_code(code_file, recommendations)

if __name__ == "__main__":
    main()

