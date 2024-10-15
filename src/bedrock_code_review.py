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

    # Debugging: print the recommendations loaded
    print(f"DEBUG: Recommendations loaded: {recommendations}")

    # Check if the 'RecommendationSummaries' key exists
    if 'RecommendationSummaries' not in recommendations:
        print("ERROR: 'RecommendationSummaries' key not found in CodeGuru results.")
        return

    # Process each recommendation and apply the fixes
    for rec in recommendations['RecommendationSummaries']:
        issue = rec['Description']
        file_path = rec['FilePath']
        start_line = rec['StartLine'] - 1  # zero-indexed for Python
        end_line = rec['EndLine'] - 1
        suggested_fix = rec.get('SuggestedFix', {}).get('Content', '')

        # Log the issue and the lines being fixed
        print(f"Fixing issue at lines {start_line + 1} to {end_line + 1} in {file_path}: {issue}")

        # Apply the fix by replacing the relevant lines if suggested fix is available
        if suggested_fix:
            code_lines[start_line:end_line + 1] = [suggested_fix + '\n']

    # Write the modified code back to the file
    with open(code_file, 'w') as f:
        f.writelines(code_lines)

# Main function
def main():
    # Ensure that the recommendations are read correctly
    recommendations = load_codeguru_results()

    # Define the path to the actual code file you want to modify
    code_file = 'src/main/java/com/shipmentEvents/handlers/EventHandler.java'

    # Apply fixes to the code file based on the recommendations
    apply_fixes_to_code(code_file, recommendations)

if __name__ == "__main__":
    main()


