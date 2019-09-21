import json
from functools import reduce
from math import ceil
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, KFold
from nbastats.game import get_game_info

class DataPreprocessor(object):
    """Generic data preprocessor loads a CSV file into a pandas.DataFrame.

    Attributes:
        raw_data: A pandas.DataFrame of the data from the CSV file.
        data: A list of data used for a model.
        target: A list of targets corresponding to the data for a model.
    """

    def __init__(self, data_filename, data_preprocessor, target_preprocessor, **kwargs):
        """Initializes a DataProcessor object.

        Arguments:
            data_filename: A string for the CSV file to be loaded.
            data_preprocessor: A function that takes some intermediate data
                and outputs some final data.
            target_preprocessor: A function that takes some intermediate target
                and outputs some final target.
            kwargs: A dictionary of keys and values for the overloaded 
                self._set_data function.
        """

        self.raw_data = None
        self.data = None
        self.target = None

        self._load_data(data_filename)
        self._set_data(data_preprocessor, target_preprocessor, **kwargs)

    def _load_data(self, data_filename):
        """Loads a CSV file with the first column as the index into raw_data."""

        self.raw_data = pd.read_csv(data_filename, index_col = 0) 

    def _set_data(self, data_preprocessor, target_preprocessor, **kwargs):
        """Generates intermediate and final data/target."""

        raw_data, raw_target = self._prep_data(**kwargs)
        self.data = data_preprocessor(raw_data)
        self.target = target_preprocessor(raw_target)
        
    def _prep_data(self):
        """Generates intermediate data/targte for user supplied preprocessors.

        Returns:
            A tuple containing the intermediate data and the intermediate target.
            
            Intermediate data: A list of data samples to be processed by a user's
                preprocessor function.
            Intermediate target: A list of target samples corresponding to their
                respective intermediate data values to be processed by a user's
                preprocessor function.
        """

        raise NotImplementedError(f'{self.__class__.__name__}._prep_data not implemented')

    def train_test_split(self, test_size, random_state = None):
        """Splits train/test data with sklearn.model_selection.train_test_split."""

        return train_test_split(self.data, self.target, test_size = test_size,
            random_state = random_state)

    def kfold(self, splits, shuffle = True, random_state = None):
        """Returns train/test data defined by sklearn.model_selection.KFold."""

        kf = KFold(n_splits = splits, shuffle = shuffle, random_state = random_state) 
        for train_index, test_index in kf.split(self.data):
            x_train, x_test = self.data[train_index], self.data[test_index]
            y_train, y_test = self.target[train_index], self.target[test_index]
            yield x_train, x_test, y_train, y_test

class TeamPreprocessor(DataPreprocessor):
    def __init__(self, shot_data_filename, team_id, data_preprocessor, 
        target_preprocessor, outcome_filename = None
    ):
        """Initializes a TeamPreprocessor object.
        
        data_preprocessor
            Arguments:
                A list of pairs of pandas.DataFrame containing shot 
                    information from (team_id's team, opponent team)
            Returns:
                A list of processed samples.

        target_preprocessor
            Arguments:
                A list of boolean values indicating if team_id's team won the
                    game.
            Returns:
                A list of processed targets. 
        """

        super(TeamPreprocessor, self).__init__(
            shot_data_filename, 
            data_preprocessor,
            target_preprocessor,
            team_id = team_id,
            outcome_filename = outcome_filename
        )

    def _prep_data(self, *, team_id, outcome_filename):
        """Get's shot information on a per game basis and the game's outcome."""

        # Reindex DataFrame
        self.raw_data = self.raw_data.set_index('GAME_ID')

        # Get game ids of the team
        team_games = self.raw_data[self.raw_data.TEAM_ID == team_id]
        self._game_ids = list(set(team_games.index))

        # Get target
        self._get_outcomes(outcome_filename, team_id)
        target = [self._outcomes[game_id] for game_id in self._game_ids]

        # Get data
        data = [_split_team_shots(self.raw_data.loc[game_id], team_id)
            for game_id in self._game_ids]

        return data, target

    def _get_outcomes(self, outcome_filename, team_id):
        """Loads cached game outcomes or gets outcomes from NBA stats."""

        if outcome_filename is not None:
            with open(outcome_filename, 'r') as in_f:
                self._outcomes = json.load(in_f)
                # Changing keys back to int (json format doesn't allow keys to be ints)
                for key in list(self._outcomes.keys()):
                    self._outcomes[int(key)] = self._outcomes.pop(key)
        else:
            self._outcomes = {game_id: get_game_info(game_id)['winner']['TEAM_ID'] == team_id 
                for game_id in self._game_ids}

    def export_outcomes(self, filename):
        """Caches game outcomes to the given file."""

        with open(filename, 'w') as out:
            json.dump(self._outcomes, out, indent = 4)

