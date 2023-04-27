import pandas as pd
from tqdm import tqdm
from random import random
from modules.scoreparser import ScoreParser
from modules.lookups import PlayerMatchHistoryLookUp,PlayerMetadataLookUp,PlayerRankLookUp
from modules.gaps import *
from datetime import datetime

def transform_jeffSackmann(df: pd.DataFrame,scoreParser:ScoreParser,player_match_history_lookup:PlayerMatchHistoryLookUp) -> pd.DataFrame:
    """
    
    """
    columns=["date","seedgap","skillgap","agegap","heightgap","knowledgegap","historicalgap","best_of","score","score_b"]
    rows = []

    for i,row in tqdm(df.iterrows(),total=len(df),desc="Building Train-Dataframe ..."):
        
        p1_score,p2_score = scoreParser.parse_string(str(row["score"]))
        if p1_score == -1:
            #Invalide Score Format
            continue
        
        
        def cleanup_seed(seed):
            if pd.isna(seed):
                return None
            else:
                try:
                    return int(seed)
                except:
                    return None
                
        date = row["tourney_date"]
        # randomly chose if the winner is player 1 or player 2
        # we don't want the model to be biased towards either player
        if random() > 0.5:
            p1_name = row["winner_name"]
            p1_seed = cleanup_seed(row["winner_seed"])
            p1_age = row["winner_age"]
            p1_height = row["winner_ht"]
            p1_rank = row["winner_rank"]
            
            p2_name = row["loser_name"]
            p2_seed = cleanup_seed(row["loser_seed"])
            p2_age = row["loser_age"]
            p2_height = row["loser_ht"]
            p2_rank = row["loser_rank"]
        else:
            #We need to Flip the score Here
            temp_sore = p1_score
            p1_score = p2_score
            p2_score = temp_sore
            
            p1_name = row["loser_name"]
            p1_seed = cleanup_seed(row["loser_seed"])
            p1_age = row["loser_age"]
            p1_height = row["loser_ht"]
            p1_rank = row["loser_rank"]
            
            p2_name = row["winner_name"]
            p2_seed = cleanup_seed(row["winner_seed"])
            p2_age = row["winner_age"]
            p2_height = row["winner_ht"]
            p2_rank = row["winner_rank"]
            
        
        #We need to calculate the gaps here
        knowledgegap = knowledge_gap(len(player_match_history_lookup.getAllMatches(p1_name,date)),len(player_match_history_lookup.getAllMatches(p2_name,date)))
        historical_matches = player_match_history_lookup.getMatchHistory(p1_name,p2_name,date)
        if len(historical_matches) == 0:
            historicalgap = 0.5 # no information  
        else:
            p1_wins = len([match for match in historical_matches if match["won"]])
            p2_wins = len([match for match in historical_matches if not match["won"]])
            historicalgap = historical_gap(p1_wins,p2_wins)
        
        if p1_seed == None and p2_seed == None:
            seedgap = 0.5
        elif p1_seed == None and p2_seed != None:
            seedgap = 1.0
        elif p1_seed != None and p2_seed == None:
            seedgap = 0.0  
        else:
            seedgap = seed_gap(p1_seed,p2_seed)
            
        skillgap = skill_gap(p1_rank,p2_rank)
        heightgap = height_gap(p1_height,p2_height)
        agegap = age_gap(p1_age,p2_age)
        best_of = int(row["best_of"])
        score = scoreParser.encode(p1_score,p2_score,best_of)
        score_binary = 0 if score < 0.5 else 1
        
        rows.append([
            date,
            seedgap,
            skillgap,
            agegap,
            heightgap,
            knowledgegap,
            historicalgap,
            row["best_of"],
            score,
            score_binary
        ])

    return pd.DataFrame(rows,columns=columns)  


def transform_tennisData_UK(df: pd.DataFrame,scoreParser:ScoreParser,player_match_history_lookup:PlayerMatchHistoryLookUp,player_metadata_lookup:PlayerMetadataLookUp,player_rank_lookup:PlayerRankLookUp) -> pd.DataFrame:
    columns=["date","seedgap","skillgap","agegap","heightgap","knowledgegap","historicalgap","best_of","score","score_b","p1_odds","p2_odds","betting_score"]
    rows = []
    skillgapMissing = 0
    for i,row in tqdm(df.iterrows(),total=len(df),desc="Building Evaluation-Dataframe ..."):
        
        p1_score,p2_score = scoreParser.parse_string(str(row["score"]))
        if p1_score == -1:
            #Invalide Score Format
            continue
        
        date = row["Date"].date()
        

        # randomly chose if the winner is player 1 or player 2
        # we don't want the model to be biased towards either player
        if random() > 0.5:
            p1_name = row["Winner"]
            p1_odds = row["odds_winner"]
            
            p2_name = row["Loser"]
            p2_odds = row["odds_loser"]
        else:
            #We need to Flip the score Here
            temp_sore = p1_score
            p1_score = p2_score
            p2_score = temp_sore
            
            p1_name = row["Loser"]
            p1_odds = row["odds_loser"]
            
            p2_name = row["Winner"]
            p2_odds = row["odds_winner"]
           
            
        p1_metadata = player_metadata_lookup[p1_name]
        p2_metadata = player_metadata_lookup[p2_name]
        
        p1_id = str(p1_metadata["id"])
        p2_id = str(p2_metadata["id"])
        
        p1_rank = player_rank_lookup.getRank(p1_id,date)
        p2_rank = player_rank_lookup.getRank(p2_id,date)
        
        p1_age = (date - p1_metadata["dob"]).days // 365
        p1_height = p1_metadata["height"]
        
        p2_age = (date - p2_metadata["dob"]).days // 365
        p2_height = p2_metadata["height"]
        
        #We need to calculate the gaps here
        knowledgegap = knowledge_gap(len(player_match_history_lookup.getAllMatches(p1_name,date)),len(player_match_history_lookup.getAllMatches(p2_name,date)))
        historical_matches = player_match_history_lookup.getMatchHistory(p1_name,p2_name,date)
        if len(historical_matches) == 0:
            historicalgap = 0.5 # no information  
        else:
            p1_wins = len([match for match in historical_matches if match["won"]])
            p2_wins = len([match for match in historical_matches if not match["won"]])
            historicalgap = historical_gap(p1_wins,p2_wins)
        
        seedgap = 0.5
  
            
        if p1_rank == -1 or p2_rank == -1:
            skillgapMissing +=1
            skillgap = 0.5
        else:
            skillgap = skill_gap(p1_rank,p2_rank)
            
        heightgap = height_gap(p1_height,p2_height)
        agegap = age_gap(p1_age,p2_age)
        best_of = int(row["Best of"])
        score = scoreParser.encode(p1_score,p2_score,best_of)
        score_binary = 0 if score < 0.5 else 1
        
        rows.append([
            date,
            seedgap,
            skillgap,
            agegap,
            heightgap,
            knowledgegap,
            historicalgap,
            best_of,
            score,
            score_binary,
            p1_odds,
            p2_odds,
            0 if p1_odds < p2_odds else 1
        ])
        
    print(f"Missing Skill Gap: {skillgapMissing}")    
    return pd.DataFrame(rows,columns=columns)  
    