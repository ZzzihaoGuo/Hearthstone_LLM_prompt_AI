import re
import numpy as np
import random


def clean_description(description):
    # 移除 HTML 标签和特殊字符
    cleaned = re.sub(r'<[^>]+>', '', description)  
    cleaned = re.sub(r'\[.*?\]', '', cleaned)      
    cleaned = re.sub(r'@\s*', '', cleaned)  
    cleaned = cleaned.replace('\n', ' ')         
    return cleaned.strip()

def extract_last_integer(text):
    # 正则表达式匹配所有整数
    matches = re.findall(r'\b\d+\b', text)
    if matches:
        return int(matches[-1])  # 返回最后一个匹配的整数
    else:
        return None  # 或者返回其他值，表示没有找到整数

def combine_names_and_stats_with_info(card_feat, card_info):
    descriptions = []
    
    if card_info[0] == None:
        return "Your hand zone has no cards"

    for i in range(card_feat.shape[0]):  # 遍历每一行
        # 跳过空行（如果第一列没有填充）
        if card_info[i] is None:
            continue
        
        # 提取卡牌特征
        cost = card_feat[i, 0]  # 卡牌消耗
        org_cost = card_feat[i, 1]  # 卡牌消耗
        is_playable = 'playable' if card_feat[i, 2] == 1 else 'not playable'  # 是否可打出
        
        # 提取卡牌类型
        if card_feat[i, 16] == 1:  # minion
            org_atk = card_feat[i, 3]
            atk = card_feat[i, 4]
            health = card_feat[i, 5]
            org_health = card_feat[i, 6]
            type_desc = f"Minion with {atk} attack and {health} health, orginally with {org_atk} attack and {org_health} health."
        elif card_feat[i, 18] == 1:  # weapon
            org_atk = card_feat[i, 3]
            atk = card_feat[i, 4]
            durability = card_feat[i, 5]
            type_desc = f"Weapon with {atk} attack and {durability} durability, orginally with{org_atk} attack"
        elif card_feat[i, 17] == 1:  # spell
            type_desc = "Spell."
        else:
            type_desc = "Unknown card type."
        
        # 提取卡牌名称和描述
        name, info = card_info[i]

        info = clean_description(info)
        
        # 合并特征和描述
        description = f"Card Name: {name}. Cost: {cost} and orginal Coat: {org_cost}, {type_desc} Status: {is_playable}. {info}"
        descriptions.append(description)
    
    return 'Your hand zone cards are as follow: ' + "\n\n".join(descriptions)  


def convert_minions_matrix_and_info_to_text(minions, minion_info):
    # 检查前7个随从是否全为 None
    if all(info is None for info in minion_info[:7]):
        player_minions_description = "You have no minions."
    else:
        player_minions_description = generate_minions_description(minions[:7], minion_info[:7], "Your")
    
    # 检查后7个随从是否全为 None
    if all(info is None for info in minion_info[7:]):
        opponent_minions_description = "Your opponent has no minions."
    else:
        opponent_minions_description = generate_minions_description(minions[7:], minion_info[7:], "Opponent's")

    # 返回完整的描述文本
    return f"{player_minions_description}\n\n{opponent_minions_description}"

