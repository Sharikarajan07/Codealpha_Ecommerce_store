#!/usr/bin/env python3
"""
Script to fix the initial_data.json file by adding missing created_at and updated_at fields
"""
import json
import os

def fix_initial_data():
    # Read the current initial_data.json
    with open('initial_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Fixed timestamp for all entries
    timestamp = "2025-08-19T00:00:00Z"
    
    # Process each item in the data
    for item in data:
        model = item.get('model', '')
        
        # Add timestamps for Category and Product models
        if model in ['store.category', 'store.product']:
            fields = item.get('fields', {})
            
            # Add created_at and updated_at if they don't exist
            if 'created_at' not in fields:
                fields['created_at'] = timestamp
            if 'updated_at' not in fields:
                fields['updated_at'] = timestamp
    
    # Write the updated data back to the file
    with open('initial_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Successfully updated initial_data.json with created_at and updated_at fields")

if __name__ == '__main__':
    fix_initial_data()
