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
            line = line + "Lahman`s Baseball Database " + year
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
    reader = csv.reader(open(data_file, 'r'), dialect='excel')
    reader.next()
    for row in reader:
        team_names[row[2]] = row[40]
    
def read_salaries(data_file, cpi_file):
    cpi = {}
    reader = csv.reader(open(cpi_file, 'r'), dialect='excel-tab')
    for row in reader:
        cpi[row[0]] = float(row[1])
        
    no_cpi_warning = False    
    reader = csv.reader(open(data_file, 'r'), dialect='excel')
    reader.next()
    for row in reader:
        id = row[3]
        year = row[0]
        # Salary in constant dollars:
        # http://www.uri.edu/artsci/newecn/Classes/Art/306a/Outlines/BasicQuest/inflation_adjustments.htm
        if year in cpi:
            salary = 100 * float(row[4]) / cpi[year]
        else:
            if not no_cpi_warning:
                no_cpi_warning = True
                print '  Warning: year ' + year + ' does not have Consumer Price Index, please update provided cpi.tsv file!'
            salary = float(row[4])
            
        if id in salary_data:
            sdat = salary_data[id]
        else:
            sdat = []
            salary_data[id] = sdat
        sdat.append([year, str(salary)])
 
def add_yearly_data(pid, all_data, yearly_data, years_active, year_col):
    if pid in all_data:
        rows = all_data[pid]
        for row in rows:
            year = row[year_col]
            yearly_data[year] = [val if val != '' else '\\N' for val in row]
            years_active.add(year)
 
def add_row_data(year, yearly_data, columns, all_row, team_data, lg_col, tm_col, st_col, rn_col):
    if year in yearly_data: 
        row = yearly_data[year]
        if -1 < lg_col: team_data[0] = row[lg_col] # league        
        if -1 < tm_col: team_data[1] = row[tm_col] # team
        if -1 < st_col: team_data[2] = row[st_col] # stint
        if -1 < rn_col: team_data[3] = row[rn_col] # round
        for col in columns:
            all_row.append(row[col])
    else:
        all_row.extend(['\\N'] * len(columns))
 
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
        yearly_salary_data = {}
        yearly_batting_data = {}
        yearly_fielding_data = {}    
        yearly_pitching_data = {}
        yearly_batting_post_data = {}
        yearly_fielding_post_data = {}    
        yearly_pitching_post_data = {}

        if pid in salary_data:
            srows = salary_data[pid]
            for srow in srows:
                year = srow[0]
                yearly_salary_data[year] = srow[1]
    
        add_yearly_data(pid, batting_data, yearly_batting_data, years_active, 1)
        add_yearly_data(pid, pitching_data, yearly_pitching_data, years_active, 1)            
        add_yearly_data(pid, fielding_data, yearly_fielding_data, years_active, 1)

        add_yearly_data(pid, batting_post_data, yearly_batting_post_data, years_active, 0)
        add_yearly_data(pid, pitching_post_data, yearly_pitching_post_data, years_active, 1)            
        add_yearly_data(pid, fielding_post_data, yearly_fielding_post_data, years_active, 1)
        
        count = count + 1
        years_active = sorted(years_active, key=lambda item: (int(item), item))
        
        for year in years_active:
            all_row = []
        
            for col in master_columns:
                all_row.append(mrow[col])

            # league, team, stint, round
            team_data = ['\\N', '\\N', '\\N', '\\N']

            if year in yearly_salary_data:
                salary = yearly_salary_data[year]            
            else:
                salary = '\\N'
                
            add_row_data(year, yearly_batting_data, batting_columns, all_row, team_data, 4, 3, 2, -1)
            add_row_data(year, yearly_pitching_data, pitching_columns, all_row, team_data, 4, 3, 2, -1)
            add_row_data(year, yearly_fielding_data, fielding_columns, all_row, team_data, 4, 3, 2, -1)

            add_row_data(year, yearly_batting_post_data, batting_post_columns, all_row, team_data, -1, -1, -1, 1)
            add_row_data(year, yearly_pitching_post_data, pitching_post_columns, all_row, team_data, -1, -1, -1, 2)
            add_row_data(year, yearly_fielding_post_data, fielding_post_columns, all_row, team_data, -1, -1, -1, 4)

            all_row.insert(len(master_columns) + 0, pid)
            all_row.insert(len(master_columns) + 1, year)
            all_row.insert(len(master_columns) + 2, team_data[0])
            all_row.insert(len(master_columns) + 3, team_data[1])        
            all_row.insert(len(master_columns) + 4, team_data[2])
            all_row.insert(len(master_columns) + 5, team_data[3])            
            all_row.insert(len(master_columns) + 6, salary)            
            
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
    
    write_xml_line(' <group name="Player stats">', xml_file, xml_strings)
    write_xml_line('  <table name="Bio">', xml_file, xml_strings)
    for name in master_names[0: len(master_names) - num_team_vars]:    
        write_xml_line('   <variable name="' + name + '"/>', xml_file, xml_strings)
    write_xml_line('  </table>', xml_file, xml_strings)
    write_xml_line('  <table name="Teams">', xml_file, xml_strings)
    for name in master_names[len(master_names) - num_team_vars: len(master_names)]:
        write_xml_line('   <variable name="' + name + '"/>', xml_file, xml_strings)
    write_xml_line('  </table>', xml_file, xml_strings)
    write_xml_line(' </group>', xml_file, xml_strings)

    write_xml_line(' <group name="Season stats">', xml_file, xml_strings)
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
    
    write_xml_line(' <group name="Post-season stats">', xml_file, xml_strings)
    write_xml_line('  <table name="Batting Post">', xml_file, xml_strings)
    for name in batting_post_names:
        write_xml_line('   <variable name="' + name + '"/>', xml_file, xml_strings)
    write_xml_line('  </table>', xml_file, xml_strings)
    write_xml_line('  <table name="Pitching Post">', xml_file, xml_strings)
    for name in pitching_post_names:
        write_xml_line('   <variable name="' + name + '"/>', xml_file, xml_strings)
    write_xml_line('  </table>', xml_file, xml_strings)    
    write_xml_line('  <table name="Fielding Post">', xml_file, xml_strings)
    for name in fielding_post_names:
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
    all_types.extend(batting_post_types)
    all_types.extend(pitching_post_types)
    all_types.extend(fielding_post_types)

    all_titles = []
    all_titles.extend(master_titles)
    all_titles.extend(batting_titles)
    all_titles.extend(pitching_titles)
    all_titles.extend(fielding_titles)
    all_titles.extend(batting_post_titles)
    all_titles.extend(pitching_post_titles)
    all_titles.extend(fielding_post_titles)
    
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
                key = row[i].replace(";", ",")
                if 'throwing hand' in title or 'batting hand' in title:
                    values[key] = hand[key]
                else:
                    values[key] = key
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
        elif 'String' in all_types[i]:
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

