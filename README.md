# A/B Experiment Analysis Application

This project is designed to interpret statistical analysis produced from A/B experiments and generate summaries with recommended actions. It provides a web interface for users to upload CSV files containing statistical data, input specific instructions, and select a GenAI model for analysis.

## Features

- **Web Interface**: Users can upload statistical analysis in CSV format, provide instructions for specific elements in the analysis file, and choose the GenAI model to be used.
- **AWS Bedrock Integration**: The application utilizes AWS Bedrock to access the selected GenAI model for generating summaries based on the uploaded data and user instructions.
- **Dynamic Prompt Generation**: User instructions are converted into prompts suitable for the GenAI model, ensuring accurate and relevant responses.
- **Summary Generation**: The application processes the output from the GenAI model to create concise summaries and actionable recommendations.
- **Field Descriptions**: The application loads descriptions of experiment fields from a CSV file and uses them to provide context for the analysis.

## Project Structure

```
ab-experiment-analysis-app
├── src
│   ├── app.py                # Main entry point of the application
│   ├── test_app.py           # Unit tests for the application
│   ├── services
│   │   ├── aws_bedrock.py    # Interactions with AWS Bedrock
│   │   ├── prompt_builder.py   # Converts user instructions into prompts
│   │   └── summary_generator.py # Generates summaries from model responses
│   ├── templates
│   │   └── index.html         # HTML template for the web interface
│   ├── static
│   │   ├── css
│   │   │   └── styles.css     # CSS styles for the web interface
│   │   ├── js
│   │   │   └── scripts.js      # JavaScript for client-side functionality
│   │   └── field_descriptions.csv # CSV file containing field descriptions
│   └── utils
│       └── file_handler.py     # Utility functions for file handling
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
└── uploads                     # Directory for uploaded files (created at runtime)
```

## Prerequisites

1. Python 3.8 or higher
2. AWS account with access to AWS Bedrock service
3. AWS credentials configured on your machine

## AWS Credentials Setup

Before running the application, make sure you have AWS credentials configured:

1. Install the AWS CLI:
   ```
   pip install awscli
   ```

2. Configure your AWS credentials:
   ```
   aws configure
   ```
   
   Enter your AWS Access Key ID, Secret Access Key, default region (e.g., us-west-2), and output format (json).

3. Ensure your AWS account has access to AWS Bedrock and the models you want to use.

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ab-experiment-analysis-app.git
   cd ab-experiment-analysis-app
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python src/app.py
   ```

5. Access the web interface at `http://localhost:5000`.touch src/__init__.py
touch src/services/__init__.py


## Running on an EC2 Instance

To run this application on an EC2 instance:

1. Connect to your EC2 instance via SSH.

2. Clone the repository and install dependencies as described above.

3. Configure your AWS credentials on the EC2 instance.

4. Start the application with Gunicorn (included in requirements.txt):
   ```
   cd ab-experiment-analysis-app
   gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 src.app:app
   
   ```

5. Access the application using your EC2 instance's public IP or domain name: `http://your-ec2-ip:5000`.

## CSV File Format

The application accepts CSV files containing A/B test results. The recommended format is:

```
metric,control,treatment,difference,p_value
conversion_rate,0.12,0.15,0.03,0.04
average_order_value,45.5,48.2,2.7,0.03
bounce_rate,0.35,0.32,-0.03,0.06
```

However, the application can also handle other CSV formats containing statistical data.

## Field Descriptions CSV

The application uses a CSV file to load descriptions of experiment fields. The file is located at `src/static/field_descriptions.csv` and has the following format:

```
field_name,description
metric,The name of the metric being measured in the experiment
control,The value of the metric in the control group (baseline)
treatment,The value of the metric in the treatment group (variant being tested)
difference,The absolute difference between the treatment and control values
p_value,The probability that the observed difference occurred by chance (lower values indicate higher statistical significance)
conversion_rate,The percentage of users who completed a desired action (e.g., made a purchase)
...
```

You can add or modify field descriptions in this file to provide more context for the analysis.

## Usage Guidelines

1. Upload your statistical analysis CSV file using the provided interface.
2. Select the desired GenAI model from the dropdown menu.
3. Enter specific instructions for the analysis in the text input field.
4. Click "Analyze Data" to generate a summary and recommended actions based on the analysis.
5. Review the results, which include:
   - A summary of the A/B test results
   - Key metrics and their interpretation
   - Statistical significance assessment
   - Recommended actions
   - Limitations of the analysis

## Running Tests

To run the unit tests:

```
cd ab-experiment-analysis-app
python -m unittest src.test_app
```

## Troubleshooting

- **AWS Credentials Issues**: Ensure your AWS credentials are correctly configured and have access to AWS Bedrock.
- **Model Access**: Verify that your AWS account has access to the selected models in AWS Bedrock.
- **CSV Format Errors**: Check that your CSV file contains numeric data and follows a supported format.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.



