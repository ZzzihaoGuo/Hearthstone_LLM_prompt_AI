import os
import random
import re
from openai import OpenAI

from Hearthstone import Hearthstone
from matrix_2_text import combine_names_and_stats_with_info, convert_minions_matrix_and_info_to_text, convert_weapons_data_to_text

def call_openai_api(game_state, temperature=0.7, max_tokens=150):
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    completion = client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {'role': 'system', 'content': 'You are an expert Hearthstone player.'}, # add more descriptions about how to play hearthstone
            {'role': 'user', 'content': game_state}
        ]
    )

    print(completion.choices[0].message.content)

    return completion.choices[0].message.content


def game_state_for_LLM(obs, options, player, op_player):

    opponent_state = obs[op_player]
    player_state = obs[player]

    # for keys in opponent_state.keys():
    #     # can't know everything of opponent, fix: secret numbers 
    #     if keys in ['hand_card_names', 'secret_names', 'hand_card_stats', 'deck_strategy']:
    #         continue
    #     opponent_LLM_state = format_card_descriptions(keys, opponent_state[keys], False)
    
    # for keys in player_state.keys():
    #     if keys in ['deck_strategy']:
    #         continue
    #     player_LLM_state = format_card_descriptions(keys, opponent_state[keys], True)

    hand_zone_text = combine_names_and_stats_with_info(player_state['hand_card_stats'], player_state['hand_card_name_description'])

    minion_text = convert_minions_matrix_and_info_to_text(player_state['minion_stats'], player_state['minion_name_description'])
    
    weapon_text = convert_weapons_data_to_text(player_state['weapon_name_description'])

    print()

    

    
    




    # game_state = f"Your hand have {handcards}"
    pass

def game_action_for_env(ai_move):


    pass



def multi_turn_conversation_with_bot(player, op_player):
    game = Hearthstone()
    position, obs, options, reward, done = game.reset()
    print("reset:  ", position)

    game_over = False
    # game_state = game_state_for_LLM(obs, options, player, op_player)

    while not game_over:
        
        # other method --random action
        if player != position+ '_not_in_model':
            print("bot's turn")
            action = random.choice(options)
            position, obs, options, reward, done = game.step(action)
            continue

        print("LLM's turn:")
        game_state = game_state_for_LLM(obs, options, player, op_player)

        # ai_move = call_openai_api(game_state)

        # action = game_action_for_env(ai_move)
        action = random.choice(options)
        position, obs, options, reward, done = game.step(action)

        if done is True:
            print('Game Over! AI wins!')


if __name__ == '__main__':

    multi_turn_conversation_with_bot("Player1_not_in_model", "Player2")




