import json
import requests
from nbastats.options import LeaderboardSortCategory

PLAYER_SHOT_LOG_URL = 'https://stats.nba.com/stats/shotchartdetail'
LEADERBOARDS_URL = 'https://stats.nba.com/stats/leaguedashplayerstats'

def get_shot_log(player_id, season, season_type, **kwargs):
    """Gets the shot log for a player from NBA stats.

    The NBA stats api returns a dictionary in the following format:
    {
        'resultSets': [
            {
                'headers': [
                    ...
                ],
                'rowSet': [
                    [
                        ... # Shot 1
                    ],
                    [
                        ... # Shot 2
                    ],
                    ...
                ],
                ...     
            }
        ],
        ...
    }

    Arguments:
        player_id: An integer id of a player.
        season: A Season object for the season.
        season_type: A string for the season type.

    Raises:
        ValueError: If the arguments provided aren't valid queries or the query
            doesn't conform to the NBA stats api.

    Returns:
        A list of dictionaries where each describes a shot.
    
        For each set in 'resultSets', a shot will be described by a dictionary 
        where the keys are the 'headers' and the values are the corresponding 
        statistics in the shot list.        
    """

    params = {
        'PlayerID': player_id,
        'Season': str(season),
        'SeasonType': season_type,
        'PlayerPosition': "",
        'ContextMeasure': "FGA",
        'DateFrom': "",
        'DateTo': "",
        'GameID': "",
        'GameSegment': "",
        'LastNGames': 0,
        'LeagueID': "00",
        'Location': "",
        'Month': 0,
        'OpponentTeamID': 0,
        'Outcome': "",
        'Period': 0,
        'Position': "",
        'RookieYear': "",
        'SeasonSegment': "",
        'TeamID': 0,
        'VsConference': "",
        'VsDivision': "" 
    }

    for key, val in kwargs.items():
        if key in params:
            params[key] = val
        else:
            raise ValueError(f"{key} is not a valid argument")

    response_str = _get_response(PLAYER_SHOT_LOG_URL, params)

    # If the parameters given aren't valid
    try:
        player_shots = json.loads(response_str)
    except:
        raise ValueError(f"API error - {response_str}")

    shots = list()
    for result in player_shots['resultSets']:
        header = result['headers']
        shots += [dict(zip(header, shot)) for shot in result['rowSet']]

    # Only keep shot data, not league averages
    shots = [shot for shot in shots if shot['GRID_TYPE'] == 'Shot Chart Detail']
    return shots

def get_leaders(season, season_type):
    """Gets the leaders of a season in descending sorted order.

    The NBA stats api returns a dictionary in the following format:
    {
        "resultSet": {
            "headers": [
                ...
            ],
            "rowSet": [
                [
                    ... # Player 1
                ],
                [
                    ... # Player 2
                ],
                ...
            ],
            ...
        },
        ...   
    }

    Arguments:
        season: A Season object for the season.
        season_type: A string for the season type.
        sort_category: An optional string for the category to be sorted by.

    Raises:
        ValueError: If the arguments provided aren't valid queries or the query
            doesn't conform to the NBA stats api.

    Returns:
        A list of players sorted by descending order.

        Each player is represented by a dictionary where the keys are "headers"
        and the values are the corresponding statistics of each player list.
    """

    params = { 
        "Season": str(season),
        "SeasonType": season_type,
        "College": "",
        "Conference": "",
        "Country": "",
        "DateFrom": "",
        "DateTo": "",
        "Division": "",
        "DraftPick": "",
        "DraftYear": "",
        "GameScope": "",
        "GameSegment": "",
        "Height": "",
        "LastNGames": "0",
        "LeagueID": "00",
        "Location": "",
        "MeasureType": "Base",
        "Month": "0",
        "OpponentTeamID": "0",
        "Outcome": "",
        "PORound": "0",
        "PaceAdjust": "N",
        "PerMode": "PerGame",
        "Period": "0",
        "PlayerExperience": "",
        "PlayerPosition": "",
        "PlusMinus": "N",
        "Rank": "N",
        "SeasonSegment": "",
        "ShotClockRange": "",
        "StarterBench": "",
        "TeamID": "0",
        "TwoWay": "0",
        "VsConference": "",
        "VsDivision": "",
        "Weight": ""
    }

    response_str = _get_response(LEADERBOARDS_URL, params)

    # If the parameters given aren't valid
    try:
        leaderboard_results = json.loads(response_str)
    except:
        raise ValueError(f"API error - {response_str}")

    leaderboards = list()
    for result in leaderboard_results['resultSets']: 
        header = result['headers']
        leaderboards += [dict(zip(header, player)) 
            for player in result['rowSet']]
    return leaderboards

def _get_response(url, params):
    """Makes a request and returns the string response

    Arguments:
        url: A string for the base url.
        params: A dictionary for any queries.

    Returns:
        A string of the response decoded based on the encoding format in the 
        returned header.
    """

    response = requests.get(
        url = url,
        params = params,
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
        }
    )

    return response.content.decode(response.encoding)