from typing import List,Tuple

class ScoreParser(object):
    """
    Class tho handle Scores in a more generic way
    """
    def __init__(self) -> None:
        super().__init__()
        
        
    def parse_string(self,string:str)->Tuple[int,int]:
        """
        Parses A Score from a String Format like "7-5 4-6 6-2" int a Tuple of (Player 1 Score, Player 2 Score)
        """
        return self.parse(string.split(" "))
        
    def parse(self,sets:List[str])->Tuple[int,int]:
        """
        Parses A Score from a String Format like "7-5 4-6 6-2" int a Tuple of (Player 1 Score, Player 2 Score)
        """
        player_1_score = 0
        player_2_score = 0
        try:
            for set in sets:
                set = set.strip()
                #Ignore Retirements and No Contests 
                if set == "RET" or set == "W/O" or set == 'UN':
                    continue
                
                separator_index = set.find('-')
                player_1_points = int(set[:separator_index])
                if "(" in set:
                    #Sometimes there is a ( in the score we ignore it here
                    player_2_points = int(set[separator_index+1:set.find('(')])
                else:
                    player_2_points = int(set[separator_index+1:])
                    
                if player_1_points > player_2_points:
                    #player 1 won the Set
                    player_1_score += 1
                elif player_2_points > player_1_points:
                    #player 2 won the Set
                    player_2_score += 1
        except:
            return -1,-1
        
        return player_1_score,player_2_score
    
    def encode(self,player_1_score:int,player_2_score:int,sets:int)->float:
        """
        Encodes a Set with Scores into a Float between 0 and 1
        """
        score = 0.0 if player_1_score > player_2_score else 1.0
        setmargin = 1.0/sets
        if score > 0.0:
            score -= player_1_score*setmargin
        else:
            score += player_2_score*setmargin
        
        return score

    def decode(self,score:float,sets:int)->Tuple[int,int]:
        """
        Takes a Score Encoded as a Float and returns the Scores as a Tuple of (Player 1 Score, Player 2 Score)
        """
        player_1_score = 0
        player_2_score = 0
        set_win_points = int(sets/2.0)+1
        setmargin = 1.0/sets
        if score > 0.5:
            player_2_score = set_win_points
            player_1_score = int(round((1.0-score) / setmargin,0))
        else:
            player_1_score = set_win_points
            player_2_score = int(score / setmargin)
        return player_1_score,player_2_score
    
if __name__ == "__main__":
    parser = ScoreParser()
    print("Parsing Tests")        
    print(parser.parse("7-5 4-6 6-2".split(" ")))
    print(parser.parse("7-5 6-7(4) 6-4 6-4".split(" ")))
    print(parser.parse("7-6(5) 2-0 RET".split(" ")))
    print("Encode/Decode Tests")
    print(parser.decode(parser.encode(2,0,3),3))
    print(parser.decode(parser.encode(2,1,3),3))
    print(parser.decode(parser.encode(1,2,3),3))
    print(parser.decode(parser.encode(1,3,5),5))
    print(parser.decode(parser.encode(2,3,5),5))
    print(parser.decode(parser.encode(3,2,5),5))