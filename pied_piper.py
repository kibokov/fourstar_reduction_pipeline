import argparse
import numpy as np
import os
from configparser import ConfigParser, ExtendedInterpolation
import sys

def print_stage(line2print, ch='-'):
    '''
    Function that prints lines for organizational purposes in the code outputs.

    Parameters:
    -----------
    line2print: str, the message to be printed
    ch : str, the boundary dividing character of the message
    '''
    nl = len(line2print)
    print(ch*nl)
    print(line2print)
    print(ch*nl)
    print(' ')


def argument_parser():
    '''
    Function that parses the arguments passed while running a script

	fits : str, the multi extension fits file outputted by galfit
	for_cutout: str, True of False
    '''
    result = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # path to the config file with parameters and information about the run
    result.add_argument('-t', dest='t', type=str,default="sci_info.txt") 
    return result


def read_config_file(config_file=None):
    '''
    Function that reads the ini file

    Parameters:
    -------------
    config_file: str, path to the config file

    Returns:
    ------------
    iniconf: dict, dictionary of parameters in the config file

    '''

    if config_file is None:
        raise ValueError('input configuration file is not provided. Use -ini config_file_path to specify the config file')

    if not os.path.isfile(config_file):
        raise ValueError('input configuration file %s does not exist!'%config_file)

    iniconf = ConfigParser(interpolation=ExtendedInterpolation())
    iniconf.read(config_file)  
    return iniconf 


if __name__ == '__main__': 

    # read in command line arguments
    args = argument_parser().parse_args()

    PATH_ini = os.getcwd() + '/pipeline/fourstar_pipeline.ini'
    
    # read parameters and information from the sci_info file 
    txt_info = np.loadtxt(args.t,dtype=str)
    pipeline_dir = txt_info[0]
    data_dir = txt_info[1]
    output_dir = txt_info[2]
    mode_pro = txt_info[3]
    use_astrometry = txt_info[4]
    which_band = txt_info[5].strip()
    flat_range = txt_info[6]

    for i in range(len(txt_info[7:])):

        sci_info = txt_info[7+i].split(',')
        sci_range = sci_info[0].replace(" ","")+','+sci_info[1].replace(" ","")
        sci_ra = sci_info[2].replace(" ","")
        sci_dec = sci_info[3].replace(" ","")
        obj_id = sci_info[4].replace(" ","")
        
        iniconf = read_config_file(PATH_ini)
        iniconf.set('all info','science',str(sci_range))
        iniconf.set('all info','ra',str(sci_ra)) 
        iniconf.set('all info','dec',str(sci_dec)) 
        iniconf.set('all info', 'flats', str(flat_range))
        iniconf.set('all info','data_dir', str(data_dir) )
        iniconf.set('all info','which_band',str(which_band))
        iniconf.set('all info','use_astrometry',str(use_astrometry)) 
        iniconf.set('all info','obj_id',str(obj_id))
        iniconf.set('all info','parallel_or_serial',str(mode_pro)) 
        iniconf.set('all info','output_dir',str(output_dir)) 
        iniconf.set('all info','pipeline_dir',str(pipeline_dir)) 


        with open(PATH_ini,'w') as f:
            iniconf.write(f)

        print_stage("File Range %s is being processed."%sci_range)

        os.system('python3 pipeline/run_pipeline.py')


