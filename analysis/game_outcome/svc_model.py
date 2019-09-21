import numpy as np
from sklearn import svm, metrics
from sklearn.model_selection import cross_val_score
from .preprocessing import TeamPreprocessor, shots_to_features_wrapper, identity

def main():
    # Preloaded GSW data
    print("Prepping data...")
    team_id = 1610612744 # GSW
    shots = TeamPreprocessor('scraped_data/shots 2018-19.csv', team_id, 
        data_preprocessor, identity, 'scraped_data/gsw_outcomes.json')

    # Cross Validation
    print("Model Results:")
    for kernel in ('linear', 'poly', 'rbf'):
        clf = svm.SVC(kernel = kernel, gamma = 'auto')
        scores = cross_val_score(clf, shots.data, shots.target, cv = 5)
        print(f"Model: {kernel[0].upper()}{kernel[1:]}")
        print(f"Scores: {', '.join(f'{score:0.2f}' for score in scores)}")
        print(f"Accuracy: {scores.mean():0.2f} (+/- {scores.std() * 2})")

def data_preprocessor(raw_data):
    """Processes shot data into features.

    Width of a basketball court: axis from courtside to courtside
    Length of a basketball court: axis from basket to basket

    Arguments:
        raw_data: A list of pairs of pandas.DataFrame containing shot 
            information.

    Returns:
        A list of numpy.array that contains the features of home team and 
        visiting team shots concatenated into a 1D array of size home team
        features count + visiting team features count.

        Shot features are simply the number of shots in a given grid on a
        basketball court.
    """

    width = 500 # X axis or bounding width of a basketball court
    length = 375 # Y axis or bounding length of half a basketball court
    width_shift = 250 # X axis values start from -250
    length_shift = 50 # Y axis values start from -50
    grid_width = 25 # X axis size of the grid
    grid_length = 25 # Y axis size of the grid

    shots_to_features = shots_to_features_wrapper(width, length, width_shift, 
        length_shift, grid_width, grid_length)

    data = list()
    for (ht_shots, vt_shots) in raw_data:
        ht_features = shots_to_features(ht_shots)
        vt_features = shots_to_features(vt_shots)
        data.append(np.concatenate((ht_features, vt_features)))

    return data

if __name__ == '__main__':
    main()