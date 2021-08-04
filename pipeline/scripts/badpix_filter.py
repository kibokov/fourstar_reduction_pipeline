#This is the script that does bad pixel filtering. We use Mike's IRAF + IDL script to do this.

import os
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



def run_badpix_filtering(iniconf):
    main_dir = iniconf['all info']['output_dir']
    temp_dir = iniconf['all info']['temp_dir'] + "/"
    obj_name = iniconf['all info']['obj_id'] 

    #read the iniconf info so that we know which folder we are looking at doing bad pixel filtering.
    obj_path = main_dir + '/' + obj_name + "/"
    #we are currently in the scripts directory
    scripts_dir = iniconf['all info']['pipeline_dir'] + "/pipeline/scripts/"
    #copy the .pro and .cl script to the temp iraf folder

    ##So IRAF is only working in home directory for some reason. 
    ##So the filtering code will be running in home folder
    ##We will be deleting the files regularly

    ##copy the final*.fits files into this temp folder

    os.system('cp ' + obj_path + 'final*.fits ' + temp_dir)
    os.system('cp ' + scripts_dir + 'filterfourstar.pro ' + temp_dir)
    os.system('cp ' + scripts_dir +  'cleanit.cl ' + temp_dir)
    os.system('cp ' + scripts_dir +  'run.idl ' + temp_dir)

    os.system('cd %s && idl < run.idl'%(temp_dir))

    #then delete all the useless files
    os.system('cd %s && rm -rf out*.fits'%(temp_dir))
    os.system('cd %s && rm -rf foo*.fits'%(temp_dir))
    os.system('cd %s && rm -rf diff*.fits'%(temp_dir))
    os.system('cd %s && rm -rf base*.fits'%(temp_dir))
    os.system('cd %s && rm -rf *.par'%(temp_dir))
    #delete all the final*.fits, that is, unfiltered fits file data.
    os.system('cd %s && rm -rf final*.fits'%(temp_dir))

    #move the filtered files to the correct storage position
    os.system('cd %s && mv filtered*.fits %s'%(temp_dir,obj_path) )


    print_stage("Bad pixel filtering finished for %s !"%obj_name)

    return 

    

# def make_own_cleanit(iniconf):
#     '''
#     This is the function that allows you to input your own parameters to do bad pixel filtering.
#     '''

#     f = open("cleanit_new.cl","a")
#     f.write("!rm out*fits\n")
#     f.write("stsdas\n")
#     f.write("!rm foo*\n")
#     f.write("rmedian base1 foo2 0.0 1.5\n")

#     f.write("imarith base1 - foo2 foo3\n")

#     f.write("imarith foo2 + 100 foo4\n")

#     f.write("imarith foo3 / foo4 foo5\n")

#     f.write("imcalc foo5,base1,foo2 out1.fits 'if im1 .gt. 1.00 .or. im1 .lt. -1.00 then im3 else im2'\n")

#     f.write("!rm foo*\n")
#     f.write("rmedian base2 foo2 0.0 1.5\n")
#     f.write("imarith base2 - foo2 foo3\n")
#     f.write("imarith foo2 + 100 foo4\n")
#     f.write("imarith foo3 / foo4 foo5\n")
#     f.write("imcalc foo5,base2,foo2 out2.fits 'if im1 .gt. 1.00 .or. im1 .lt. -1.00 then im3 else im2'\n")
#     f.write("!rm foo*\n")
#     f.write("rmedian base3 foo2 0.0 1.5\n")
#     f.write("imarith base3 - foo2 foo3\n")
#     f.write("imarith foo2 + 100 foo4\n")
#     f.write("imarith foo3 / foo4 foo5\n")
#     f.write("imcalc foo5,base3,foo2 out3.fits 'if im1 .gt. 1.00 .or. im1 .lt. -1.00 then im3 else im2'\n")
#     f.write("!rm foo*\n")
#     f.write("rmedian base4 foo2 0.0 1.5\n")
#     f.write("imarith base4 - foo2 foo3\n")
#     f.write("imarith foo2 + 100 foo4\n")
#     f.write("imarith foo3 / foo4 foo5\n")
#     f.write("imcalc foo5,base4,foo2 out4.fits 'if im1 .gt. 1.00 .or. im1 .lt. -1.00 then im3 else im2'\n")
#     f.write("!rm diff*fits\n")
#     f.write("imarith base1 - out1 diff1\n")
#     f.write("imarith base2 - out2 diff2\n")
#     f.write("imarith base3 - out3 diff3\n")
#     f.write("imarith base4 - out4 diff4\n")
#     f.write("log\n")









    


