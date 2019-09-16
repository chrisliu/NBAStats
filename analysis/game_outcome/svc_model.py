import numpy as np
from sklearn import svm, metrics
from .preprocessing import TeamPreprocessor, to_features

def main():
    # Preloaded GSW data
    team_id = 1610612744 # GSW
    p = TeamPreprocessor('shot_data/shots 2018-19.csv', team_id, to_features, 
        'shot_data/gsw_outcomes.json')

    def prep_data(data):
        x = [np.concatenate((ht_shots, vt_shots)) for (ht_shots, vt_shots, _) in data]
        y = [is_win for (_, _, is_win) in data]
        return x, y

    x_train, y_train = prep_data(p.train_data)
    x_test, y_test = prep_data(p.test_data)

    for kernel in ('linear', 'poly', 'rbf'):
        clf = svm.SVC(kernel = kernel)
        clf.fit(x_train, y_train)

        y_pred = clf.predict(x_test)
        print(f"{kernel} accuracy: {metrics.accuracy_score(y_test, y_pred)}")

if __name__ == '__main__':
    main()