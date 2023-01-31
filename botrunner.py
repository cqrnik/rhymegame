
import discord
from discord.ext import commands
import requests
import random

import asyncio

from typing import List, Dict
rhyme_endpoint = "https://api.datamuse.com/words"
file_name = "3000_words_no_spaces.txt"
 
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

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


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))




    
# TODO: Optimization- on the game setup we pick the words


#exit game        
async def exitGame(message):
    await message.channel.send(f"Exiting game...") 
    return


# game iteration
async def full_game_iteration(NUMBER_OF_WORDS, message, players):
    scores=[]
    for i in players:
        scores.append(0)
    
    # finds n random words from a list
    chosen_words = random.sample(english_lower_list,(NUMBER_OF_WORDS*len(players)))
    list_of_output_dicts = create_rhyme_results_list_of_dict(chosen_words)
    for rounds in range(NUMBER_OF_WORDS): #loops for each round
        for level,chosen_word in enumerate(chosen_words): #level:
            for player in players: #loops for each player
            
                guess=None 
                # asks user to input a word that rhymes
                displayword = chosen_word.replace("_"," ")
                await message.channel.send(f"{player.mention}, Find a rhyme for \"{displayword}\": ")
                while guess is None:  
                    async for prev in message.channel.history(limit=1):
                        if (prev.author == player):
                            guess=prev.content
                    
                if guess=="!exit":
                    await exitGame(message)
                    return
                #check for 2nd start
                if guess=="!start":
                    await message.channel.send ("Can't start another game")
                    guess="start"
                


                # find the words that rhy nry hom cns
                # look for the user input inside of these and determine score
                res = check_matches(guess,list_of_output_dicts[level])
                player_score=scores[players.index(player)]

                # determine score
                first_matched_type = [k for k, v in res.items() if v]
                if first_matched_type:
                    score_for_level = SCORES[first_matched_type[0]]
                    #update total score
                    player_score += score_for_level * res[first_matched_type[0]]['numSyllables']

                    await message.channel.send(f"""\
                    {player.mention}'s guess: {guess}
                    Type: {CODE_TO_NAME_MAPPING[first_matched_type[0]]}
                    Score: {score_for_level} * {res[first_matched_type[0]]['numSyllables']} Syllable
                    Total Score: {player_score}""")
                else:
                    await message.channel.send(f"""\
                    Your guess: {guess}
                    Type: NO MATCH
                    Score: 0
                    Total Score: {player_score}""")
                scores[players.index(player)]=player_score

    await message.channel.send(f""" 
                    Game of {NUMBER_OF_WORDS} words ended
                    ========Scores:========
                    User: 
                                            """)        
    

     

#command start testing
@bot.command()
async def start(ctx):
    
    players = []

    message = await ctx.send(f"""\
                 Rhyme Game
                 React to join
             """)

    
    await message.add_reaction('✅')
    
    await asyncio.sleep(10) #10 second timer
    
    message = await ctx.fetch_message(message.id)

    for reaction in message.reactions:
        if reaction.emoji == '✅':
            async for user in reaction.users():
                if user != bot.user:
                    players.append(user)

    if len(players) < 1:
        await ctx.send('Time is up, and not enough players')
    else:
        await message.channel.send(f"Enter number of words")
        N=None
        while N is None:  
            async for prev in message.channel.history(limit=1):
                if (prev.author == ctx.message.author):
                    if (int(prev.content)<=50):
                        N=int(float(prev.content))
        await message.channel.send(f"Setting up game for {N} words...")
        await full_game_iteration(N, ctx, players)
   
    # # start command
    # if message.content.startswith("!start"):

    #         #create list of tuples for players in the game
    #         players= []
    #         gameRunning=True

    #         players.append({
    #             'user':message.author,
    #             'score':0
    #         })
    #         await message.channel.send(f"""\
    #             Rhyme Game
    #             !join to join the game
    #             !continue to finalize players
    #             !cancel to exit
    #         """)
    #         check=False
    #         while check==False:
    #             async for prev in message.channel.history(limit=1):
    #                 if (prev.content == "!join"):
    #                     if [d['user'] for d in players]==prev.author: #check duplicate
    #                         await message.channel.send(f"Player has already joined")
    #                         return
    #                     else: 
    #                         print ("111111111111111111111111111111111111111111")
    #                         players.append({    #add player
    #                         'user':prev.author,
    #                         'score':0
    #                     })
    #                 elif (prev.content == "!continue"): #exit player add
    #                     check=True

    #                 elif (prev.content == "!cancel"): #exit player add
    #                     await exitGame()
    #                     exit
    #         print (players)         

    #         await message.channel.send(f"Enter game length")
    #         
    #         N=None
    #         while N is None:  
    #             async for prev in message.channel.history(limit=1):
    #                 if (prev.author == message.author and int(prev.content)<=50):
    #                     N=int(prev.content)
                    
    #         if N==0:
    #                     await exitGame()
    #                     exit
    #         else:
                
    #             await message.channel.send(f"Setting up game for {N} words...")
    #             await full_game_iteration(N)
    #             players=[]
            
    

    
    
    
    
bot.run(TOKEN)
