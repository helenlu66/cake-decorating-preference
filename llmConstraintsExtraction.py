from pprint import pprint
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from ConfigUtil import get_args
from prompts import *
import os


class ConstraintExtractor:
    def __init__(self, prompts_setup:dict, task_setup:dict, api_key=os.environ['OPENAI_API_KEY'] if 'OPENAI_API_KEY' in os.environ else None) -> None:
        self.input_dict = {**prompts_setup, **task_setup}
        self.classifier = LLMChain(llm = OpenAI(openai_api_key=api_key, temperature=0), prompt=classification_prompt, output_key='classification')
        self.redirector = LLMChain(llm = OpenAI(openai_api_key=api_key, temperature=0), prompt=redirect_prompt, output_key='robot_response')
        self.constraints_extractor = LLMChain(llm = OpenAI(openai_api_key=api_key, temperature=0), prompt=constraints_extraction_prompt, output_key='constraints')
    
    def classify(self, robot_question:str, human_answer:str) -> bool:
        """takes in a human response and classify whether the ConstraintExtractor can handle this response

        Args:
            robot_question (str): the robot's question
            human_response (str): a human response to the robot's question

        Returns:
            either true or false
        """
        self.input_dict['robot_question'] = robot_question
        self.input_dict['human_answer'] = human_answer
        outputs = self.classifier(inputs=self.input_dict)
       
        if outputs['classification'].lower() == 'yes':
            return True
        return False
    
    def redirect(self, robot_question:str, human_answer:str) -> bool:
        """given a human answer that does not answer the robot question, respond in a way to redirect the human back to the task

        Args:
            robot_question (str): the robot's question
            human_response (str): a human response to the robot's question

        Returns:
            robot's response text
        """
        self.input_dict['robot_question'] = robot_question
        self.input_dict['human_answer'] = human_answer
        outputs = self.redirector(inputs=self.input_dict)
        return outputs['robot_response']
    
    def extract_constraints(self, robot_question:str, human_answer:str) -> list[str]:
        """takes in a human response and extracts a list of constraints

        Args:
            robot_question (str): the robot's question
            human_response (str): a human response to the robot's question

        Returns:
            list of constraints
        """
        self.input_dict['robot_question'] = robot_question
        self.input_dict['human_answer'] = human_answer
        outputs = self.constraints_extractor(inputs=self.input_dict)
        constraints_list = outputs['constraints'].split(',')
        return constraints_list
        

if __name__=="__main__":
    args = get_args()
    constraint_extractor = ConstraintExtractor(prompts_setup=prompts_setup, task_setup={
        'surface_width':20,
        'surface_len':20
    }, api_key=args.api_key if args.api_key else os.environ['OPENAI_API_KEY'])
    #pprint(constraint_extractor.classify(robot_question='Where should I put the first candle?', human_answer='I do not know. Can you give me some example locations?'))
    pprint(constraint_extractor.redirect(robot_question='Where should I put the first candle?', human_answer='I do not know. Why are you asking me?'))
    #pprint(constraint_extractor.extract_constraints(robot_question='Where should I put the first candle?', human_answer='Put it on the left side of the cake.'))

