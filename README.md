## Lahman’s Baseball Database

These scripts download the data from the [Lahman’s Baseball Database](http://seanlahman.com/baseball-archive/statistics/) 
and format it as a mirador project.

### DEPENDENCIES

The scripts have the following dependencies:

1. Python 2.7.3+ (not tested with 3+) and the following package:
  * Requests: http://docs.python-requests.org/en/latest/index.html 

### Usage

**1)** Download and extract the zip files, indicating the release year and url (since it is 
not the same across years):

```bash
python download.py 2013 http://seanlahman.com/files/database/lahman-csv_2014-02-14.zip
```

**2)** Update the table files to indicate the variables to be included in the aggregated
dataset. These files can be constructed from the corresponding sections in the readme file
included alongside the data files in the original package, for example

```
2.1 MASTER table


playerID       A unique code asssigned to each player.  The playerID links
                 the data in this file with records in the other files.
birthYear      Year player was born
birthMonth     Month player was born
birthDay       Day player was born
birthCountry   Country where player was born
birthState     State where player was born
birthCity      City where player was born
deathYear      Year player died
deathMonth     Month player died
deathDay       Day player died
deathCountry   Country where player died
deathState     State where player died
deathCity      City where player died
nameFirst      Player's first name
nameLast       Player's last name
nameGiven      Player's given name (typically first and middle)
weight         Player's weight in pounds
height         Player's height in inches
bats           Player's batting hand (left, right, or both)         
throws         Player's throwing hand (left or right)
debut          Date that player made first major league appearance
finalGame      Date that player made first major league appearance (blank if still active)
retroID        ID used by retrosheet
bbrefID        ID used by Baseball Reference website
```

First, the space between the variable name and description should be replaced by a tab, 
and the descriptions made into a single line if needed. Then, the variables that should be
included into the mirador dataset are selected by adding a data type as a third column, 
resulting in something like follows:

```
playerID	A unique code asssigned to each player. The playerID links the data in this file with records in the other files.
birthYear	Year player was born	int
birthMonth	Month player was born	int
birthDay	Day player was born	int
birthCountry	Country where player was born	category
birthState	State where player was born	category
birthCity	City where player was born	category
deathYear	Year player died
deathMonth	Month player died
deathDay	Day player died
deathCountry	Country where player died
deathState	State where player died
deathCity	City where player died
nameFirst	Player's first name
nameLast	Player's last name
nameGiven	Player's given name (typically first and middle)
weight	Player's weight in pounds	int
height	Player's height in inches	int
bats	Player's batting hand (left, right, or both)	category
throws	Player's throwing hand (left or right)	category
debut	Date that player made first major league appearance
finalGame	Date that player made first major league appearance (blank if still active)
retroID	ID used by retrosheet
bbrefID	ID used by Baseball Reference website
```

**3)** Run the makedataset.py script, indicating the release year:

```bash
python makedataset.py 2013
```

The resulting Mirador dataset will be saved in the mirador folder.