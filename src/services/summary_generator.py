from langchain import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class SummaryGenerator:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.llm = OpenAI(model_name=model_name)

    def generate_summary(self, analysis_results: str, instructions: str) -> str:
        prompt = self.build_prompt(analysis_results, instructions)
        chain = LLMChain(llm=self.llm, prompt=PromptTemplate(template=prompt))
        summary = chain.run()
        return summary

    def build_prompt(self, analysis_results: str, instructions: str) -> str:
        return f"Based on the following A/B experiment analysis results:\n\n{analysis_results}\n\nPlease provide a summary and recommended actions considering the instructions: {instructions}"