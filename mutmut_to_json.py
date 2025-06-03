import json
import subprocess
import re
from typing import Dict, List

def parse_mutmut_results() -> Dict:
    # Run mutmut results and capture output
    result = subprocess.run(['mutmut', 'results'], capture_output=True, text=True)
    output = result.stdout

    # Initialize result dictionary
    data = {
        "survived": [],
        "killed": [],
        "timeout": [],
        "skipped": []
    }

    # Parse the output
    current_section = None
    current_file = None
    
    for line in output.split('\n'):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Check for section headers
        if line.startswith('Survived'):
            current_section = "survived"
            continue
        elif line.startswith('Killed'):
            current_section = "killed"
            continue
        elif line.startswith('Timeout'):
            current_section = "timeout"
            continue
        elif line.startswith('Skipped'):
            current_section = "skipped"
            continue
            
        # Check for file headers
        if line.startswith('----'):
            match = re.search(r'---- (.*?) \((.*?)\) ----', line)
            if match:
                current_file = {
                    "file": match.group(1),
                    "count": int(match.group(2)),
                    "mutations": []
                }
                data[current_section].append(current_file)
            continue
            
        # Parse mutation lines
        if current_file and line:
            # Split line into individual mutations
            mutations = line.split(',')
            for mutation in mutations:
                mutation = mutation.strip()
                if '-' in mutation:
                    # Handle ranges (e.g., "7-8")
                    start, end = map(int, mutation.split('-'))
                    for line_num in range(start, end + 1):
                        current_file["mutations"].append(line_num)
                else:
                    # Handle single line numbers
                    try:
                        line_num = int(mutation)
                        current_file["mutations"].append(line_num)
                    except ValueError:
                        continue

    return data

def main():
    # Parse mutmut results
    results = parse_mutmut_results()
    
    # Write to JSON file
    with open('mut.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    main() 