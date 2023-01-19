TOKEN= 'MTA1NDc3NDE5NzkyODMzNzQzOQ.G3WugQ.r_Ph0t5SJJG7TC2Ek9ga2bQDB2X5nBBhLU9RZo'

import discord
import requests
import random
from typing import List, Dict
rhyme_endpoint = "https://api.datamuse.com/words"
file_name = "3000_words_no_spaces.txt"
 
intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)

import tracemalloc
tracemalloc.start()
 
with open(file_name, "r") as f:
    english_lower_list = []
    for line in f:
        stripped_line = line.strip()
        english_lower_list.append(stripped_line)

PARAM_CODES = [   
    "rhy",
    "nry", 
    "hom",
    "cns",
]

SCORES = {
    "rhy" : 50,
    "nry" : 25,
    "hom" : 15,
    "cns" : 10,
}

CODE_TO_NAME_MAPPING = {
    "rhy" : "Perfect Rhyme",
    "nry" : "Near Rhyme", 
    "hom" : "Homonym",
    "cns" : "Consonant Swap",
}

def get_request_json(word:str,param:str):
        payload = {f"rel_{param}" : word}
        response = requests.get(rhyme_endpoint, params=payload)
        return response.json()

def create_rhyme_results_list_of_dict(chosen_words : List[str]) -> List[Dict[str,List[Dict]]]:
        list_of_output_dicts = []
        for chosen_word in chosen_words:
            #preprocessing
            output_dict = {}
            for code in PARAM_CODES:
                output_dict[code] = get_request_json(chosen_word,code) # Dict[List[Dict]]
            list_of_output_dicts.append(output_dict)
        return list_of_output_dicts

# TODO: make parallel calls 
def check_matches(user_guess : str, list_of_results_of_different_codes: Dict[str,List[Dict]]) -> Dict:
    matches = {}
    for code in PARAM_CODES:
        res = list(filter(lambda entry: entry['word'] == user_guess, list_of_results_of_different_codes[code]))
        exists = bool(res)
        if exists:
            matches[code] = res[0]
        else:
            matches[code] = {}
    return matches

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    
    # TODO: Optimization- on the game setup we pick the words

    
    #return content of previous message
        

    # game iteration
    async def full_game_iteration(NUMBER_OF_WORDS):
        total_score = 0
        
        # finds n random words from a list
        chosen_words = random.sample(english_lower_list,NUMBER_OF_WORDS)
        list_of_output_dicts = create_rhyme_results_list_of_dict(chosen_words)
        for level,chosen_word in enumerate(chosen_words):
            guess=None #random value that won't rhyme with anything
            # asks user to input a word that rhymes
            displayword = chosen_word.replace("_"," ")
            await message.channel.send(f"Find a rhyme for \"{displayword}\": ")
            while guess is None:  
                async for prev in message.channel.history(limit=1):
                    if (prev.author == message.author):
                        guess=prev.content
                
            if guess=="!exit":
                await message.channel.send ("Exiting game")
                return
            #check for 2nd start
            if guess=="!start":
                await message.channel.send ("Can't start another game")
                guess="start"
            


            # find the words that rhy nry hom cns
            # look for the user input inside of these and determine score
            res = check_matches(guess,list_of_output_dicts[level])

            # determine score
            first_matched_type = [k for k, v in res.items() if v]
            if first_matched_type:
                score_for_level = SCORES[first_matched_type[0]]
                #update total score
                total_score += score_for_level * res[first_matched_type[0]]['numSyllables']

                await message.channel.send(f"""\
                Your guess: {guess}
                Type: {CODE_TO_NAME_MAPPING[first_matched_type[0]]}
                Score: {score_for_level} * {res[first_matched_type[0]]['numSyllables']} Syllable
                Total Score: {total_score}""")
            else:
                await message.channel.send(f"""\
                Your guess: {guess}
                Type: NO MATCH
                Score: 0
                Total Score: {total_score}""")

        await message.channel.send(f""" 
                Game of {N} words ended
                ========Scores:========
                User: {total_score}
                                        """)
     

    # start command
    if message.content.startswith("!start"):
            await message.channel.send(f"Enter game length")
            
            N = None
            while N is None:  
                async for prev in message.channel.history(limit=1):
                    if (prev.author == message.author and int(prev.content)<=50):
                        N=int(prev.content)
            
            await message.channel.send(f"Setting up game for {N} words...")
            await full_game_iteration(N)
            
    

    
    
    
    
client.run(TOKEN)
