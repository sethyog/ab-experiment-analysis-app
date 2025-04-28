import os
import pandas as pd
import tempfile
from src.utils.file_handler import FileHandler

def test_field_descriptions():
    print("Testing field descriptions loading...")
    
    # Create test data
    test_csv_data = """metric,control,treatment,difference,p_value
conversion_rate,0.12,0.15,0.03,0.04
average_order_value,45.5,48.2,2.7,0.03
bounce_rate,0.35,0.32,-0.03,0.06
"""
    # Create a test file
    os.makedirs('test_uploads', exist_ok=True)
    with open('test_uploads/test.csv', 'w') as f:
        f.write(test_csv_data)
    
    # Create test field descriptions with different column names
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        temp_file.write("field_name,description\n")
        temp_file.write("conversion_rate,The percentage of users who completed a desired action\n")
        temp_file.write("p_value,The probability that the observed difference occurred by chance\n")
        temp_path_1 = temp_file.name
        
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        temp_file.write("Column,Description\n")
        temp_file.write("conversion_rate,The percentage of users who completed a desired action\n")
        temp_file.write("p_value,The probability that the observed difference occurred by chance\n")
        temp_path_2 = temp_file.name
        
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        temp_file.write("FieldName,FieldDescription\n")
        temp_file.write("conversion_rate,The percentage of users who completed a desired action\n")
        temp_file.write("p_value,The probability that the observed difference occurred by chance\n")
        temp_path_3 = temp_file.name
    
    try:
        # Test with field_name,description format
        print("\nTesting with field_name,description format:")
        file_handler_1 = FileHandler(upload_folder='test_uploads', descriptions_path=temp_path_1)
        df = pd.read_csv('test_uploads/test.csv')
        descriptions_1 = file_handler_1.get_field_descriptions(df)
        print(f"Found descriptions: {descriptions_1}")
        
        # Test with Column,Description format
        print("\nTesting with Column,Description format:")
        file_handler_2 = FileHandler(upload_folder='test_uploads', descriptions_path=temp_path_2)
        descriptions_2 = file_handler_2.get_field_descriptions(df)
        print(f"Found descriptions: {descriptions_2}")
        
        # Test with custom column names
        print("\nTesting with custom column names (FieldName,FieldDescription):")
        file_handler_3 = FileHandler(upload_folder='test_uploads', descriptions_path=temp_path_3)
        descriptions_3 = file_handler_3.get_field_descriptions(df)
        print(f"Found descriptions: {descriptions_3}")
        
    finally:
        # Clean up
        if os.path.exists('test_uploads/test.csv'):
            os.remove('test_uploads/test.csv')
        if os.path.exists('test_uploads'):
            os.rmdir('test_uploads')
        if os.path.exists(temp_path_1):
            os.remove(temp_path_1)
        if os.path.exists(temp_path_2):
            os.remove(temp_path_2)
        if os.path.exists(temp_path_3):
            os.remove(temp_path_3)

if __name__ == "__main__":
    test_field_descriptions()