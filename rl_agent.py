import random

q_table = {}
actions = ["add_index", "rewrite_query", "no_action"]

def choose_action(state):
    if state not in q_table:
        q_table[state] = [0, 0, 0]
    return random.randint(0, 2)

def update_q(state, action_index, reward):
    q_table[state][action_index] += 0.1 * reward