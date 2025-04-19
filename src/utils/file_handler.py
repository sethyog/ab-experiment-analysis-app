def upload_file(file):
    # Function to handle file upload
    if file and file.filename.endswith('.csv'):
        file_path = f"uploads/{file.filename}"
        file.save(file_path)
        return file_path
    else:
        raise ValueError("Invalid file format. Please upload a CSV file.")

def read_csv(file_path):
    # Function to read a CSV file and return its contents
    import pandas as pd
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        raise ValueError(f"Error reading the CSV file: {e}")

def process_data(data):
    # Function to process the data for analysis
    # Placeholder for data processing logic
    processed_data = data.describe()  # Example: returning summary statistics
    return processed_data