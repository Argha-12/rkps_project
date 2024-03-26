import os
import shutil

def download_pdfs(input_folder, output_folder, task_id):
    # Iterate through files in the input folder
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(".pdf"):
                # Extract the first 13 numbers from the filename
                extracted_task_id = file[:13]

                # Check if the extracted task_id matches the provided task_id
                if extracted_task_id == task_id:
                    # Move the PDF file to the output folder
                    shutil.move(os.path.join(root, file), os.path.join(output_folder, file))
                    print(f"Downloaded {file} successfully for task_id {task_id}.")
                    return  # Exit after downloading the first matching PDF file

    # If no matching PDF file found
    print(f"No PDF file found for task_id {task_id} in the input folder.")

# Example usage:
# Example usage:
input_folder = "C:\\Users\\argha\\Desktop\\input"  # Escaping backslashes
output_folder = "C:\\Users\\argha\\Desktop\\output"  # Escaping backslashes
task_id = "1709888419108"  # Provide the first 13 digits of the task_id
download_pdfs(input_folder, output_folder, task_id)




