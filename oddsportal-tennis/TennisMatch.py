"""
Tennis match object.
"""

from datetime import datetime
import time

MINUTES_TO_SECONDS = 60

class TennisMatch():

    def __init__(self):
        """
        Constructor.
        """

        self.start = None
        self.player1 = "None"
        self.player2 = "None"
        self.player3 = "None"
        self.player4 = "None"
        self.team1_odds = ""
        self.team2_odds = ""
        self.draw_odds = ""
        self.outcome = ""

    def set_start(self, start_time_str):
        """
        Set the match's start time from a formatted string.

        Args:
            start_time_str (str): String representing the match start time,
                expected in the format of "%d %b %Y %H:%M".
        """

        self.start = datetime.strptime(start_time_str, "%d %b %Y %H:%M")

    def set_players(self, participants):
        """
        Set the match's participating players.

        Args:
            participants (list of str): The names of team 1 and team 2, in
                that order.
        """
        if len(participants)==4:
            self.player1 = participants[0]
            self.player2 = participants[1]
            self.player3 = participants[2]
            self.player4 = participants[3]
        else:
            self.player1 = participants[0]
            self.player3 = participants[1]


    def set_outcome_from_scores(self, scores):
        """
        Set the match's outcome string, based on team 1 and team 2 scores.

        Args:
            scores (list of int): Team 1 and team 2 scores, in that order.
        """

        if scores == None or len(scores) == 0:
            self.outcome = "NONE"
        elif scores[0] == -1 and scores[1] == -1:
            self.outcome = "NONE"
        elif scores[0] > scores[1]:
            self.outcome = "TEAM1"
        elif scores[0] < scores[1]:
            self.outcome = "TEAM2"
        else:
            self.outcome = "DRAW"

    def set_odds(self, odds):
        """
        Set the odds-related fields.

        Args:
            odds (list of float): The odds od a team 1 win, a draw, and a team
                2 win, in that order.
        """

        self.team1_odds = odds[0]
        self.team2_odds = odds[1]

    def get_start_time_unix_int(self):
        """
        Get the start time of a match, as a Unix format timestamp (GMT+5).

        Returns:
            (int) Start time as a Unix timestamp.
        """

        if self.start is None:
            return 0
        return int(time.mktime(self.start.timetuple()))

    def get_end_time_unix_int(self):
        """
        Get the estimated end time of a game, where the estimate is the start
        time plus 90 minutes, as a Unix format timestamp (GMT+5).

        Returns:
            (int) Estimated end time as a Unix timestamp.
        """

        if self.start is None:
            return 0
        return (90 * MINUTES_TO_SECONDS) + int(time.mktime(self.start.timetuple()))

    def get_player1_string(self):
        """
        Get the name of participating player 1.

        Returns:
            (str) Name of participating player 1.
        """

        return self.player1.replace("'"," ")

    def get_player2_string(self):
        """
        Get the name of participating player 2.

        Returns:
            (str) Name of participating player 2.
        """

        return self.player2.replace("'"," ")

    def get_player3_string(self):
        """
        Get the name of participating player 3.

        Returns:
            (str) Name of participating player 3.
        """

        return self.player3.replace("'"," ")

    def get_player4_string(self):
        """
        Get the name of participating player 4.

        Returns:
            (str) Name of participating player 4.
        """

        return self.player4.replace("'"," ")

    def get_team1_odds(self):
        """
        Get the odds of a team 1 win.

        Return:
            (str) Team 1 win odds.
        """

        return self.team1_odds

    def get_team2_odds(self):
        """
        Get the odds of a team 2 win.

        Return:
            (str) Team 2 win odds.
        """

        return self.team2_odds

    def get_draw_odds(self):
        """
        Get the odds of a match draw.

        Return:
            (str) Draw odds.
        """

        return self.draw_odds

    def get_outcome_string(self):
        """
        Get the outcome as a string - TEAM1 (team 1 win), TEAM2 (team 2 win),
        DRAW (draw), and NONE (no outcome, i.e. postponement or cancellation).

        Return:
            (str) Outcome string.
        """

        return self.outcome
