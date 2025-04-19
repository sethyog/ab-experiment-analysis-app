from flask import Flask, request, render_template
from services.aws_bedrock import get_model_response
from services.prompt_builder import build_prompt
from services.summary_generator import generate_summary
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        csv_file = request.files['csv_file']
        instructions = request.form['instructions']
        model_name = request.form['model_name']

        if csv_file:
            df = pd.read_csv(csv_file)
            prompt = build_prompt(instructions, df)
            response = get_model_response(model_name, prompt)
            summary = generate_summary(response)

            return render_template('index.html', summary=summary)

    return render_template('index.html', summary=None)

if __name__ == '__main__':
    app.run(debug=True)