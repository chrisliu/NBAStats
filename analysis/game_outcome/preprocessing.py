import json
import random
from functools import reduce
import numpy as np
import pandas as pd
from nbastats.game import get_game_info

class TeamPreprocessor(object):
    TRAIN_PERCENT = 0.7

    def __init__(self, shot_data_filename, team_id, preprocess_function, 
        outcome_filename = None
    ):
        self.team_id = team_id
        self.games = None
        self.game_ids = None
        self.outcomes = None
        self.train_data = None
        self.test_data = None

        self.preprocess_function = preprocess_function     
        self._load_games(shot_data_filename)
        self._get_outcomes(outcome_filename)
        self._prepare_data()

    def _load_games(self, shot_data_filename):
        # Load by GAME_ID column
        shot_data = pd.read_csv(shot_data_filename, index_col = 2)
        shot_data = shot_data.drop(shot_data.columns[0], axis = 1)

        team_games = shot_data[shot_data.TEAM_ID == self.team_id]
        self.game_ids = list(set(team_games.index))

        # Assign all team games
        self.games = shot_data.loc[self.game_ids]

    def _get_outcomes(self, outcome_filename):
        if outcome_filename is not None:
            with open(outcome_filename, 'r') as in_f:
                self.outcomes = json.load(in_f)
                # Changing keys back to int (json format doesn't allow keys to be ints)
                for key in list(self.outcomes.keys()):
                    self.outcomes[int(key)] = self.outcomes.pop(key)
        else:
            self.outcomes = {game_id: get_game_info(game_id)['winner']['TEAM_ID'] == self.team_id
                for game_id in self.game_ids}

    def _prepare_data(self):
        data = list()
        for game_id in self.game_ids:
            ht_shots, vt_shots = split_team_shots(self.games.loc[game_id], self.team_id)
            ht_shots = self.preprocess_function(ht_shots)
            vt_shots = self.preprocess_function(vt_shots)
            outcome = self.outcomes[game_id]
            data.append((ht_shots, vt_shots, outcome))

        random.shuffle(data)
        train_count = int(len(self.game_ids) * self.TRAIN_PERCENT)
        self.train_data = data[:train_count]
        self.test_data = data[train_count:]

    def export_outcomes(self, filename):
        with open(filename, 'w') as out:
            json.dump(self.outcomes, out, indent = 4)

# Helper Functions
def split_team_shots(game_shots, home_team_id = None):
    if home_team_id is None:
        home_team_id = next(iter(set(game_shots.TEAM_ID)))

    team1_shots = game_shots[game_shots.TEAM_ID == home_team_id]
    team2_shots = game_shots[game_shots.TEAM_ID != home_team_id]

    return team1_shots, team2_shots

def identity(shots):
    return shots

def to_matrix(shots):
    """
    (min, max)
    X: (-250, 250) # Court width
    Y: (-50, 500) # Half court length and a little more
    """

    width = 500 # X
    length = 550 # Y
    width_shift = 250 # X
    length_shift = 50 # Y

    def shift_x(x_coord):
        shifted = x_coord + width_shift
        return shifted, shifted >= 0 and shifted < width

    def shift_y(y_coord):
        shifted = y_coord + length_shift
        return shifted, shifted >= 0 and shifted < length

    shot_matrix = np.full((length, width), 0)
    for _, shot in shots.iterrows():
        y, is_y_valid = shift_y(shot.LOC_Y)
        x, is_x_valid = shift_x(shot.LOC_X)

        if not is_y_valid or not is_x_valid:
            continue

        shot_matrix[y, x] += 1

    return shot_matrix

def to_features(shots):
    shot_mat = to_matrix(shots)
    dimension = reduce(lambda x, y: x * y, shot_mat.shape)
    return shot_mat.reshape(dimension)

def to_count(shots):
    return np.sum(to_features(shots))

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    team_id = 1610612744 # GSW
    p = TeamPreprocessor('shot_data/shots 2018-19.csv', team_id, to_matrix, 
        'shot_data/gsw_outcomes.json')
    print(p.train_data)