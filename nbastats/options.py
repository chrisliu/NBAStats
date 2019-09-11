class Season(object):
    """A representation of a NBA season"""

    def __init__(self, season_year):
        """Initializes a Season representation.

        Arguments:
            season_year: An integer for the year the season begins.
        """
        self.season_year = season_year

    def __str__(self):
        """Returns a string representation of the season.

        Returns:
            A string in the format 'AABB-CC' where a year is represented
            by 'AABB' and CC is BB + 1 
        """
        return f'{self.season_year}-{self.season_year % 100 + 1}'

class SeasonType():
    """The string representation for each stage of a NBA season used by the NBA stats api."""
    
    PRE_SEASON = 'Pre Season'
    REGULAR_SEASON = 'Regular Season'
    PLAYOFFS = 'Playoffs'
    ALL_STAR = 'All Star'

class LeaderboardSortCategory():
    """The string representation for each category that leaders could be sorted by"""

    MINUTES_PLAYED = 'MIN'
    OFFENSIVE_REBOUNDS = 'OREB'
    DEFENSIVE_REBOUNDS = 'DREB'
    REBOUNDS = 'REB'
    ASSISTS = 'AST'
    STEALS = 'STL'
    BLOCKS = 'BLK'
    TURNOVERS = 'TOV'
    EFFICIENCY = 'EFF'
    POINTS = 'PTS'