import os
import random
import re
import openai
from openai import OpenAI

from Hearthstone import Hearthstone
from matrix_2_text import *

# client = OpenAI()
def call_openai_api(game_state, temperature=0.2, max_tokens=100):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {'role': 'system', 'content': 'You are an expert Hearthstone player.'}, # add more descriptions about how to play hearthstone
            {'role': 'user', 'content': game_state}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )

    print('gpt output: ', completion.choices[0].message.content)

    output_number = extract_last_integer(completion.choices[0].message.content)

    return int(output_number)


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

    if isinstance(actions, int):
        return actions

    action_state_input = '/n'.join([game_state, actions])

    output_prompt = ' /n/n Attention! You need choose 1 action and give me the index number in the end of your reply, JUST GIVE ME 1 INT NUMBER AT LAST, DONT SHOW OTHERS' 
    
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
            # print("bot's action")
            action = random.choice(options)
            position, obs, options, reward, done = game.step(action)
            continue

        # print("LLM's action")
        game_state = game_state_for_LLM(obs, options, player, op_player)

        input_for_model = game_action_for_env(game_state, options)

        if isinstance(input_for_model, int)
            ai_move = input_for_model
        else:

            ai_move = call_openai_api(input_for_model)
            
        # action = game_action_for_env(ai_move)
        action = options[ai_move]

        position, obs, options, reward, done = game.step(action)
        if player == 'Player1_not_in_model':
            if reward == 1:
                print('Game Over! AI wins!')
            elif reward == -1:
                print('Game Over! Bot wins')
            if done is True:
                return reward
        
        else:
            if reward == -1:
                print('Game Over! AI wins!')
            elif reward == 1:
                print('Game Over! Bot wins')
            if done is True:
                return reward


if __name__ == '__main__':
    total_game_num = 4
    player1_win_number = 0
    player2_win_number = 0
    for i in range(4):
        
        # AI play first 
        # count = multi_turn_conversation_with_bot("Player1_not_in_model", "Player2")
        # Bot play first
        count = multi_turn_conversation_with_bot("Player2_not_in_model", "Player1")

        if count is False:
            total_game_num -= 1
        
        elif count == 1:
            player1_win_number += 1
        elif count == -1:
            player2_win_number += 1
    
    print('play1 win rate: ', player1_win_number/total_game_num)
    print('play2 win rate: ', player2_win_number/total_game_num)
    print('worked game number: ', total_game_num)



