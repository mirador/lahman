'''
Creates Mirador dataset from Lahman data in csv format.

@copyright: Fathom Information Design 2014
'''

import sys, os, csv, codecs
from xml.dom.minidom import parseString
from sets import Set

def write_xml_line(line):
    ascii_line = ''.join(char for char in line if ord(char) < 128)
    if len(ascii_line) < len(line):
        print "  Warning: non-ASCII character found in line: '" + line.encode('ascii', 'ignore') + "'"
    xml_file.write(ascii_line + '\n')
    xml_strings.append(ascii_line + '\n')

#http://seanlahman.com/files/database/lahman-csv_2014-02-14.zip

source_folder = 'source/test/'
output_folder = 'mirador/'

master_data = []
reader = csv.reader(open(source_folder + 'Master.csv', 'r'), dialect='excel')
reader.next()
for row in reader:
    master_data.append(row)

master_columns = []
master_names = []
master_titles = []
master_types = []
reader = csv.reader(open('Master-columns.tsv', 'r'), dialect='excel-tab')
for row in reader:
    master_columns.append(int(row[0]))
    master_names.append(row[1])
    master_titles.append(row[2])
    master_types.append(row[3])
master_names.extend(['yearID', 'stint', 'teamID', 'lgID']);
master_titles.extend(['Year', "player's stint", 'Team', 'League']);
master_types.extend(['int', 'int', 'category', 'category']);
  
# salaries_data = []
# reader = csv.reader(open(source_folder + 'Salaries.csv', 'r'), dialect='excel')
# reader.next()
# for row in reader:
#     salaries_data.append(row)    
  
batting_data = []
reader = csv.reader(open(source_folder + 'Batting.csv', 'r'), dialect='excel')
reader.next()
for row in reader:
    batting_data.append(row)

batting_columns = []
batting_names = []
batting_titles = []
batting_types = []
reader = csv.reader(open('Batting-columns.tsv', 'r'), dialect='excel-tab')
for row in reader:
    batting_columns.append(int(row[0]))
    batting_names.append(row[1])
    batting_titles.append(row[2])
    batting_types.append(row[3])
        
fielding_data = []
reader = csv.reader(open(source_folder + 'Fielding.csv', 'r'), dialect='excel')
reader.next()
for row in reader:
    fielding_data.append(row)

fielding_columns = []
fielding_names = []
fielding_titles = []
fielding_types = []
reader = csv.reader(open('Fielding-columns.tsv', 'r'), dialect='excel-tab')
for row in reader:
    fielding_columns.append(int(row[0]))
    fielding_names.append(row[1])
    fielding_titles.append(row[2])
    fielding_types.append(row[3]) 

pitching_data = []
reader = csv.reader(open(source_folder + 'Pitching.csv', 'r'), dialect='excel')
reader.next()
for row in reader:
    pitching_data.append(row)
    
pitching_columns = []
pitching_names = []
pitching_titles = []
pitching_types = []
reader = csv.reader(open('Pitching-columns.tsv', 'r'), dialect='excel-tab')
for row in reader:
    pitching_columns.append(int(row[0]))
    pitching_names.append(row[1])
    pitching_titles.append(row[2])
    pitching_types.append(row[3])

all_names = []
all_names.extend(master_names)
all_names.extend(batting_names)
all_names.extend(fielding_names)
all_names.extend(pitching_names)

print "Creating data file..."
writer = csv.writer(open(output_folder + 'data.tsv', 'w'), dialect='excel-tab')    
writer.writerow(all_names)
num_players = len(master_data)
count = 0
all_data = []
for row in master_data:
    mrow = [val if val != '' else '\\N' for val in row]
    id = mrow[0]
    cid = mrow[1]
    
    years_active = Set([])
    yearly_batting_data = {}
    yearly_fielding_data = {}    
    yearly_pitching_data = {} 
    
    for brow in batting_data:
        if brow[0] == cid:
            year = brow[1]
            yearly_batting_data[year] = [val if val != '' else '\\N' for val in brow]
            years_active.add(year)
            
    for frow in fielding_data:
        if frow[0] == cid:
            year = frow[1]
            yearly_fielding_data[year] = [val if val != '' else '\\N' for val in frow]
            years_active.add(year)
            
    for prow in pitching_data:
        if prow[0] == cid:
            year = prow[1]
            yearly_pitching_data[year] = [val if val != '' else '\\N' for val in prow]
            years_active.add(year)
            
    count = count + 1
    years_active = sorted(years_active, key=lambda item: (int(item), item))
        
    for year in years_active:
        all_row = []
        
        for col in master_columns:
            all_row.append(mrow[col])
                    
        stint = '\\N'
        team = '\\N'        
        league = '\\N'
                                    
        if year in yearly_batting_data: 
            brow = yearly_batting_data[year]
            stint = brow[2]
            team = brow[3]
            league = brow[4]
            for col in batting_columns:
                all_row.append(brow[col])
        else:
            all_row.extend(['\\N'] * len(batting_columns))
            
        if year in yearly_fielding_data: 
            frow = yearly_fielding_data[year]            
            stint = frow[2]
            team = frow[3]
            league = frow[4]
            for col in fielding_columns:
                all_row.append(frow[col])
        else:
            all_row.extend(['\\N'] * len(fielding_columns))

        if year in yearly_pitching_data: 
            prow = yearly_pitching_data[year]
            stint = prow[2]
            team = prow[3]
            league = prow[4]
            for col in pitching_columns:
                all_row.append(prow[col])
        else:
            all_row.extend(['\\N'] * len(pitching_columns))

        all_row.insert(len(master_columns), year)
        all_row.insert(len(master_columns) + 1, stint)
        all_row.insert(len(master_columns) + 2, team)        
        all_row.insert(len(master_columns) + 2, league)
        
        writer.writerow(all_row)
        all_data.append(all_row)
        
    perc = int(100 * count / num_players)      
    if perc % 10 == 0:
        print "  " + str(perc) + "% completed"