def generate_minions_description(minions_slice, minion_info_slice, owner):
    descriptions = []
    race_names = {
    0: "INVALID",
    1: "BLOODELF",
    2: "DRAENEI",
    3: "DWARF",
    4: "GNOME",
    5: "GOBLIN",
    6: "HUMAN",
    7: "NIGHTELF",
    8: "ORC",
    9: "TAUREN",
    10: "TROLL",
    11: "UNDEAD",
    12: "WORGEN",
    13: "GOBLIN2",
    14: "MURLOC",
    15: "DEMON",
    16: "SCOURGE",
    17: "MECHANICAL",
    18: "ELEMENTAL",
    19: "OGRE",
    20: "BEAST",
    21: "TOTEM",
    22: "NERUBIAN",
    23: "PIRATE",
    24: "DRAGON",
    25: "BLANK",
    26: "ALL",
    38: "EGG"
}
    
    for i, minion in enumerate(minions_slice):
        # 跳过空行（如果没有随从）
        if minion[0] == 0:
            continue

        # 提取随从基础信息
        cost = minion[0]  # 法力值消耗
        can_attack = 'can attack' if minion[1] == 1 else 'cannot attack'
        atk = minion[2]  # 基础攻击力
        attack_damage = minion[3]  # 当前攻击力
        health = minion[4]  # 当前生命值
        base_health = minion[5]  # 基础生命值

        # 提取关键字信息，并排除"no"的状态
        status_list = []
        if minion[6] == 1:
            status_list.append('Taunt')
        if minion[7] == 1:
            status_list.append('Divine Shield')
        if minion[8] == 1:
            status_list.append('Deathrattle')
        if minion[9] == 1:
            status_list.append('Frozen')
        if minion[10] == 1:
            status_list.append('Windfury')
        if minion[11] == 1:
            status_list.append('Silenced')
        if minion[12] == 1:
            status_list.append('Stealth')

        # 提取随从种族信息
        race = np.argmax(minion[14:])  # 获取种族的索引
        race_name = race_names.get(race, "Unknown race")  # 获取种族名称 race"
        
        # 结合随从信息
        if minion_info_slice[i] is not None:
            minion_name = minion_info_slice[i][0]  # 获取随从名称
            minion_desc = clean_description(minion_info_slice[i][1])  # 获取随从描述并替换换行符
        else:
            minion_name = "Unknown Minion"
            minion_desc = "No description available."

        # 拼接状态列表
        status_str = ", ".join(status_list) if status_list else "No special abilities"
        
        # 生成随从的描述
        description = (f"{owner} Minion {i + 1}: {minion_name}. Cost {cost}, {can_attack}, "
                       f"Attack {atk} (Damage {attack_damage}), Health {health}/{base_health}, "
                       f"{status_str}, Race: {race_name}. {minion_desc}")
        descriptions.append(description)

    return "\n\n".join(descriptions) if descriptions else f"{owner} has no active minions."


def convert_weapons_data_to_text(weapon_data):
    # 检查自己和对方的武器
    if all(weapon is None for weapon in weapon_data):
        return ""
    
    player_weapons = weapon_data[:1]  # 假设第一个是自己的武器
    opponent_weapons = weapon_data[1:]  # 假设第二个及以后的都是对方的武器

    descriptions = []
    
    # 处理自己的武器
    if all(weapon is None for weapon in player_weapons):
        descriptions.append("You have no weapons.")
    else:
        for i, weapon in enumerate(player_weapons):
            if weapon is None:
                continue
            
            weapon_name = weapon[0]
            weapon_desc = clean_description(weapon[1])
            
            descriptions.append(f"Your Weapon: {weapon_name} and description: {weapon_desc}")

    # 处理对方的武器
    if all(weapon is None for weapon in opponent_weapons):
        descriptions.append("Your opponent has no weapons.")
    else:
        for i, weapon in enumerate(opponent_weapons):
            if weapon is None:
                continue
            
            weapon_name = weapon[0]
            weapon_desc = clean_description(weapon[1])
            
            descriptions.append(f"Opponent's Weapon: {weapon_name} and description: {weapon_desc}")

    return "\n".join(descriptions)


def convert_secrets_data_to_text(secrets_data):
    # 检查自己的秘密
    if all(secret is None for secret in secrets_data):
        return ""

    descriptions = []

    for i, secret in enumerate(secrets_data):
        if secret is None:
            continue

        secret_name = secret[0]
        secret_desc = secret[1].replace("Description: ", "").strip()

        descriptions.append(f"Your Secret {i + 1}: {secret_name}. Description: {secret_desc}")

    return "\n".join(descriptions) if descriptions else "You have no secrets."


