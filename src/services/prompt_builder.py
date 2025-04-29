import pandas as pd
import json
from typing import List, Dict, Any, Optional

class PromptBuilder:
    def __init__(self):
        pass
        
    def build_prompt(self, instructions, data_df, field_descriptions=None, examples=None):
        """
        Build a prompt for the GenAI model based on the statistical data, field descriptions, and user instructions
        
        Args:
            instructions (str): User instructions for interpreting the data
            data_df (pandas.DataFrame): DataFrame containing the A/B experiment statistical data
            field_descriptions (dict, optional): Dictionary mapping field names to their descriptions
            examples (List[Dict[str, Any]], optional): List of examples to include in the prompt
            
        Returns:
            str: A formatted prompt for the GenAI model
        """
        # Convert DataFrame to a more readable format
        data_str = self._format_dataframe(data_df)
        
        # Format field descriptions if provided
        descriptions_str = ""
        if field_descriptions and len(field_descriptions) > 0:
            descriptions_str = "## FIELD DESCRIPTIONS:\n"
            for field, description in field_descriptions.items():
                descriptions_str += f"- {field}: {description}\n"
        
        # Format examples if provided
        examples_str = ""
        if examples and len(examples) > 0:
            examples_str = "## EXAMPLES OF GOOD ANALYSES:\n"
            for example in examples:
                examples_str += self._format_example(example)
        
        # Build the prompt with clear instructions for the model
        prompt = f"""
You are an expert data scientist specializing in A/B testing analysis. 
Your task is to analyze the following statistical output from an A/B experiment and provide a clear, actionable summary.

{examples_str}
## STATISTICAL DATA TO ANALYZE:
{data_str}

{descriptions_str}
## USER INSTRUCTIONS:
{instructions}

## REQUIRED OUTPUT FORMAT:
Please provide your analysis in the following JSON structure:
```json
{{
  "summary": "A concise summary of the A/B test results (2-3 paragraphs)",
  "key_metrics": [
    {{
      "metric_name": "Name of the metric",
      "impact range": "Confidence interval of impact percentage",
      "probability of impact >0": "Probability that the treatment is better than control",
      "annualized impact": "Estimated annualized impact of the metric",
      "interpretation": "What this metric means in context"
    }}
  ],
  "recommendations": [
    "Clear, actionable recommendation based on the results",
    "Additional recommendations if applicable"
  ],
  "limitations": [
    "Any limitations or caveats to consider"
  ]
}}
```

Ensure your analysis is data-driven, statistically sound, and provides clear business recommendations.
Use the field descriptions to provide more context and accurate interpretations of the metrics.
Learn from the examples provided to structure your analysis in a similar way.
"""
        return prompt
        
    def _format_example(self, example: Dict[str, Any]) -> str:
        """
        Format an example for inclusion in the prompt
        
        Args:
            example (Dict[str, Any]): Example with data and analysis
            
        Returns:
            str: Formatted example string
        """
        metadata = example.get('metadata', {})
        data_df = example.get('data')
        analysis = example.get('analysis', {})
        
        # Format the data
        data_str = self._format_dataframe(data_df)
        
        # Format the analysis
        analysis_str = json.dumps(analysis, indent=2)
        
        return f"""
### EXAMPLE: {metadata.get('name', 'A/B Test Example')}
#### DATA:
{data_str}

#### ANALYSIS:
```json
{analysis_str}
```

"""
        
    def _format_dataframe(self, df):
        """
        Format a DataFrame into a readable string representation
        """
        # Check if the DataFrame is empty
        if df.empty:
            return "No data provided"
            
        # Try to identify if this is a standard A/B test result format
        if all(col in df.columns for col in ['metric', 'control', 'treatment', 'difference', 'p_value']):
            # This looks like a standard A/B test result format
            return self._format_ab_test_results(df)
        elif all(col in df.columns for col in ['variable', 'coefficient', 'std_error', 't_value', 'p_value']):
            # This looks like a regression analysis output
            return self._format_regression_results(df)
        else:
            # Generic format for any DataFrame
            # Include descriptive statistics
            desc_stats = df.describe().to_string()
            
            # Include correlation matrix if there are numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            corr_matrix = ""
            if len(numeric_cols) > 1:
                corr_matrix = f"\n\nCorrelation Matrix:\n{df[numeric_cols].corr().to_string()}"
                
            # Include the first few rows of data
            data_sample = f"\n\nData Sample (first 5 rows):\n{df.head().to_string()}"
            
            return f"Descriptive Statistics:\n{desc_stats}{corr_matrix}{data_sample}"
    
    def _format_ab_test_results(self, df):
        """
        Format A/B test results in a readable way
        """
        result = "A/B Test Results:\n\n"
        
        # Format each row nicely
        for _, row in df.iterrows():
            metric = row.get('metric', 'Unknown Metric')
            control = row.get('control', 'N/A')
            treatment = row.get('treatment', 'N/A')
            diff = row.get('difference', 'N/A')
            p_val = row.get('p_value', 'N/A')
            
            # Format p-value with stars for significance
            sig_stars = ''
            if isinstance(p_val, (int, float)):
                if p_val < 0.001:
                    sig_stars = '***'
                elif p_val < 0.01:
                    sig_stars = '**'
                elif p_val < 0.05:
                    sig_stars = '*'
                p_val_str = f"{p_val:.4f}{sig_stars}"
            else:
                p_val_str = str(p_val)
            
            result += f"Metric: {metric}\n"
            result += f"  Control: {control}\n"
            result += f"  Treatment: {treatment}\n"
            result += f"  Difference: {diff}\n"
            result += f"  P-value: {p_val_str}\n\n"
            
        result += "Significance levels: * p<0.05, ** p<0.01, *** p<0.001"
        return result
        
    def _format_regression_results(self, df):
        """
        Format regression analysis results in a readable way
        """
        result = "Regression Analysis Results:\n\n"
        
        # Format each row nicely
        for _, row in df.iterrows():
            var = row.get('variable', 'Unknown Variable')
            coef = row.get('coefficient', 'N/A')
            std_err = row.get('std_error', 'N/A')
            t_val = row.get('t_value', 'N/A')
            p_val = row.get('p_value', 'N/A')
            
            # Format p-value with stars for significance
            sig_stars = ''
            if isinstance(p_val, (int, float)):
                if p_val < 0.001:
                    sig_stars = '***'
                elif p_val < 0.01:
                    sig_stars = '**'
                elif p_val < 0.05:
                    sig_stars = '*'
                p_val_str = f"{p_val:.4f}{sig_stars}"
            else:
                p_val_str = str(p_val)
            
            result += f"Variable: {var}\n"
            result += f"  Coefficient: {coef}\n"
            result += f"  Std Error: {std_err}\n"
            result += f"  t-value: {t_val}\n"
            result += f"  P-value: {p_val_str}\n\n"
            
        result += "Significance levels: * p<0.05, ** p<0.01, *** p<0.001"
        return result

