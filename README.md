## rsach ##

Quick/dirty cmdline script to read and report specific SAC header values.

Requires ObsPy.

Return header as key:value pair.

Currently works on only 1 file at a time


### Installation ### 

Clone source package  
`git clone http://github.com/flyrok/rsach`

Install with pip after download  
`pip install .`

Or, install in editable mode  
`pip install -e .`

Or install directly from github  
`pip install git+https://github.com/flyrok/rsach#egg=rsach`


## Python Dependencies ##
* python>=3.6 

*  ObsPy


## Usage/Examples ##

To see help:  
`rsach --help`    

To see version:  
`rsach --version`    

To report origin time fields:  
`rsach -f DAG-1.IM.NV10..SHZ.sac -k nzyear nzjday nzhour nzmin nzsec nzmsec`  
nzyear:2018 nzjday:201 nzhour:16 nzmin:51 nzsec:52 nzmsec:680

To report origin time in isoformat:  
`rsach -f DAG-1.IM.NV10..SHZ.sac -k  otime`  
2018-07-20T16:51:52.680000

To report P arrival time:  
`rsach -f DAG-2.IM.NV10..SHZ.sac -k a`  
a:38.236




