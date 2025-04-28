import os
import json
import pandas as pd
from typing import List, Dict, Any, Optional
import random

class ExampleManager:
    """
    Service for managing example data and analyses for few-shot learning
    """
    def __init__(self, examples_dir: str = 'src/examples'):
        """
        Initialize the ExampleManager with the path to the examples directory
        
        Args:
            examples_dir (str): Path to the directory containing examples
        """
        self.examples_dir = examples_dir
        self.data_dir = os.path.join(examples_dir, 'data')
        self.analyses_dir = os.path.join(examples_dir, 'analyses')
        self.metadata_path = os.path.join(examples_dir, 'metadata.json')
        self.examples = self._load_metadata()
        
    def _load_metadata(self) -> List[Dict[str, Any]]:
        """
        Load example metadata from the metadata.json file
        
        Returns:
            List[Dict[str, Any]]: List of example metadata
        """
        try:
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'r') as f:
                    metadata = json.load(f)
                return metadata.get('examples', [])
            else:
                print(f"Warning: Example metadata file not found at {self.metadata_path}")
                return []
        except Exception as e:
            print(f"Error loading example metadata: {str(e)}")
            return []
            
    def get_all_examples(self) -> List[Dict[str, Any]]:
        """
        Get all available examples
        
        Returns:
            List[Dict[str, Any]]: List of all examples with metadata
        """
        return self.examples
        
    def get_example_data(self, example_id: str) -> Optional[pd.DataFrame]:
        """
        Get the data for a specific example
        
        Args:
            example_id (str): ID of the example
            
        Returns:
            Optional[pd.DataFrame]: DataFrame containing the example data, or None if not found
        """
        example = next((e for e in self.examples if e['id'] == example_id), None)
        if not example:
            return None
            
        data_path = os.path.join(self.data_dir, example['data_file'])
        try:
            if os.path.exists(data_path):
                return pd.read_csv(data_path)
            else:
                print(f"Warning: Example data file not found at {data_path}")
                return None
        except Exception as e:
            print(f"Error loading example data: {str(e)}")
            return None
            
    def get_example_analysis(self, example_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the analysis for a specific example
        
        Args:
            example_id (str): ID of the example
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary containing the example analysis, or None if not found
        """
        example = next((e for e in self.examples if e['id'] == example_id), None)
        if not example:
            return None
            
        analysis_path = os.path.join(self.analyses_dir, example['analysis_file'])
        try:
            if os.path.exists(analysis_path):
                with open(analysis_path, 'r') as f:
                    return json.load(f)
            else:
                print(f"Warning: Example analysis file not found at {analysis_path}")
                return None
        except Exception as e:
            print(f"Error loading example analysis: {str(e)}")
            return None
            
    def select_examples(self, data_df: pd.DataFrame, max_examples: int = 2) -> List[Dict[str, Any]]:
        """
        Select relevant examples based on the input data
        
        Args:
            data_df (pd.DataFrame): DataFrame containing the input data
            max_examples (int): Maximum number of examples to select
            
        Returns:
            List[Dict[str, Any]]: List of selected examples with their data and analyses
        """
        # Get the metrics in the input data
        if 'metric' in data_df.columns:
            input_metrics = set(data_df['metric'].unique())
        else:
            input_metrics = set(data_df.columns)
            
        # Score examples based on metric overlap
        scored_examples = []
        for example in self.examples:
            example_metrics = set(example.get('metrics', []))
            if not example_metrics:
                # If no metrics specified, use all examples
                score = 0.5
            else:
                # Calculate Jaccard similarity between input metrics and example metrics
                intersection = len(input_metrics.intersection(example_metrics))
                union = len(input_metrics.union(example_metrics))
                score = intersection / union if union > 0 else 0
                
            scored_examples.append((example, score))
            
        # Sort examples by score (descending)
        scored_examples.sort(key=lambda x: x[1], reverse=True)
        
        # Select top examples
        selected_examples = []
        for example, score in scored_examples[:max_examples]:
            example_data = self.get_example_data(example['id'])
            example_analysis = self.get_example_analysis(example['id'])
            
            if example_data is not None and example_analysis is not None:
                selected_examples.append({
                    'metadata': example,
                    'data': example_data,
                    'analysis': example_analysis,
                    'relevance_score': score
                })
                
        return selected_examples
        
    def get_random_examples(self, max_examples: int = 2) -> List[Dict[str, Any]]:
        """
        Get random examples for cases where we can't determine relevance
        
        Args:
            max_examples (int): Maximum number of examples to select
            
        Returns:
            List[Dict[str, Any]]: List of randomly selected examples with their data and analyses
        """
        if not self.examples:
            return []
            
        # Randomly select examples
        selected_ids = random.sample([e['id'] for e in self.examples], min(max_examples, len(self.examples)))
        
        selected_examples = []
        for example_id in selected_ids:
            example = next((e for e in self.examples if e['id'] == example_id), None)
            example_data = self.get_example_data(example_id)
            example_analysis = self.get_example_analysis(example_id)
            
            if example is not None and example_data is not None and example_analysis is not None:
                selected_examples.append({
                    'metadata': example,
                    'data': example_data,
                    'analysis': example_analysis,
                    'relevance_score': 0.5  # Default score for random selection
                })
                
        return selected_examples
        
    def format_example_for_prompt(self, example: Dict[str, Any]) -> str:
        """
        Format an example for inclusion in a prompt
        
        Args:
            example (Dict[str, Any]): Example with metadata, data, and analysis
            
        Returns:
            str: Formatted example string for the prompt
        """
        metadata = example['metadata']
        data_df = example['data']
        analysis = example['analysis']
        
        # Format the data as a string
        data_str = data_df.to_string(index=False)
        
        # Format the analysis as a string
        analysis_str = json.dumps(analysis, indent=2)
        
        # Combine into a formatted example
        formatted_example = f"""
## EXAMPLE: {metadata['name']}
### DATA:
{data_str}

### ANALYSIS:
{analysis_str}
"""
        return formatted_example