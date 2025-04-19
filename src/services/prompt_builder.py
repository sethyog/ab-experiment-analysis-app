class PromptBuilder:
    def __init__(self, instructions):
        self.instructions = instructions

    def build_prompt(self, analysis_data):
        prompt = f"Based on the following statistical analysis data:\n{analysis_data}\n"
        prompt += f"Please consider the following instructions:\n{self.instructions}\n"
        prompt += "Generate a summary with recommended actions."
        return prompt

    def validate_instructions(self):
        if not self.instructions:
            raise ValueError("Instructions cannot be empty.")
        # Additional validation logic can be added here if needed.