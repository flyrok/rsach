#!/usr/bin/env python3

'''
TDMS file format converter
after installation, get usage by typing
tdsm2bin -h 

Aaron Ferris
'''

# tdms class ------------------------------------
from nptdms import TdmsFile

# Time and memory tracking ----------------------
import tracemalloc 
from time import perf_counter

# standard system stuff -------------------------
from pathlib import Path
import sys
from datetime import datetime,timedelta
import logging
import argparse

# Number stuff ----------------------------------
import numpy as np

# END Module import -----------------------------

# conversion from bytes to GiB
toGB=1024*1024*1024

# set version stuff
there = Path(__file__).resolve().parent
exec(open(there / "version.py").read())

class tdms2bin(object):
    def __init__(self,tdms_file=None,outbin=None,data_group='Unscaled Data',scale_group='Scaling Coefficients',debug=0):
        '''
        basic usage:
            tdms2bin_obj=tdms2bin(tdms_file='junk.tdms')
            tdms2bin_obj.write_bin()

        Parameters:
            tdms_file (str): name of the input tdms file
            outbin (str): rootname of the output .bin files,
                defaults to original file name (minus suffix) plus 'device_name.channel_name.bin'
            data_group (str): tdms group name of raw data
            scale_group (str): tdms group name of scaling coefficient groups
            debug (int): debub level, 0=warn, 1=info, 2=debug
        '''

        # class debug level
        self.debug=debug 

        # setup logging to stdout
        self.log=self._setup_log(self.debug)

        # make some things visible to the class
        self.tdms_file=tdms_file
        # set output root filename
        if outbin:
            self.outroot=outbin
        else:
            self.outroot=self.tdms_file.rsplit(".",1)[0]

        # data group
        self.data_grp=data_group
        # scaling coefficients group
        self.scale_grp=scale_group

        self.log.debug(f'Settings ...\n\
            tdms_file->{self.tdms_file}\n\
            outbin_root->{self.outroot}\n\
            data_group->{self.data_grp}\n\
            scale_group->{self.scale_grp}')

    def initialize(self):
        '''
        intializes the conversion of the tdms_file.
        This should always be done first, because ...

        1) starts timer and memory watcher--for funz
        2) reads the tdms file
        3) checks that the expected groups exists in the file
        4) Check/computes tdms time metadata, if needed
        5) Set, if applicable, tdms time meta data to tdsm.properties

        The tdms file object can be accessed via tdms2bin_obj.tdms

        '''
        _name=f'{__class__.__name__}.initialize:'

        self.tic=perf_counter() # start time tracking
        tracemalloc.start()     # Start memory tracking

        # Read tdms file
        self.tdms=self.read_tdms(self.tdms_file)

        # Check that the groups we expect, exist
        self.check_groups()

        # make a dict of important tdsm file properties
        time_props=self.get_time_properties()

        # set tdms channel properties for analysis/plotting, if not already set
        self.set_chan_properties(time_props)

        current, peak = tracemalloc.get_traced_memory()
        self.log.debug(f'{_name}: Memory after tdms read Cur,Peak: {current/toGB:0.4f},{peak/toGB} GiB\n')

    def write_bin(self):
        """
        Function to write the tdms data to a file
        1) it calls initialzes
        """
        _name=f'{__class__.__name__}.write_bin:'

        # Intialize tdms object 
        self.initialize() 
        for chan in self.tdms[self.data_grp].channels():
            chan_name=chan.name
            scale_coeffs=self.scaling_coeffs(self.tdms,chan_name)
            data=scale_coeffs[0] + chan[:] * scale_coeffs[1]
            header=self.make_header(chan,len(data))
            outarray=np.hstack((header,data))
            outfile=f'{self.outroot}.{chan_name.replace("/",".")}.bin'
            self.log.debug(f'{_name} Writing {chan_name} to {outfile}')
            outarray.astype('float32').tofile(outfile)

            if self.debug > 0:
                toc= perf_counter() - self.tic
                current, peak = tracemalloc.get_traced_memory()
                self.log.info(f'{_name} Cumulative runtime after read/scale/write:{toc:0.4f} secs\n\
                    Memory for  {chan_name} ... Current-> {current/toGB:0.4f} GiB Peak->{peak/toGB:0.4f} GiB\n\
                    header length={len(header)}\n\
                    data length={len(data)}\n\
                    output array={len(outarray)}\n\
                    file_size={4*len(outarray)} bytes')

    def make_header(self,chan_obj,nsamp):
        '''
        Make the header, i.e. make an array with the
        expected values and as 4-byte floats
        input:
            chan_obj: channel object from tdms object
            nsamp: number of samples in the data stream
                we need this to compute end time

        '''
        # sample rate from channel properties
        samp_rate=chan_obj.properties['samp_rate']
        # start time from channel properties, as datetime obj
        startt=chan_obj.properties['wf_start_time'].tolist()
        # endtime 
        endt=startt+timedelta(seconds=(nsamp-1)/samp_rate)

        # fill out header in right order, as 4-byte floats
        header=np.asarray([samp_rate,startt.year,startt.month,startt.day,
            startt.hour,startt.minute,
            startt.second+startt.microsecond/100000,
            endt.year,endt.month,endt.day,
            endt.hour,endt.minute,
            endt.second+endt.microsecond/100000],
            dtype='float32')

        return header

    def get_time_properties(self):
        _name=f'{__class__.__name__}.get_time_properties'
        '''
        Get or compute properties from the tdsm file and put in dictionary
        These will be added to each channel.property if they don't
        already exists. These values are needed for output/plotting

        inputs
            tdsm.object as self.tdms
        output: dict
               wf_start_time,samp_rate,wf_start_offset,wf_increment
        '''

        # Properties of interest
        keys=['Configuration', 'ChannelAssign', 'Author', 'TimeStamp', 'Sample Clock Rate']
        time_props={}
        config=self.tdms.properties[keys[0]]
        chanass=self.tdms.properties[keys[1]]
        if not self.tdms.properties[keys[3]]:  # check that TimeStamp is set
            self.log.warn(f'{_name}:\n !*!*!*!{keys[3]} not set in input file !*!*!*!*!')
            self.tdms.properties[keys[3]]='1970-01-01T00:00:00:000000'
        time_props['wf_start_time']=self.tdms.properties[keys[3]]
        time_props['samp_rate']=self.tdms.properties[keys[4]] 
        time_props['wf_start_offset']=0
        time_props['wf_increment']=1/time_props['samp_rate']
       
        # output messages
