'''
Creates Mirador dataset from Lahman data in csv format.

@copyright: Fathom Information Design 2014
'''

import sys, os, csv, codecs
from xml.dom.minidom import parseString
from sets import Set

def write_xml_line(line, xml_file, xml_strings):
    ascii_line = ''.join(char for char in line if ord(char) < 128)
    if len(ascii_line) < len(line):
        print "  Warning: non-ASCII character found in line: '" + line.encode('ascii', 'ignore') + "'"
    xml_file.write(ascii_line + '\n')
    xml_strings.append(ascii_line + '\n')

def init_dataset(output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Remove binary file, just in case
    if os.path.isfile(output_folder + 'data.bin'):
        os.remove(output_folder + 'data.bin')

    # Creating Mirador configuration file
    template_config = "config.mira"
    project_config = output_folder + "/config.mira"

    template_file = open(template_config, 'r')
    project_file = open(project_config, 'w')
    lines = template_file.readlines()
    for line in lines:
        line = line.strip()
        if line == "project.title=":
            line = line + "Lahman's Baseball Database " + year
        project_file.write(line + '\n') 
    template_file.close()
    project_file.close()

def read_master(data_file, table_file, data, columns, names, titles, types):
    reader = csv.reader(open(data_file, 'r'), dialect='excel')
    reader.next()
    for row in reader:
        data.append(row)
    reader = csv.reader(open(table_file, 'r'), dialect='excel-tab')
    col = 0
    for row in reader:
        if len(row) == 3:
            columns.append(col)
            names.append(row[0].strip())
            titles.append(row[1].strip())
            types.append(row[2].strip())
        col = col + 1

def read_table(data_file, table_file, data, columns, names, titles, types, idcol, prefix):
    reader = csv.reader(open(data_file, 'r'), dialect='excel')
    reader.next()
    for row in reader:
        id = row[idcol]
        if id in data:
            pdat = data[id]
        else:
            pdat = []
            data[id] = pdat
        pdat.append(row)
    reader = csv.reader(open(table_file, 'r'), dialect='excel-tab')
    col = 0
    for row in reader:
        if len(row) == 3:
            columns.append(col)
            names.append(prefix + row[0].strip())
            titles.append(row[1].strip())
            types.append(row[2].strip())
        col = col + 1

def read_team_names(data_file):
    # Read team names
    team_names = {}
    reader = csv.reader(open(data_file, 'r'), dialect='excel')
    reader.next()
    for row in reader:
        team_names[row[2]] = row[40]
    
def read_salaries(data_file):
    reader = csv.reader(open(data_file, 'r'), dialect='excel')
    reader.next()
    for row in reader:
        row[4] = str(float(row[4]) * 19.2)
        salary_data.append(row)
 
def write_data(filename):
    writer = csv.writer(open(filename, 'w'), dialect='excel-tab')    
    writer.writerow(all_names)
    num_players = len(master_data)
    count = 0
    lastPercPoint = 0
    for row in master_data:
        mrow = [val if val != '' else '\\N' for val in row]
        pid = mrow[0]
    
        years_active = Set([])
        yearly_batting_data = {}
        yearly_fielding_data = {}    
        yearly_pitching_data = {} 
    
        if pid in batting_data:        
            brows = batting_data[pid]
            for brow in brows:
                year = brow[1]
                yearly_batting_data[year] = [val if val != '' else '\\N' for val in brow]
                years_active.add(year)
            
        if pid in pitching_data:        
            prows = pitching_data[pid]
            for prow in prows: 
                year = prow[1]
                yearly_pitching_data[year] = [val if val != '' else '\\N' for val in prow]
                years_active.add(year)
            
        if pid in fielding_data:        
            frows = fielding_data[pid]
            for frow in frows:
                year = frow[1]
                yearly_fielding_data[year] = [val if val != '' else '\\N' for val in frow]
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
            salary = '\\N'
                                    
            if year in yearly_batting_data: 
                brow = yearly_batting_data[year]
                stint = brow[2]
                team = brow[3]
                league = brow[4]
                for col in batting_columns:
                    all_row.append(brow[col])
            else:
                all_row.extend(['\\N'] * len(batting_columns))

            if year in yearly_pitching_data: 
                prow = yearly_pitching_data[year]
                stint = prow[2]
                team = prow[3]
                league = prow[4]
                for col in pitching_columns:
                    all_row.append(prow[col])
            else:
                all_row.extend(['\\N'] * len(pitching_columns))
            
            if year in yearly_fielding_data: 
                frow = yearly_fielding_data[year]            
                stint = frow[2]
                team = frow[3]
                league = frow[4]
                for col in fielding_columns:
                    all_row.append(frow[col])
            else:
                all_row.extend(['\\N'] * len(fielding_columns))

#             if year in yearly_batting_data: 
                

            all_row.insert(len(master_columns), year)
            all_row.insert(len(master_columns) + 1, stint)
            all_row.insert(len(master_columns) + 2, team)        
            all_row.insert(len(master_columns) + 3, league)
            all_row.insert(len(master_columns) + 4, salary)            
            
            writer.writerow(all_row)
            all_data.append(all_row)

        perc = int(100 * count / num_players)
        if lastPercPoint < perc:
            print '  Completed ' + str(perc) + '%...'
            lastPercPoint = perc

def write_groups(filename):
    # Writing file in utf-8 because the input html files from
    # NHANES website sometimes have characters output the ASCII range.
    xml_file = codecs.open(filename, 'w', 'utf-8')
    xml_strings = []

    write_xml_line('<?xml version="1.0"?>', xml_file, xml_strings)

    write_xml_line('<data>', xml_file, xml_strings)
    write_xml_line(' <group name="Player info">', xml_file, xml_strings)
    write_xml_line('  <table name="Vitals">', xml_file, xml_strings)
    for name in master_names[0: len(master_names) - 5]:    
        write_xml_line('   <variable name="' + name + '"/>', xml_file, xml_strings)
    write_xml_line('  </table>', xml_file, xml_strings)
    write_xml_line('  <table name="Teams">', xml_file, xml_strings)
    for name in master_names[len(master_names) - 5: len(master_names)]:
        write_xml_line('   <variable name="' + name + '"/>', xml_file, xml_strings)
    write_xml_line('  </table>', xml_file, xml_strings)
    write_xml_line(' </group>', xml_file, xml_strings)

    write_xml_line(' <group name="Player stats">', xml_file, xml_strings)
    write_xml_line('  <table name="Batting">', xml_file, xml_strings)
    for name in batting_names:
        write_xml_line('   <variable name="' + name + '"/>', xml_file, xml_strings)
    write_xml_line('  </table>', xml_file, xml_strings)
    write_xml_line('  <table name="Pitching">', xml_file, xml_strings)
    for name in pitching_names:
        write_xml_line('   <variable name="' + name + '"/>', xml_file, xml_strings)
    write_xml_line('  </table>', xml_file, xml_strings)    
    write_xml_line('  <table name="Fielding">', xml_file, xml_strings)
    for name in fielding_names:
        write_xml_line('   <variable name="' + name + '"/>', xml_file, xml_strings)
    write_xml_line('  </table>', xml_file, xml_strings)
    write_xml_line(' </group>', xml_file, xml_strings)
    write_xml_line('</data>', xml_file, xml_strings)
    xml_file.close()

    # XML validation.
    try:
        doc = parseString(''.join(xml_strings))
        doc.toxml()
    except:
        sys.stderr.write('XML validation error:\n')
        raise    
    
def write_dict(dict_file):
    all_types = []
    all_types.extend(master_types)
    all_types.extend(batting_types)
    all_types.extend(pitching_types)
    all_types.extend(fielding_types)    

    all_titles = []
    all_titles.extend(master_titles)
    all_titles.extend(batting_titles)
    all_titles.extend(pitching_titles)
    all_titles.extend(fielding_titles)    

    # Initialize ranges
    all_ranges = [None] * len(all_names)

    hand = {'L':'Left', 'R':'Right', 'B':'Both'}

    for i in range(0, len(all_names)):
        name = all_names[i]
        title = all_titles[i]
        if name == 'teamID':
            range_str = ''
            for key in team_names:
                if not range_str == '': range_str = range_str + ';'
                range_str = range_str + key + ':' + team_names[key]
            all_ranges[i] = range_str
        elif all_types[i] == 'category':
            values = {}
            for row in all_data:
                if row[i] == '\\N': continue
                if 'throwing hand' in title or 'batting hand' in title:
                    values[row[i]] = hand[row[i]]
                else:
                    values[row[i]] = row[i]
            range_str = ''            
            for key in values:
                if not range_str == '': range_str = range_str + ';'
                range_str = range_str + key + ':' + values[key]
            all_ranges[i] = range_str
        elif all_types[i] == 'int':
            minVal = 1E9
            maxVal = 0
            for row in all_data:
                if row[i] == '\\N': continue
                val = int(row[i])
                if val < minVal: minVal = val
                if maxVal < val: maxVal = val
            all_ranges[i] = str(minVal) + ',' + str(maxVal)
            if maxVal < minVal:
                all_ranges[i] = '0,0'
                print "  Warning: no values found for " + name
        elif all_types[i] == 'float':
            minVal = 1E9
            maxVal = 0
            for row in all_data:
                if row[i] == '\\N': continue
                val = float(row[i])
                if val < minVal: minVal = val
                if maxVal < val: maxVal = val
            all_ranges[i] = str(minVal) + ',' + str(maxVal)
            if maxVal < minVal:
                all_ranges[i] = '0,0'
                print "  Warning: no values found for " + name
        elif 'label' in all_types[i]:
            all_ranges[i] = all_types[i]    
            all_types[i] = 'String'
          
    dfile = open(dict_file, 'w')
    for i in range(0, len(all_names)):
        line = all_titles[i] + '\t' + all_types[i] + '\t' + all_ranges[i] + '\n'
        dfile.write(line)  
    dfile.close()

##########################################################################################

year = sys.argv[1]
source_folder = 'source/' + year + '/'
output_folder = 'mirador/'

master_data = []
master_columns = []
master_names = []
master_titles = []
master_types = []

batting_data = {}
batting_columns = []
batting_names = []
batting_titles = []
batting_types = []

pitching_data = {}
pitching_columns = []
pitching_names = []
pitching_titles = []
pitching_types = []

fielding_data = {}
fielding_columns = []
fielding_names = []
fielding_titles = []
fielding_types = []

team_names = {}
salary_data = []

init_dataset(output_folder)

print 'Reading master table...'
read_master(source_folder + 'Master.csv', 'master-table.tsv', master_data, master_columns, master_names, master_titles, master_types) 
print 'Done.'
master_names.extend(['yearID', 'stint', 'teamID', 'lgID', 'salary']);
master_titles.extend(['Year', "player's stint", 'Team', 'League', 'Salary']);
master_types.extend(['int', 'int', 'category', 'category', 'float']);

print 'Reading batting table...'
read_table(source_folder + 'Batting.csv', 'batting-table.tsv', batting_data, batting_columns, batting_names, batting_titles, batting_types, 0, 'BAT.')    
print 'Done.'

print 'Reading pitching table...'
read_table(source_folder + 'Pitching.csv', 'pitching-table.tsv', pitching_data, pitching_columns, pitching_names, pitching_titles, pitching_types, 0, 'PITCH.')
print 'Done.'

print 'Reading fielding table...'
read_table(source_folder + 'Fielding.csv', 'fielding-table.tsv', fielding_data, fielding_columns, fielding_names, fielding_titles, fielding_types, 0, 'FIELD.')
print 'Done.'

print 'Reading team names...'
read_team_names(source_folder + 'Teams.csv')
print 'Done.'

print 'Reading salaries...'
read_salaries(source_folder + 'Salaries.csv')
print 'Done.'

all_data = []
all_names = []
all_names.extend(master_names)
all_names.extend(batting_names)
all_names.extend(pitching_names)
all_names.extend(fielding_names)

print 'BUILDING MIRADOR DATASET...'
print '  Writing data file...'
write_data(output_folder + 'data.tsv')
print '  Done.'
print '  Writing groups file...'
write_groups(output_folder + 'groups.xml')
print '  Done.'
print '  Writing dictionary file...'
write_dict(output_folder + 'dictionary.tsv')
print '  Done.'
print 'DATASET READY.'