print "Done."        

# Remove binary file, just in case
if os.path.isfile(output_folder + 'data.bin'):
    os.remove(output_folder + 'data.bin')


# Writing file in utf-8 because the input html files from
# NHANES website sometimes have characters output the ASCII range.
xml_file = codecs.open(output_folder + 'groups.xml', 'w', 'utf-8')
xml_strings = []

write_xml_line('<?xml version="1.0"?>')

print "Creating groups file..."
write_xml_line('<data>')
write_xml_line(' <group name="Player info">')
write_xml_line('  <table name="Vitals">')
for name in master_names[0: len(master_names) - 4]:
    write_xml_line('   <variable name="' + name + '"/>')
write_xml_line('  </table>') 
write_xml_line('  <table name="Teams">')
for name in master_names[len(master_names) - 4: len(master_names)]:
    write_xml_line('   <variable name="' + name + '"/>')
write_xml_line('  </table>')
write_xml_line(' </group>')

write_xml_line(' <group name="Player stats">')
write_xml_line('  <table name="Batting">')
for name in batting_names:
    write_xml_line('   <variable name="' + name + '"/>')
write_xml_line('  </table>')
write_xml_line('  <table name="Fielding">')
for name in fielding_names:
    write_xml_line('   <variable name="' + name + '"/>')
write_xml_line('  </table>')
write_xml_line('  <table name="Pitching">')
for name in pitching_names:
    write_xml_line('   <variable name="' + name + '"/>')
write_xml_line('  </table>')
write_xml_line(' </group>')
write_xml_line('</data>')    
xml_file.close()

# XML validation.
try:
    doc = parseString(''.join(xml_strings))
    doc.toxml()
    print 'Done.' 
except:
    sys.stderr.write('XML validation error:\n')
    raise

all_types = []
all_types.extend(master_types)
all_types.extend(batting_types)
all_types.extend(fielding_types)
all_types.extend(pitching_types)

all_titles = []
all_titles.extend(master_titles)
all_titles.extend(batting_titles)
all_titles.extend(fielding_titles)
all_titles.extend(pitching_titles)

#print all_names
#print all_types
#print all_titles

print "Creating dictionary file..."

# Initialize ranges
all_ranges = {}

# Get team names
team_names = {}
reader = csv.reader(open(source_folder + 'Teams.csv', 'r'), dialect='excel')
reader.next()
for row in reader:
    team_names[row[2]] = row[40]

for i in range(0, len(all_names)):
    name = all_names[i]
    if name == 'teamID':
        all_ranges[name] = team_names    
    elif all_types[i] == 'category':
        values = {}
        for row in all_data:
            if row[i] == '\\N': continue
            values[row[i]] = row[i]
        all_ranges[name] = values                
    elif all_types[i] == 'int':
        minVal = 1E9
        maxVal = 0
        for row in all_data:
            if row[i] == '\\N': continue
            val = int(row[i])
            if val < minVal: minVal = val
            if maxVal < val: maxVal = val
        all_ranges[name] = [minVal, maxVal]
        if maxVal < minVal:
            all_ranges[name] = [0, 0]
            print "  Warning: no values found for " + name        
    elif all_types[i] == 'float':
        minVal = 1E9
        maxVal = 0
        for row in all_data:
            if row[i] == '\\N': continue
            val = float(row[i])
            if val < minVal: minVal = val
            if maxVal < val: maxVal = val
        all_ranges[name] = [minVal, maxVal]        
        if maxVal < minVal:
            all_ranges[name] = [0, 0] 
            print "  Warning: no values found for " + name
    elif 'label' in all_types[i]:
        all_ranges[name] = all_types[i]    
        all_types[i] = 'String'
          
          
          
#all_ranges['lgID'] = {}
#print team_names
#print all_ranges

print "Done."