#!/usr/bin/env python3
"""
Re-parse JSON from existing Perplexity response
"""

import json
import sys

# Load the saved response
with open('outputs/flo_test/flo_health_full_response.json', 'r') as f:
    result = json.load(f)

# Extract content
content = result['choices'][0]['message']['content']

# Try to find JSON in code fence
if '```' in content:
    parts = content.split('```')
    markdown_section = parts[0].strip()

    for i, part in enumerate(parts[1:], 1):
        if i % 2 == 0:
            continue
        json_candidate = part.strip()
        if json_candidate.startswith('json'):
            json_candidate = json_candidate[4:].strip()

        try:
            if json_candidate.startswith('{'):
                json_section = json.loads(json_candidate)
                print('✅ Successfully extracted JSON!')
                print(f'Product: {json_section.get("product_name")}')
                print(f'Category: {json_section.get("category")}')

                # Save it
                with open('outputs/flo_test/flo_health_data.json', 'w') as f:
                    json.dump(json_section, f, indent=2)
                print('✅ Saved to flo_health_data.json')
                break
        except json.JSONDecodeError as e:
            print(f'Failed to parse: {e}')
