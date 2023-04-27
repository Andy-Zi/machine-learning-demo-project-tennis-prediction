import os 
import json
from tkinter.messagebox import NO
import pandas as pd
from tqdm import tqdm
import datetime

class BaseLookup(object):
    def __init__(self,directory,filename) -> None:
        super().__init__()
        self.directory = directory
        self.filename = filename
        self.dateColumn = None
        self.data = None
        
    def load(self,df:pd.DataFrame)->dict:
        """
        Takes a dataframe and builds the lookup dictionary
        """
        file = os.path.join(self.directory, self.filename)
        if not os.path.exists(file):
            data = self._build(df)
            open(file, "w").write(json.dumps(data, indent=4))
        self.data = json.load(open(file), object_hook=self.date_hook_date)
        print(f"Loaded {type(self).__name__} from {self.filename}")
        return self.data
            
            
    def _build(self,df:pd.DataFrame)->dict:
        return None
    
    def __getitem__(self, key):
        return self._getitem(key)
    
    def _getitem(self, key:str):
        return None
    
    def date_hook_date(self,json_dict):
        """
        Datetime hook for the json.load
        """
        try:
            json_dict[self.dateColumn] = datetime.datetime.strptime(json_dict[self.dateColumn], "%Y-%m-%d").date()
        except:
            pass
        return json_dict
    
class PlayerRankLookUp(BaseLookup):
    """
    Lookup that maps Player IDs to their Rankings in different Time periodes
    """
    def __init__(self, directory) -> None:
        super().__init__(directory, "player_rank_lookup.json")
        self.dateColumn = "date"
        
        
    def _build(self, df: pd.DataFrame) -> dict:
        data = {}
        #Group the Dataframe by Player IDS
        players_grouped = df.groupby([df["player"]])
        for player_id, ranking in tqdm(players_grouped,desc="Building Player Ranking Lookup ..."):
            ranking.drop(["player"],axis=1,inplace=True)
            #Ensure sorting by Datetimes
            ranking = ranking.sort_values(by=["ranking_date"])
            entries = []
            #Append all Entries to the Lookup 
            for i, row in ranking.iterrows():
                entries.append({
                    "date":row["ranking_date"].strftime("%Y-%m-%d"),
                    "rank":int(row["rank"]),
                    "points":row["points"]
                    })    
            data[int(player_id)] = entries
        return data
    
    def _getitem(self, key:str):
        return self.data[str(key)]
    
    def getRank(self,id,date:datetime=None)->int:
        """
        Returns the Rank of the Player at the given Date
        """
        id = str(id)
        if id not in self.data:
            return -1 #very high number to ensure last place in WorldRanking
        
        if date is None:
            return self.data[id][-1]["rank"]
        
        difference =  datetime.timedelta.max
        rank = -1
        for entry in self.data[id]:
            new_delta = abs(entry["date"] - date)
            if new_delta < difference:
                difference = new_delta
                rank = entry["rank"]
        return rank
                
    
    
class PlayerMetadataLookUp(BaseLookup):
    """
    Lookup that maps the a Players Name to their Metadata (ID,Height,Country of Origin,Date of Birth)
    """
    def __init__(self, directory) -> None:
        super().__init__(directory, "player_metadata_lookup.json")
        self.dateColumn = "dob"
        
    def _build(self, df: pd.DataFrame) -> dict:
        
        data = {}
        duplicated_counter = 0
        #Iterate over all players
        for i, row in tqdm(df.iterrows(),desc="Building Player Meatdata Lookup ..."):
            #Build their full name
            name = f"{row['name_first']} {row['name_last']}".upper()
            if name in data:
                duplicated_counter += 1
            #Players are ordered by their Date of Birth (ascending) -> if we have a Duplicated Name we use the younger athlete because he/she is more likely to still play today
            data[name] = {
                "id":row["player_id"],
                "height":row["height"],
                "hand":row["hand"],
                "dob":row["dob"].strftime("%Y-%m-%d"),
                "country":row["ioc"]
                }
        if duplicated_counter > 0:
            print("Warning: There are {} Duplicated Player Names, these Players were ignored and are not present in the Lookup!".format(duplicated_counter))
        return data
    
        
    def _getitem(self, key:str):
        return self.data[key.upper()]
    
    
class PlayerMatchHistoryLookUp(BaseLookup):
    """
    Lookup that holds all the Match history of a Player
    """
    def __init__(self, directory,player_metadata_lookup:PlayerMetadataLookUp) -> None:
        super().__init__(directory, "player_matchHistory_lookup.json")
        self.player_metadata_lookup = player_metadata_lookup
        self.dateColumn = "date"
        
    def _build(self, df: pd.DataFrame)-> dict:
        data={}
        self.skipedcounter = 0
        def add_match(player,opponent,date,score,best_of,won):
            
            if player not in self.player_metadata_lookup.data or opponent not in self.player_metadata_lookup.data:
                self.skipedcounter += 1
                return
            
            if player not in data:
                data[player] = {}
            if opponent not in data[player]:
                data[player][opponent] = []
            data[player][opponent].append({
                "won":won,
                "date":date,
                "score":score,
                "best_of":best_of
            })
            
        for _, row in tqdm(df.iterrows(),desc="Building Player MatchHistory Lookup ..."):
            winner = str(row["winner_name"]).upper()
            loser = str(row["loser_name"]).upper()
            date = row["tourney_date"].strftime("%Y-%m-%d")
            score = str(row["score"])
            best_of = int(row["best_of"])
            
            #Add the Match to both Players
            add_match(winner,loser,date,score,best_of,True)
            add_match(loser,winner,date,score,best_of,False)
        
        if self.skipedcounter > 0:
            print("Skipped {} Matches because one of the Players was not present in the PlayerMetadataLookup!".format(self.skipedcounter))
        return data
    
    def _getitem(self, key:str):
        return self.data[key.upper()]
    
    
    def getMatchHistory(self,player:str,opponent:str, date:datetime=None):
        """
        Gets the Match History between the given players up the the provided date
        """
        player = player.upper()
        opponent = opponent.upper()
        if player not in self.data or opponent not in self.data[player]:
            return []
        if date is None:
            return self.data[player][opponent]
        else:
            return [match for match in self.data[player][opponent] if match["date"] <= date]
        
    def getAllMatches(self,player:str,date:datetime=None):
        player = player.upper()
        if player not in self.data:
            return []
        matches = []
        for opponent in self.data[player]:
            matches += self.data[player][opponent]
        
        if date is None:
            return matches
        return [match for match in matches if match["date"] <= date]
            
            
            