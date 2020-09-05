#!/usr/bin/env python3

'''


'''

# standard system stuff -------------------------
from pathlib import Path
import sys
import argparse
from obspy import Stream,read, UTCDateTime
import logging

# END Module import -----------------------------


# set version stuff
there = Path(__file__).resolve().parent
exec(open(there / "version.py").read())

class rsach(object):
    def __init__(self,debug=None):
        '''
        '''

        # class debug level
        self.log=self._setup_log(debug)

    def read_sac(self,sac_files):
        st=Stream()
        for sac in sac_files:
            try: 
                st+=read(sac)
            except Exception as e:
                self.log.error(f'Problem reading {sac}. Error is: \n\t{e}')
                pass
        return st
    
    def report(self,st,keys):
        # grab the sac attribute dict
        for tr in st:
            try:
                sacd=tr.stats.sac
            except Exception as e:
                self.log.error('Problem with trace stats.sac. Error is: \n\t{e}')
                sys.exit(0)
            # if otime requested, grab pertinent header fields and run through 
            # UTCDateTime
            msg='' 
            if 'otime' in keys:
                keys.remove('otime')
                try:
                    YYYY=sacd['nzyear'.lower()]
                    DDD=sacd['nzjday'.lower()]
                    H=sacd['nzhour'.lower()]
                    M=sacd['nzmin'.lower()]
                    S=sacd['nzsec'.lower()]
                    MS=sacd['nzmsec'.lower()]
                    t=UTCDateTime(f'{YYYY:04d}{DDD:03d}T{H:02d}{M:02d}{S:02d}.{MS}').isoformat()
                    msg+=f'{t} '


                except Exception as e:
                    self.log.error(f'Problem with otime keys, error:\n\t{e}')
                    pass
            # Loop through requested sac headers and report values
            for i in keys:
                try:
                    msg+=f'{i}:{sacd[i.lower()]} '
                except Exception as e:
                    self.log.error(f'Problem with keys, error is: \n\t{e}')
                    pass
            print(msg)



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

        logging.basicConfig(level=loglevel,
            datefmt="%Y-%j %H:%M:%S", format="%(asctime)s-%(levelname)s %(message)s")

        log=logging.getLogger(__class__.__name__)
        ch = logging.StreamHandler()

        ch.setFormatter(logging.Formatter(datefmt="%Y%m%dT%H:%M:%S",fmt="%(asctime)s[%(levelname)s] %(message)s"))
        log.addHandler(ch)
        log.setLevel(loglevel)
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
    
    '''

    parser = argparse.ArgumentParser(prog=progname,
            formatter_class=CustomFormatter,
            description= '''
            ''',
            epilog='''
            Example usage:
            ''')

    parser.add_argument("-f","--sacfile",nargs='*',type=str, 
        required=True, help="Input sac file.")


    parser.add_argument("-k","--keys", type=str, nargs="*", 
        required=True, help="Sac header keys. add otime to get origin time in isoformat")

    parser.add_argument("-v", "--verbose", action="count",default=0,
        help="Turn on debug spewage (e.g. -v, -vv, -vvv)")

    parser.add_argument('--version', action='version',
        version='%(prog)s {version}'.format(version=__version__))

    args = parser.parse_args()
    sac=args.sacfile
    keys=args.keys
    debug=args.verbose

    obj=rsach(debug=debug)
    st=obj.read_sac(sac)
    obj.report(st,keys)

if __name__ == '__main__':
    main()
    
