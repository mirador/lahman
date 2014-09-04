'''
Creates Mirador dataset from Lahman data in csv format.

@copyright: Fathom Information Design 2014
'''

import sys
import csv
from sets import Set

#http://seanlahman.com/files/database/lahman-csv_2014-02-14.zip

source_folder = '2012/'

master_data = []
reader = csv.reader(open(source_folder + 'Master.csv', 'r'), dialect='excel')
reader.next()
for row in reader:
    master_data.append(row)

master_columns = []
master_names = []
master_titles = []
reader = csv.reader(open('Master-columns.tsv', 'r'), dialect='excel-tab')
for row in reader:
    master_columns.append(int(row[0]))
    master_names.append(row[1])
    master_titles.append(row[2])
master_names.extend(['yearID', 'stint', 'teamID', 'lgID']);
master_titles.extend(['Year', "player's stint", 'Team', 'League']);

batting_data = []
reader = csv.reader(open(source_folder + 'Batting.csv', 'r'), dialect='excel')
reader.next()
for row in reader:
    batting_data.append(row)

batting_columns = []
batting_names = []
batting_titles = []
reader = csv.reader(open('Batting-columns.tsv', 'r'), dialect='excel-tab')
for row in reader:
    batting_columns.append(int(row[0]))
    batting_names.append(row[1])
    batting_titles.append(row[2])

fielding_data = []
reader = csv.reader(open(source_folder + 'Fielding.csv', 'r'), dialect='excel')
reader.next()
for row in reader:
    fielding_data.append(row)

fielding_columns = []
fielding_names = []
fielding_titles = []
reader = csv.reader(open('Fielding-columns.tsv', 'r'), dialect='excel-tab')
for row in reader:
    fielding_columns.append(int(row[0]))
    fielding_names.append(row[1])
    fielding_titles.append(row[2])

pitching_data = []
reader = csv.reader(open(source_folder + 'Pitching.csv', 'r'), dialect='excel')
reader.next()
for row in reader:
    pitching_data.append(row)
    
pitching_columns = []
pitching_names = []
pitching_titles = []
reader = csv.reader(open('Pitching-columns.tsv', 'r'), dialect='excel-tab')
for row in reader:
    pitching_columns.append(int(row[0]))
    pitching_names.append(row[1])
    pitching_titles.append(row[2])

all_names = master_names
all_names.extend(batting_names)
all_names.extend(fielding_names)
all_names.extend(pitching_names)
# print len(all_names)

writer = csv.writer(open('mirador/data.tsv', 'w'), dialect='excel-tab')    
writer.writerow(all_names)

num_players = len(master_data)
count = 0
for row in master_data:
    mrow = [val if val != '' else '\N' for val in row]
    id = mrow[0]
    cid = mrow[1]
    
    years_active = Set([])
    yearly_batting_data = {}
    yearly_fielding_data = {}    
    yearly_pitching_data = {} 
    
    for brow in batting_data:
        if brow[0] == cid:
            year = brow[1]
            yearly_batting_data[year] = [val if val != '' else '\N' for val in brow]
            years_active.add(year)
            
    for frow in fielding_data:
        if frow[0] == cid:
            year = frow[1]
            yearly_fielding_data[year] = [val if val != '' else '\N' for val in frow]
            years_active.add(year)
            
    for prow in pitching_data:
        if prow[0] == cid:
            year = prow[1]
            yearly_pitching_data[year] = [val if val != '' else '\N' for val in prow]
            years_active.add(year)
            
    count = count + 1
    years_active = sorted(years_active, key=lambda item: (int(item), item))
        
    for year in years_active:
        all_row = []
        
#         print "YEAR",year,"*************"
        
        for col in master_columns:
            all_row.append(mrow[col])
                    
        stint = '\N'
        team = '\N'        
        league = '\N'
                                    
        if year in yearly_batting_data: 
            brow = yearly_batting_data[year]
            stint = brow[2]
            team = brow[3]
            league = brow[4]
            for col in batting_columns:
                all_row.append(brow[col])
        else:
            all_row.extend(['\N'] * len(batting_columns))
            
        if year in yearly_fielding_data: 
            frow = yearly_fielding_data[year]            
            stint = frow[2]
            team = frow[3]
            league = frow[4]
            for col in fielding_columns:
                all_row.append(frow[col])
        else:
            all_row.extend(['\N'] * len(fielding_columns))

        if year in yearly_pitching_data: 
            prow = yearly_pitching_data[year]
            stint = prow[2]
            team = prow[3]
            league = prow[4]
            for col in pitching_columns:
                all_row.append(prow[col])
        else:
            all_row.extend(['\N'] * len(pitching_columns))

        all_row.insert(len(master_columns), year)
        all_row.insert(len(master_columns) + 1, stint)
        all_row.insert(len(master_columns) + 2, team)        
        all_row.insert(len(master_columns) + 2, league)
        
        writer.writerow(all_row)

    print str(count) + "/" + str(num_players)
