import requests
from pathlib import Path
import github
from tqdm import tqdm
import os
import re
import pandas as pd
import USERNAME, PASSWORD from dummyuser

class DataSource(object):
    """
    Class to retrieve Tennis data from different sources.
    """
    def __init__(self, data_dir):
        self.data_dir = data_dir
        
    def get_github_data(self,pattern,subdir):
        """
        Retrieve data from Github the https://github.com/JeffSackmann/tennis_atp repository that matches the given regex pattern.
        """
        Path(os.path.join(self.data_dir,"JeffSackmann",subdir)).mkdir(parents=True, exist_ok=True)
        repo_name = "tennis_atp"
        user = "JeffSackmann"
        try:
            g = github.Github(USERNAME, PASSWORD)
            repo = g.get_user(user).get_repo(repo_name)
            files_of_interest = [f for f in repo.get_contents("") if re.match(pattern,f.name)]
        except:
            print("Error Connecting to Github...")
            return
        for file in tqdm(files_of_interest,desc=f"Downloading {subdir} Data from Github ..."):
            try:

                    if(re.match(pattern,file.name)):
                        filename = os.path.join(self.data_dir,"JeffSackmann",subdir,file.name)
                        if not os.path.exists(filename):
                            url = f"https://raw.githubusercontent.com/{user}/{repo_name}/master/{file.name}"
                            r = requests.get(url)
                            if r.ok:
                                open(filename, 'wb').write(r.content)
                            else:
                                print(f"Error Downloading File {file.name}")
            except Exception as e:
                print(f"Error Downloading File {file.name}")
                print(e)
    
                
    def get_tennis_data_uk_data(self,start_year=2000,end_year=2021):
        """
        Retrieves data from http://www.tennis-data.co.uk and converts it to a csv file.
        """
        years = list(range(start_year,end_year+1))
        Path(os.path.join(self.data_dir,"tennis_data_uk")).mkdir(parents=True, exist_ok=True)
        url = 'http://www.tennis-data.co.uk'
        for year in tqdm(years,desc="Downloading Data from Tennis-Data.co.uk ..."):
            if year < 2013:
                extention = "xls"
            else:
                extention = "xlsx"
            try:
                filename = os.path.join(self.data_dir,"tennis_data_uk",f"{year}.csv")
                if not os.path.exists(filename):
                    r = requests.get(f"{url}/{year}/{year}.{extention}", allow_redirects=True)
                    data = pd.read_excel(r.content)
                    data.to_csv(os.path.join(filename),index=False)
            except Exception as e:
                print(f"Error Downloading File {year}.{extention}")
                print(e)
           

#If this file is run as a script execute the get_data function           
if __name__ == "__main__":
    dataSource =  DataSource(r"./data")
    dataSource.get_tennis_data_uk_data()
    dataSource.get_github_data()