batting_post_data = {}
batting_post_columns = []
batting_post_names = []
batting_post_titles = []
batting_post_types = []

pitching_post_data = {}
pitching_post_columns = []
pitching_post_names = []
pitching_post_titles = []
pitching_post_types = []

fielding_post_data = {}
fielding_post_columns = []
fielding_post_names = []
fielding_post_titles = []
fielding_post_types = []

team_names = {}
salary_data = {}

init_dataset(output_folder)

print 'Reading master table...'
read_master(source_folder + 'Master.csv', 'master-table.tsv', master_data, master_columns, master_names, master_titles, master_types) 
print 'Done.'
num_team_vars = 7
master_names.extend(['playerID', 'yearID', 'lgID', 'teamID', 'stint', 'round', 'salary']);
master_titles.extend(['Player ID', 'Year', 'League', 'Team', 'Player\'s stint', 'Level of playoffs', 'Salary']);
master_types.extend(['String', 'int', 'category', 'category', 'int', 'category', 'float']);

print 'Reading batting table...'
read_table(source_folder + 'Batting.csv', 'batting-table.tsv', batting_data, batting_columns, batting_names, batting_titles, batting_types, 0, 'BAT.')    
print 'Done.'

print 'Reading pitching table...'
read_table(source_folder + 'Pitching.csv', 'pitching-table.tsv', pitching_data, pitching_columns, pitching_names, pitching_titles, pitching_types, 0, 'PITCH.')
print 'Done.'

print 'Reading fielding table...'
read_table(source_folder + 'Fielding.csv', 'fielding-table.tsv', fielding_data, fielding_columns, fielding_names, fielding_titles, fielding_types, 0, 'FIELD.')
print 'Done.'

print 'Reading battingPost table...'
read_table(source_folder + 'BattingPost.csv', 'battingpost-table.tsv', batting_post_data, batting_post_columns, batting_post_names, batting_post_titles, batting_post_types, 2, 'BAT_POST.')    
print 'Done.'

print 'Reading pitchingPost table...'
read_table(source_folder + 'PitchingPost.csv', 'pitchingpost-table.tsv', pitching_post_data, pitching_post_columns, pitching_post_names, pitching_post_titles, pitching_post_types, 0, 'PITCH_POST.')
print 'Done.'

print 'Reading fieldingPost table...'
read_table(source_folder + 'FieldingPost.csv', 'fieldingpost-table.tsv', fielding_post_data, fielding_post_columns, fielding_post_names, fielding_post_titles, fielding_post_types, 0, 'FIELD_POST.')
print 'Done.'

print 'Reading team names...'
read_team_names(source_folder + 'Teams.csv')
print 'Done.'

print 'Reading salaries...'
read_salaries(source_folder + 'Salaries.csv', 'cpi.tsv')
print 'Done.'

all_data = []
all_names = []
all_names.extend(master_names)
all_names.extend(batting_names)
all_names.extend(pitching_names)
all_names.extend(fielding_names)
all_names.extend(batting_post_names)
all_names.extend(pitching_post_names)
all_names.extend(fielding_post_names)

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