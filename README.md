## tdms2bin ##
Convert each Device/Channel in a TDMS file to separate 4-byte float file

### Purpose/Assumtions/Info ###

`tdms2bin` originally written to convert BRAVO data. The TDMS channel data are stored as
2-byte intergers. Converting them to 4-bytes, doubles the storage. The current version of `tdms2info` does not check that disks space is available before boldly writing a new file.

Program assumes that an 'Unscaled Data' and 'Scaling Coefficients' group exist in the file, If not, then the user needs to input the right group names  via command line paramater (see below)

The program assumes the 'Scaling coeffcients' are linear and entered in the TDMS as [DC_offset, scale_factor]


## Installation ##

*** Option 1 ***  
Obtain the tdms2bin.tgz source package and   

`
tar xzvf tdms2bin.tgz;   
cd tdms2bin; 
pip3 install .
`  

*** Option 2 ***

Clone source package  
`git clone http://github.com/flyrok/tdms2bin`

Install with pip after download  
`pip install .`

Or, install in editable mode  
`pip install -e .`

Or install directly from github  
`pip install git+https://github.com/flyrok/tdms2bin#egg=plot_tdms`


## Python Dependencies ##
python>=3.6 (script uses f-strings)  

If using python 3.5, then the user needs to install future_fstrings. The setup.py will not.  
`pip3 install future_fstrings` 

npTDMS>=0.27.0  
numpy  

## Usage/Examples ##

To see help:  
`tdms2bin --help`    

To see version:  
`tdms2bin --version`    

** Example 1 **  

To convert file *200218_192507_LS_BALTORO_5_Nom.tdms* with debug messages on and saving to the default output files  

`tdms2bin -f 200218_192507_LS_BALTORO_5_Nom.tdms -vvv`  
  
This will spew a lot  of messages and produce files  

1. -rw-r--r-- 1 aferris aferris 36400052 Jun 18 12:12 200218_192507_LS_BALTORO_5_Nom.Dev1.ai3.bin  
2. -rw-r--r-- 1 aferris aferris 36400052 Jun 18 12:12 200218_192507_LS_BALTORO_5_Nom.Dev1.ai0.bin  

** Example 2 **  

To convert file *200218_192507_LS_BALTORO_5_Nom.tdms* and save to files with a filename_root of *junk*  

`tdms2bin -f 200218_192507_LS_BALTORO_5_Nom.tdms -o junk ` 

This will produce files with names  

1. -rw-r--r-- 1 aferris aferris 36400052 Jun 18 12:42 junk.Dev1.ai3.bin  
2. -rw-r--r-- 1 aferris aferris 36400052 Jun 18 12:42 junk.Dev1.ai0.bin  





