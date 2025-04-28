import os
import pandas as pd
from werkzeug.utils import secure_filename

class FileHandler:
    def __init__(self, upload_folder='uploads', descriptions_path='src/static/field_descriptions.csv'):
        """
        Initialize the FileHandler with the upload folder path and descriptions file path
        
        Args:
            upload_folder (str): Path to the folder where uploaded files will be stored
            descriptions_path (str): Path to the CSV file containing field descriptions
        """
        self.upload_folder = upload_folder
        self.descriptions_path = descriptions_path
        self.field_descriptions = self._load_field_descriptions()
        self._ensure_upload_folder_exists()
        
    def _ensure_upload_folder_exists(self):
        """
        Create the upload folder if it doesn't exist
        """
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
            
    def _load_field_descriptions(self):
        """
        Load field descriptions from the CSV file
        
        Returns:
            dict: A dictionary mapping field names to their descriptions
        """
        try:
            if os.path.exists(self.descriptions_path):
                df = pd.read_csv(self.descriptions_path)
                
                # Check if the dataframe has at least two columns
                if len(df.columns) >= 2:
                    # Use the first column for field names and the second column for descriptions
                    field_name_col = df.columns[0]
                    description_col = df.columns[1]
                    
                    return dict(zip(df[field_name_col], df[description_col]))
                else:
                    print(f"Warning: Field descriptions file must have at least two columns")
                    return {}
            else:
                print(f"Warning: Field descriptions file not found at {self.descriptions_path}")
                return {}
        except Exception as e:
            print(f"Error loading field descriptions: {str(e)}")
            return {}
            
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
            
    def get_field_descriptions(self, df):
        """
        Get descriptions for the fields in the DataFrame
        
        Args:
            df (pandas.DataFrame): The DataFrame containing experiment data
            
        Returns:
            dict: A dictionary mapping field names to their descriptions
        """
        descriptions = {}
        for column in df.columns:
            if column in self.field_descriptions:
                descriptions[column] = self.field_descriptions[column]
            
        # Also include descriptions for any values in the 'metric' column if it exists
        if 'metric' in df.columns:
            for metric in df['metric'].unique():
                if metric in self.field_descriptions:
                    descriptions[metric] = self.field_descriptions[metric]
                    
        return descriptions
        
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





