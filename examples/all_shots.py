import json
import pandas as pd
from nbastats.player import get_leaders, get_shot_log
from nbastats.options import Season, SeasonType

def main():
    season = Season(2018)
    season_type = SeasonType.REGULAR_SEASON

    leaderboard = get_leaders(season, season_type)
    player_ids = [player['PLAYER_ID'] for player in leaderboard]

    shots = list()
    for i, player_id in enumerate(player_ids):
        print(f"{i + 1}th player: {leaderboard[i]['PLAYER']}")
        shots += get_shot_log(player_id, season, season_type)

        # Save progress
        with open('output/temp.json', 'w') as out:
            json.dump(shots, out, indent = 4)

    column_names = list(shots[0].keys())
    column_data = [[shot.get(key, '') for key in column_names] for shot in shots]
    shots_df = pd.DataFrame(data = shots, columns = column_names)
    shots_df.to_csv('output/shots 2018-19.csv')

if __name__ == '__main__':
    main()