def convert_hero_state_to_text(hero_state):
    descriptions = []

    for i, state in enumerate(hero_state):
        if i == 0:
            player_type = "Your"
        else:
            player_type = "Opponent's"

        # 基础信息
        attack_damage = int(state[1])
        base_health = int(state[2])
        current_health = int(state[3])
        remaining_mana = int(state[7])
        base_mana = int(state[8])
        spell_power = int(state[9])
        armor = int(state[10])

        # 武器处理
        if state[11] == 1:  # 如果武器存在
            weapon_durability = int(state[12])
            weapon_attack = int(state[13])
            weapon_info = f"with a weapon (Attack: {weapon_attack}, Durability: {weapon_durability})"
        else:
            weapon_info = None

        deck_count = int(state[14])
        hand_count = int(state[15])
        secret_count = int(state[16])

        # 可选状态
        status_parts = []
        if state[4] == 1:
            status_parts.append("frozen")
        if state[5] == 1:
            status_parts.append("has windfury")
        if state[6] == 1:
            status_parts.append("has stealth")

        status_text = ", ".join(status_parts) if status_parts else None

        # 排除不能攻击的情况
        description = f"{player_type} hero has {attack_damage} attack damage, {base_health} base health ({current_health} current health), "
        description += f"{remaining_mana}/{base_mana} mana, {spell_power} spell power, {armor} armor."

        # 仅在有武器时添加武器信息
        if weapon_info:
            description += f" {weapon_info}."

        description += f" {player_type} have {deck_count} cards in the deck, {hand_count} cards in hand."

        # 仅在有秘密时提到秘密
        if secret_count > 0:
            description += f" and {secret_count} secrets."

        # 仅在有状态时提到状态
        if status_text:
            description += f" Status: {status_text}."

        if i == 0:
            num_attacks = int(state[26])
            num_cards_played = int(state[27])
            overload_locked = int(state[28])
            description += (
                f" Number of attacks this turn: {num_attacks}, cards played this turn: {num_cards_played}, "
                f"overload locked: {overload_locked}."
            )

        descriptions.append(description.strip())  # 删除末尾可能多余的空格

    return "\n".join(descriptions)


def convert_actions_to_text(action_list):
    descriptions = []
    # print('org: ', len(action_list))
    for i, action in enumerate(action_list):
        if 'ChooseTask' in action:
            return random.randint(0, len(action_list)-1)

        if 'EndTurnTask' in action:
            descriptions.append(f"{i}. You end your turn.")
        elif 'PlayCardTask' in action:
            # 获取卡牌名称和类型
            card_info = action.split("play ")[1].split(" Option")[0]
            card_name, card_type = card_info.split('(')
            target_info = action.split("'")  # 用于获取目标
            if  "MINION" in action:
                position_info = action.split("to Pos[")[1].split(']')[0]
                descriptions.append(f"{i}.You play {card_name} (MINION) to position {position_info}.")
            elif "SPELL" in action:
                if len(target_info) > 2:
                    # target_name = target_info[2]  # 目标
                    descriptions.append(f"{i}. You play {card_name} ({card_type.strip()}).")
                else:
                    descriptions.append(f"{i}. You play {card_name} ({card_type.strip()}).")
            elif 'WEAPON' in action:
                descriptions.append(f"{i}. You play {card_name} ({card_type.strip()}).")
            elif 'HERO' in action:
                descriptions.append(f"{i}. You play {card_name} ({card_type.strip()}).")

        elif 'HeroPowerTask' in action:
            # 获取英雄技能名称
            hero_power = action.split("using '")[1].split("'")[0]
            descriptions.append(f"{i}. You use the hero power '{hero_power}'.")
        elif 'HeroAttackTask' in action:
            # 获取攻击信息
            attacker = action.split("'")[1]
            target = action.split("attacks '")[1].split("'")[0]
            descriptions.append(f"{i}. Your {attacker} attacks {target}.")
        elif 'MinionAttackTask' in action:
            attacker = action.split("'")[1]
            target = action.split("attack")[1]
            descriptions.append(f"{i}. Your {attacker} attacks {target}.")

    # print('after: ', len(descriptions))

    if len(descriptions) != len(action_list):
        print('Actions number not match')
    


    return 'You can choose one action from below: ' + ' '.join(descriptions)