#        if config:
#            self.log.info(f'{_name}: Configuration:\n\t{config}')
#        else:
#            self.log.warn(f'{_name}: Empty configuration')

        self.log.debug(f'{_name} ChannelAssign\n\t{chanass}')
        self.log.debug(f"{_name} wf_start_time:{time_props['wf_start_time']}")
        self.log.debug(f"{_name} samp_rate:{time_props['samp_rate']}")
        self.log.debug(f"{_name} wf_start_offset:{time_props['wf_start_offset']}")
        self.log.debug(f"{_name} wf_increment:{time_props['wf_increment']}\n")
        return time_props

    def set_chan_properties(self,time_props):
        _name=f'{__class__.__name__}.set_chan_properties:'
        '''
        Set channel properties, in case they don't exist
        works inplace on the tdsm file
        '''
        # tdms properties to check/set
        keys=['wf_start_time','samp_rate','wf_start_offset','wf_increment']

        if not time_props:
            self.log.warn(f'{_name}\n* time_props empty, this is problem')

        groups=self.tdms.groups()
        self.log.debug(f'Found {len(groups)} groups in tdms file')

        for i in groups:
            if self.scale_grp in i.name:
                self.log.debug(f'Not setting chan_properties to group:{i.name}')
                continue

            channels=i.channels()
            self.log.debug(f'Found {len(channels)} channels in group:{i.name}')

            for c in channels:
                for k in time_props.keys():
                    if not k in c.properties.keys():
                        self.log.debug(f'key:{k} NOT in {c.name}, so setting it')
                        c.properties[k]=time_props[k]
                    else:
                        self.log.debug('key:{k} exists in {c.name}')
        return

    def check_groups(self):
        _name=f'{__class__.__name__}.check_groups:'
        '''
        Check the tdms groups to make sure they are what we expect.
        If the are not, then will likely set them wrong on input
        '''
        group_names=[i.name for i in self.tdms.groups()]

        if len(group_names) != 2:
            self.log.warning(f'{_name} Expected 2 groups, got {len(group_names)}')

        exit=0
        if not self.data_grp in group_names:
            self.log.error(f'{_name} [{self.data_grp}] not in {self.tdms_file}')
            exit=1

        if not self.scale_grp in group_names:
            self.log.error(f'{_name} [{self.data_grp}] not in {self.tdms_file}')
            exit=1

        if exit:
            self.log.error(f"{_name} We can't proceed ... exiting")
            sys.exit(0)

        self.log.debug(f"{_name} We found the following groups in {self.tdms_file}:\n{group_names}")

        return 

    def read_tdms(self,tdms_file):
        '''
        Read the tdms file.
        input (str): tdms_file name
        output (obj): tdms_object 
        '''
        _name=f"{__class__.__name__}.read_tdms:"
        try:
            tdms=TdmsFile.read(tdms_file)
        except Exception as e:
            self.log.error(f'{_name} Problem reading {tdms_file} ... \n\t{e}')
            sys.exit(0)
        self.log.debug(f'{_name} Read {tdms_file}')
        return tdms


    def scaling_coeffs(self,tdms,chan_name):
        '''
        Pull the scaling coeffs for a particular device/channel.
        We assume there are 2 coefficients  per channel
        '''
        _name=f"{__class__.__name__}.scaling_factor:"
        
        scale_coeffs=[0.0,1.0] #defaults, just in case
        try:
            scale_coeffs=tdms[self.scale_grp][chan_name][:]
        except Exception as e:
            self.log.error(f'{_name} Error with {self.scale_grp}:\n\t{e}')
            pass
        return scale_coeffs

    def _setup_log(self,debug):
        ''' Helper function to set up logging
            at the right debug level
            input (int): debug level (0,1,2). 
                0=warn
                1=info
                2=debug
        '''
        # INFO,DEBUG,WARN
        if debug == 0:
            loglevel="WARN"
        elif debug == 1:
            loglevel="INFO"
        else:
            loglevel="DEBUG"

        logging.basicConfig(filename='/dev/null', level=loglevel,
            datefmt="%Y-%j %H:%M:%S", format="%(asctime)s-%(levelname)s %(message)s")

        log=logging.getLogger(__class__.__name__)
        ch = logging.StreamHandler()

        ch.setFormatter(logging.Formatter(datefmt="%Y%m%dT%H:%M:%S",fmt="%(asctime)s[%(levelname)s] %(message)s"))
        log.addHandler(ch)
        log.setLevel(loglevel)
        print(f' {__class__.__name__} loglevel set to {loglevel}:{log.level}')
        return log


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    '''
    re-class ArgDefaults formatter to also print things pretty. Helps printing out the config file example
    '''
    def _get_help_string(self, action):
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    if type(action.default) == type(sys.stdin):
                        print( action.default.name)
                        help += ' (default: ' + str(action.default.name) + ')'
                    else:
                        help += ' (default: %(default)s)'
        return help


