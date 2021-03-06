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
        print(f"{ordinal(i + 1)} player: {leaderboard[i]['PLAYER_NAME']}")
        shots += get_shot_log(player_id, season, season_type)

        # Save progress
        with open('scraped_data/temp.json', 'w') as out:
            json.dump(shots, out, indent = 4)

    column_names = list(shots[0].keys())
    column_data = [[shot.get(key, '') for key in column_names] for shot in shots]
    shots_df = pd.DataFrame(data = shots, columns = column_names)
    shots_df.to_csv('scraped_data/shots 2018-19.csv')

def ordinal(num):
    num_ord = {1: 'st', 2: 'nd', 3: 'rd'}.get(num if num < 20 else num % 10, 'th')
    return f'{num}{num_ord}'

if __name__ == '__main__':
    main()