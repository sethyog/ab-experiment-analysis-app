# A/B Experiment Analysis Application

This project is designed to interpret statistical analysis produced from A/B experiments and generate summaries with recommended actions. It provides a web interface for users to upload CSV files containing statistical data, input specific instructions, and select a GenAI model for analysis.

## Features

- **Web Interface**: Users can upload statistical analysis in CSV format, provide instructions for specific elements in the analysis file, and choose the GenAI model to be used.
- **AWS Bedrock Integration**: The application utilizes AWS Bedrock to access the selected GenAI model for generating summaries based on the uploaded data and user instructions.
- **Dynamic Prompt Generation**: User instructions are converted into prompts suitable for the GenAI model, ensuring accurate and relevant responses.
- **Summary Generation**: The application processes the output from the GenAI model to create concise summaries and actionable recommendations.

## Project Structure

```
ab-experiment-analysis-app
├── src
│   ├── app.py                # Main entry point of the application
│   ├── services
│   │   ├── aws_bedrock.py    # Interactions with AWS Bedrock
│   │   ├── prompt_builder.py   # Converts user instructions into prompts
│   │   └── summary_generator.py # Generates summaries from model responses
│   ├── templates
│   │   └── index.html         # HTML template for the web interface
│   ├── static
│   │   ├── css
│   │   │   └── styles.css     # CSS styles for the web interface
│   │   └── js
│   │       └── scripts.js      # JavaScript for client-side functionality
│   └── utils
│       └── file_handler.py     # Utility functions for file handling
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
└── .gitignore                  # Files to ignore in version control
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ab-experiment-analysis-app.git
   cd ab-experiment-analysis-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/app.py
   ```

4. Access the web interface at `http://localhost:5000`.

## Usage Guidelines

- Upload your statistical analysis CSV file using the provided interface.
- Enter specific instructions for the analysis in the text input field.
- Select the desired GenAI model from the dropdown menu.
- Submit the form to generate a summary and recommended actions based on the analysis.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.