# Preprocessing functions
def identity(*args):
    """Generic identity function.

    Returns:
        None if there aren't any arguments.
        The argument if there's only 1 argument.
        A tuple of arguments if there are more than 1 arguments.
    """

    if not len(args):
        return None
    elif len(args) == 1:
        return args[0]
    return args

def shots_to_matrix_wrapper(width, length, width_shift = 0, length_shift = 0):
    """A wrapper that converts shot coordinates to a matrix."""

    def shots_to_matrix(shots):
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

    return shots_to_matrix

def sum_matrix_by_grids_wrapper(w, l = None):
    """A wrapper that sums a matrix by grids."""

    if l is None:
        l = w

    if l == 1 and w == 1:
        return identity

    def sum_matrix_by_grids(shots):
        length, width = shots.shape

        length_chunks = ceil(length / l)
        corrected_length =  length_chunks * l
        length_pad = (corrected_length - length) // 2
        width_chunks = ceil(width / w)
        corrected_width = width_chunks * w
        width_pad = (corrected_width - width) // 2

        # Correct matrix so it could be evenly divided
        corrected_mat = np.full((corrected_length, corrected_width), 0)
        corrected_mat[length_pad: length_pad + length, 
            width_pad: width_pad + width] = shots

        # Split matrix into grids of l x w
        grids = np.split(corrected_mat, length_chunks, axis = 0)
        grids = [np.split(h_slice, width_chunks, axis = 1) for h_slice in grids]

        # Compute sum for each grid
        grids_sum = [[np.sum(chunk) for chunk in chunks] for chunks in grids]
        return np.array(grids_sum)

    return sum_matrix_by_grids 

def shots_to_features_wrapper(court_width, court_length, court_width_shift = 0, 
    court_length_shift = 0, grid_width = 1, grid_length = 1
):
    """A wrapper that converts shot coordinates to a list of features."""

    shots_to_matrix = shots_to_matrix_wrapper(court_width, court_length, 
        court_width_shift, court_length_shift)
    sum_matrix_by_grids = sum_matrix_by_grids_wrapper(grid_width, grid_length)

    def shots_to_features(shots):
        shot_mat = shots_to_matrix(shots)
        shot_mat = sum_matrix_by_grids(shot_mat)
        dimension = reduce(lambda x, y: x * y, shot_mat.shape)
        return shot_mat.reshape(dimension)

    return shots_to_features

def shots_to_shot_types(shots):
    """Converts shots into a (2pt attempts, 3pt attempts) pair."""

    twopt_count = len(shots[shots.SHOT_TYPE == '2PT Field Goal']) 
    threept_count = len(shots[shots.SHOT_TYPE == '3PT Field Goal']) 
    return [twopt_count, threept_count]

# Helper Functions
def _split_team_shots(game_shots, team_id = None):
    """Splits shots by team.

    Arguments:
        game_shots: A pandas.DataFrame containing shots in a game.
        team_id: An optional integer ID for the team to be returned first.
        
    Returns:
        A pair of pandas.DataFrame such that it's (team1 shots, team2 shots).

        team1 shots will be shots by team_id if team_id is not None.
    """

    if team_id is None:
        team_id = next(iter(set(game_shots.TEAM_ID)))

    team1_shots = game_shots[game_shots.TEAM_ID == team_id]
    team2_shots = game_shots[game_shots.TEAM_ID != team_id]

    return team1_shots, team2_shots