def main():
    '''
    Convience wrapper to run tdms2bin as a
    commandline program

    usage: tdmsinfo -h
    '''

    parser = argparse.ArgumentParser(prog=progname,
            formatter_class=CustomFormatter,
            description= '''
            Convert a tdms file to a 4-byte float file with
            specific header values
            ''',
            epilog='''
            Example usage:
            ''')

    parser.add_argument("-f","--tdms",type=str, 
        required=True, help="Input tdms file.")

    parser.add_argument("-o","--outbin", type=str, default=None,
        required=False, help="Root name for output .bin files. \
            Defaults to appending .device.chan.bin to input filename")

    parser.add_argument("-d","--datagrp", type=str, default='Unscaled Data',
        required=False, help="Name of the group with the raw data. Set if non-standard")

    parser.add_argument("-s","--scalegrp", type=str, default='Scaling Coefficients',
        required=False, help="Name of the scaling coefficients group  Set if non-standard")

    parser.add_argument("-v", "--verbose", action="count",default=0,
        help="Turn on debug spewage (e.g. -v, -vv, -vvv)")

    parser.add_argument('--version', action='version',
        version='%(prog)s {version}'.format(version=__version__))

    args = parser.parse_args()
    tdms_file=args.tdms
    outbin=args.outbin
    datagrp=args.datagrp
    scalegrp=args.scalegrp
    debug=args.verbose

    tdmsconv=tdms2bin(tdms_file=tdms_file,outbin=outbin,
        data_group=datagrp, scale_group=scalegrp, debug=debug)
    tdmsconv.write_bin()

if __name__ == '__main__':
    main()
    
