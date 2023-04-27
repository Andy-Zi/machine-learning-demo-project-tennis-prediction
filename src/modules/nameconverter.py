from modules.lookups import PlayerMetadataLookUp

class nameconverter():

    def __init__(self,player_metadata_lookup:PlayerMetadataLookUp):
        self.lastname_firstname_lookup = {}
        
        for name in player_metadata_lookup.data.keys():
            name_split = name.rsplit(" ",1)
            if name_split[-1] in self.lastname_firstname_lookup:
                self.lastname_firstname_lookup[name_split[-1]].append(name)
            else:
                self.lastname_firstname_lookup[name_split[-1]] = [name]


    col=["Winner","Loser"]
    notfound = []

    def complete_name(self,row):
        found = [False] * len(self.col)
        for index,colum in enumerate(self.col):
            lastname = row[colum].rstrip().rsplit(" ",1)[0].upper()
            firstname = row[colum].rstrip(".").rsplit(" ",1)[1].upper()
            if lastname in self.lastname_firstname_lookup:
                possible_full_names = self.lastname_firstname_lookup[lastname]
                for possible_full_name in possible_full_names:
                    if(possible_full_name[0] == firstname):
                        row.at[colum] = possible_full_name
                        found[index] = True
                        break
                if not found:
                    found[index] = False
                    if row[colum] not in self.notfound:
                        self.notfound.append(row[colum])
            else:
                found[index] = False
                if row[colum] not in self.notfound:
                    self.notfound.append(row[colum])
        if False not in found:
            return row
        else:
            return 0