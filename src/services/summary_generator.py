import json
import re

class SummaryGenerator:
    def __init__(self):
        pass
        
    def generate_summary(self, model_response):
        """
        Process the model response and extract the summary and recommendations
        
        Args:
            model_response (str): The raw response from the GenAI model
            
        Returns:
            dict: A dictionary containing the parsed summary and recommendations
        """
        try:
            # Try to extract JSON from the response
            json_data = self._extract_json(model_response)
            
            if json_data:
                # Successfully parsed JSON
                return {
                    'summary': json_data.get('summary', 'No summary provided'),
                    'key_metrics': json_data.get('key_metrics', []),
                    'statistical_significance': json_data.get('statistical_significance', 'Not specified'),
                    'recommendations': json_data.get('recommendations', []),
                    'limitations': json_data.get('limitations', []),
                    'raw_response': model_response
                }
            else:
                # Fallback to text parsing if JSON extraction fails
                return self._parse_text_response(model_response)
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {
                'summary': 'Error processing model response',
                'key_metrics': [],
                'statistical_significance': 'Error',
                'recommendations': ['Please try again with different instructions'],
                'limitations': ['Error in processing model response'],
                'raw_response': model_response
            }
    
    def _extract_json(self, text):
        """
        Extract JSON from the model response
        """
        # Try to find JSON in the response using regex
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without the markdown code block
            json_match = re.search(r'(\{[\s\S]*\})', text)
            if json_match:
                json_str = json_match.group(1)
            else:
                return None
                
        try:
            # Parse the JSON string
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    
    def _parse_text_response(self, text):
        """
        Parse the text response if JSON extraction fails
        """
        # Simple heuristic parsing for text responses
        lines = text.split('\n')
        
        summary = []
        recommendations = []
        limitations = []
        key_metrics = []
        significance = "Not specified"
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to identify sections
            lower_line = line.lower()
            if 'summary' in lower_line and len(line) < 30:
                current_section = 'summary'
                continue
            elif any(x in lower_line for x in ['recommend', 'action', 'next step']) and len(line) < 30:
                current_section = 'recommendations'
                continue
            elif any(x in lower_line for x in ['limitation', 'caveat', 'constraint']) and len(line) < 30:
                current_section = 'limitations'
                continue
            elif any(x in lower_line for x in ['metric', 'measure', 'kpi']) and len(line) < 30:
                current_section = 'metrics'
                continue
            elif any(x in lower_line for x in ['significance', 'confidence', 'p-value', 'p value']) and len(line) < 50:
                if 'statistical_significance' not in lower_line:  # Avoid capturing the JSON key itself
                    significance = line
                    continue
            
            # Add content to the appropriate section
            if current_section == 'summary':
                summary.append(line)
            elif current_section == 'recommendations':
                if line.startswith('- ') or line.startswith('* '):
                    recommendations.append(line[2:])
                elif line[0].isdigit() and line[1] in ['.', ')']:
                    recommendations.append(line[2:].strip())
                else:
                    recommendations.append(line)
            elif current_section == 'limitations':
                if line.startswith('- ') or line.startswith('* '):
                    limitations.append(line[2:])
                elif line[0].isdigit() and line[1] in ['.', ')']:
                    limitations.append(line[2:].strip())
                else:
                    limitations.append(line)
            elif current_section == 'metrics':
                if line.startswith('- ') or line.startswith('* '):
                    key_metrics.append({'metric_name': line[2:], 'value': 'N/A', 'interpretation': 'N/A'})
                elif line[0].isdigit() and line[1] in ['.', ')']:
                    key_metrics.append({'metric_name': line[2:].strip(), 'value': 'N/A', 'interpretation': 'N/A'})
                else:
                    key_metrics.append({'metric_name': line, 'value': 'N/A', 'interpretation': 'N/A'})
        
        return {
            'summary': ' '.join(summary) if summary else 'No summary extracted',
            'key_metrics': key_metrics,
            'statistical_significance': significance,
            'recommendations': recommendations if recommendations else ['No specific recommendations extracted'],
            'limitations': limitations,
            'raw_response': text
        }
