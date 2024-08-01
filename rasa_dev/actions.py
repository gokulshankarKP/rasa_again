from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType
import openai

import pandas as pd
import requests
import os
from  dotenv import load_dotenv, find_dotenv
find_dotenv()
load_dotenv()
import boto3
import numpy as np
import json
import ast
from tqdm import tqdm
import time
import string

#############################################################################################################################################################################################################
#############################################################################################################################################################################################################
#############################################################################################################################################################################################################
#############################################################################################################################################################################################################

class ActionCheckAge(Action):
    def name(self) -> Text:
        return "action_check_age"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global age
        recipe = pd.read_csv(r"recipe.csv", encoding = 'latin-1')
        recipe['age'] = recipe['age'].astype(str)
        age_list = recipe['age'].to_list()
        age = str(tracker.get_slot("age"))
        age_is_valid = age in age_list
        return [SlotSet("age_is_valid", age_is_valid)]



class ActionGetRecipe(Action):
    def name(self) -> Text:
        return "action_get_recipe"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        food_category = str(tracker.get_slot("food_category"))
        lactose_intolerant = tracker.get_slot("lactose_intolerant")
        recipe = pd.read_csv(r"recipe.csv", encoding = 'latin-1')
        print(lactose_intolerant)


        recipe = recipe[(recipe['age'] == age) & (recipe['lacto'] == lactose_intolerant) & (recipe['categories'] == food_category)]
        #recommended_recipe = recipe['description'].iloc[0]
        print(recipe)

        all_text = recipe.to_string()

        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {
                    "role": "system", 
                    "content": "You are an assistant that rephrases sentences."
                },
                {
                    "role": "user", 
                    "content": "Rephrase the following recipe as you are explaining stepwise. \nExample: \nRecommended Recipe: Pineapple Cucumber Cooler\nDescription: Pineapple Cucumber Cooler is a cooling, wonderful summertime beverage made with fresh cucumbers & pineapple. It is a tasty, flavourful & is extremely easy to make.\n{all_text}"
                }
            ]

        #  messages=[
        #         {"role": "system", "content": "You are an assistant that rephrases sentences."},
        #         {"role": "user", "content": f"Rephrase the following recipe as you are explaining stepwise:you are going to suggest food for child with age of {age}  and the i need in {food_category} and lactose intolerance is {lactose_intolerant} with details of  '{all_text}'"}
        #     ]
            
        )
        rephrased_recipe = response['choices'][0]['message']['content']
        print(rephrased_recipe)
        recommended_recipe=rephrased_recipe
        return [SlotSet("recommended_recipe", recommended_recipe), SlotSet("rephrased_recipe", rephrased_recipe)]
    



