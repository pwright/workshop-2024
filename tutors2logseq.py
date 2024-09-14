#!/usr/bin/env python3

import os
import shutil
import argparse
import zipfile

# Function to create destination directories
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Function to flatten the directory structure by replacing '/' with '___' in filenames
def flatten_md_files(input_dir, output_dir):
    pages_dir = os.path.join(output_dir, 'pages')
    assets_dir = os.path.join(output_dir, 'assets')
    
    ensure_dir(pages_dir)
    ensure_dir(assets_dir)

    # Traverse the input directory for markdown and asset files
    for root, dirs, files in os.walk(input_dir):
        # Skip the output directory to avoid processing it
        if os.path.commonpath([output_dir, root]) == output_dir:
            print(f'Skipping output directory: {root}')
            continue

        for file in files:
            # Create a relative path to flatten
            relative_path = os.path.relpath(os.path.join(root, file), input_dir)
            
            if file.endswith('.md'):
                # Replace '/' in relative path with '___'
                flat_name = relative_path.replace(os.sep, '___')
                
                # New path for the markdown file in the pages directory
                dest_file_path = os.path.join(pages_dir, flat_name)
                
                # Ensure directory structure exists
                dest_file_dir = os.path.dirname(dest_file_path)
                ensure_dir(dest_file_dir)
                
                # Copy markdown file to the new directory with '___'
                shutil.copy2(os.path.join(root, file), dest_file_path)
                print(f'Moved {relative_path} -> {dest_file_path}')
            
            elif any(ext in file for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                # Handle assets (images, etc.)
                asset_dest_path = os.path.join(assets_dir, file)
                shutil.copy2(os.path.join(root, file), asset_dest_path)
                print(f'Moved asset {file} -> {asset_dest_path}')

# Function to handle input and output directories
def handle_input_output(input_dir, output_dir):
    # If input is the current directory, ignore output directory when parsing input
    if input_dir == '.':
        print(f'Input directory is current directory. Ignoring {output_dir} for input parsing.')
        input_dir = os.getcwd()  # Set input to current working directory
    else:
        # Use the provided input directory
        input_dir = os.path.abspath(input_dir)
    
    # Make sure output directory is absolute
    output_dir = os.path.abspath(output_dir)

    return input_dir, output_dir

# Function to extract ZIP file (if needed)
def extract_zip(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# Main function to process the command-line arguments
def main():
    parser = argparse.ArgumentParser(description='Flatten files with / to ___ to create a flat Logseq folder structure.')
    parser.add_argument('input_dir', type=str, help='Input directory or ZIP file containing the hierarchical structure.')
    parser.add_argument('output_dir', type=str, help='Output directory for the flattened Logseq folder structure.')

    args = parser.parse_args()

    input_dir, output_dir = handle_input_output(args.input_dir, args.output_dir)

    # Check if the input is a ZIP file
    if input_dir.endswith('.zip'):
        # Extract ZIP file to a temporary location
        tmp_dir = os.path.join(output_dir, 'tmp')
        extract_zip(input_dir, tmp_dir)
        input_dir = tmp_dir

    # Flatten the markdown files and assets to the destination
    flatten_md_files(input_dir, output_dir)

    # Clean up temporary files if zip was extracted
    if 'tmp_dir' in locals():
        shutil.rmtree(tmp_dir)
        print('Temporary files cleaned up.')

    print('Process completed successfully.')

if __name__ == '__main__':
    main()
