import json
import requests
from nbastats.http import get_response

GAME_INFO_URL = 'https://stats.nba.com/stats/boxscoresummaryv2'

def get_game_info(game_id):
    if not isinstance(game_id, int):
        raise ValueError("game_id must be an int")

    params = {
        'GameID': str(game_id).rjust(10, '0')
    }

    response_str = get_response(GAME_INFO_URL, params)

    try:
        raw_game_info = json.loads(response_str)
    except Exception as e:
        raise ValueError(f"API error - {response_str}")

    raw_game_info = raw_game_info['resultSets']

    # Game summary
    summary = _nba_to_listdict(raw_game_info[0])[0]

    # Other stats
    home_other, visiting_other = _nba_to_listdict(raw_game_info[1])

    # Officials
    officials = _nba_to_listdict(raw_game_info[2])

    # Inactive
    inactive = _nba_to_listdict(raw_game_info[3])

    # Game Info
    game_info = _nba_to_listdict(raw_game_info[4])[0]

    # Line score
    home_line, visiting_line = _nba_to_listdict(raw_game_info[5])

    # Last meeting
    last_meeting = _nba_to_listdict(raw_game_info[6])[0]

    # Season series
    season_series = _nba_to_listdict(raw_game_info[7])[0]

    # Set winning team
    def clean_team_info(line):
        keys = ['TEAM_ID', 'TEAM_ABBREVIATION', 'TEAM_CITY_NAME', 'TEAM_NICKNAME']
        return {key: line[key] for key in keys}

    if home_line['PTS'] > visiting_line['PTS']:
        winner = clean_team_info(home_line) 
    else:
        winner = clean_team_info(away_line)

    return {
        'summary': summary,
        'other_stats': {
            'home': home_other,
            'visiting': visiting_other
        },
        'officials': officials,
        'inactive': inactive,
        'game_info': game_info,
        'line_score': {
            'home': home_line,
            'visiting': visiting_line
        },
        'last_meeting': last_meeting,
        'season_series': season_series,
        'winner': winner
    }

def _nba_to_listdict(nba_dict):
    header = nba_dict['headers']
    return [dict(zip(header, item)) for item in nba_dict['rowSet']]