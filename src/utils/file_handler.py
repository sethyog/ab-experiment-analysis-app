import os
import pandas as pd
from werkzeug.utils import secure_filename

class FileHandler:
    def __init__(self, upload_folder='uploads'):
        """
        Initialize the FileHandler with the upload folder path
        
        Args:
            upload_folder (str): Path to the folder where uploaded files will be stored
        """
        self.upload_folder = upload_folder
        self._ensure_upload_folder_exists()
        
    def _ensure_upload_folder_exists(self):
        """
        Create the upload folder if it doesn't exist
        """
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
            
    def save_file(self, file):
        """
        Save an uploaded file to the upload folder
        
        Args:
            file: The file object from the request
            
        Returns:
            str: The path to the saved file
        """
        if not file:
            raise ValueError("No file provided")
            
        filename = secure_filename(file.filename)
        if not filename:
            raise ValueError("Invalid filename")
            
        if not self._is_csv_file(filename):
            raise ValueError("Only CSV files are allowed")
            
        file_path = os.path.join(self.upload_folder, filename)
        file.save(file_path)
        return file_path
        
    def _is_csv_file(self, filename):
        """
        Check if a file is a CSV file based on its extension
        
        Args:
            filename (str): The filename to check
            
        Returns:
            bool: True if the file is a CSV file, False otherwise
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'
        
    def read_csv(self, file_path):
        """
        Read a CSV file and return a pandas DataFrame
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            pandas.DataFrame: The data from the CSV file
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")
            
    def validate_csv_content(self, df):
        """
        Validate the content of a CSV file
        
        Args:
            df (pandas.DataFrame): The DataFrame to validate
            
        Returns:
            bool: True if the content is valid, False otherwise
        """
        # Check if the DataFrame is empty
        if df.empty:
            raise ValueError("The CSV file is empty")
            
        # Check if the DataFrame has at least one numeric column
        numeric_columns = df.select_dtypes(include=['number']).columns
        if len(numeric_columns) == 0:
            raise ValueError("The CSV file must contain at least one numeric column")
            
        return True
