# %%
import requests
import random
from typing import List, Dict
rhyme_endpoint = "https://api.datamuse.com/words"
file_name = "3000_words_no_spaces.txt"

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


# TODO: Optimization- on the game setup we pick the words

def create_rhyme_results_list_of_dict(chosen_words : List[str]) -> List[Dict[str,List[Dict]]]:
    list_of_output_dicts = []
    for chosen_word in chosen_words:
        #preprocessing
        output_dict = {}
        for code in PARAM_CODES:
            output_dict[code] = get_request_json(chosen_word,code) # Dict[List[Dict]]
        list_of_output_dicts.append(output_dict)
    return list_of_output_dicts

def full_game_iteration(NUMBER_OF_WORDS):
    total_score = 0
    
    # finds n random words from a list
    chosen_words = random.sample(english_lower_list,NUMBER_OF_WORDS)
    list_of_output_dicts = create_rhyme_results_list_of_dict(chosen_words)
    for level,chosen_word in enumerate(chosen_words):
        # asks user to input a word that rhymes
        displayword = chosen_word.replace("_"," ")
        guess = input(f"Find a rhyme for \"{displayword}\": ")


        # find the words that rhy nry hom cns
        # look for the user input inside of these and determine score
        res = check_matches(guess,list_of_output_dicts[level])

        # determine score
        first_matched_type = [k for k, v in res.items() if v]
        if first_matched_type:
            score_for_level = SCORES[first_matched_type[0]]
            #update total score
            total_score += score_for_level * res[first_matched_type[0]]['numSyllables']

            print(f"""\
            Your guess: {guess}
            Type: {CODE_TO_NAME_MAPPING[first_matched_type[0]]}
            Score: {score_for_level} * {res[first_matched_type[0]]['numSyllables']} Syllable
            Total Score: {total_score}""")
        else:
            print(f"""\
            Your guess: {guess}
            Type: NO MATCH
            Score: 0
            Total Score: {total_score}""")

if __name__ == "__main__":
    N = 3
    print(f"Setting up game for {N} words")
    full_game_iteration(N)

# %%
