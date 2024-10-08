import os
import random
import re
from openai import OpenAI

from Hearthstone import Hearthstone
from matrix_2_text import *


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

    return int(completion.choices[0].message.content[-2])


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

    secret_text = convert_secrets_data_to_text(player_state['secret_name_description'])

    hero_stats_text = convert_hero_state_to_text(player_state['hero_stats'])

    return '/n'.join([hand_zone_text, minion_text, weapon_text, secret_text, hero_stats_text])

def game_action_for_env(game_state, actions):
    actions_list = []
    
    for i in actions:
        actions_list.append(i.FullPrint())
    
    actions = convert_actions_to_text(actions_list)

    action_state_input = '/n'.join([game_state, actions])

    output_prompt = ' Attention! You need choose 1 action and give me the index number in the end of your reply, JUST GIVE ME 1 OPTION, DONT SHOW OTHERS' 
    
    return action_state_input + output_prompt



def multi_turn_conversation_with_bot(player, op_player):
    game = Hearthstone()
    position, obs, options, reward, done = game.reset()
    print("reset:  ", position)

    game_over = False
    # game_state = game_state_for_LLM(obs, options, player, op_player)

    while not game_over:
        
        # other method --random action
        if player != position+ '_not_in_model':
            print("bot's action")
            action = random.choice(options)
            position, obs, options, reward, done = game.step(action)
            continue

        print("LLM's action")
        game_state = game_state_for_LLM(obs, options, player, op_player)

        input_for_model = game_action_for_env(game_state, options)

        # ai_move = call_openai_api(input_for_model)
        # action = game_action_for_env(ai_move)
        action = random.choice(options)

        position, obs, options, reward, done = game.step(action)

        if reward == 1:
            print('Game Over! AI wins!')
        elif reward == -1:
            print('Game Over! Bot wins')
        if done is True:
            break


if __name__ == '__main__':

    multi_turn_conversation_with_bot("Player1_not_in_model", "Player2")




