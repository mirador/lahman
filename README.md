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
dataset.


**3)** Run the makedataset.py script, indicating the release year:

```bash
python makedataset.py 2013
```

The resulting Mirador dataset will be saved in the mirador folder.