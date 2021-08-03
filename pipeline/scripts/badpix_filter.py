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
    #read the iniconf info so that we know which folder we are looking at doing bad pixel filtering.
    obj_path = main_dir + '/' + iniconf['all info']['obj_id'] + "/"
    obj_name = iniconf['all info']['obj_id']
    #we are currently in the scripts directory
    scripts_dir = iniconf['all info']['pipeline_dir'] + "/pipeline/scripts/"
    #copy the .pro and .cl script to each folder
    os.system('cp ' + scripts_dir + 'filterfourstar.pro ' + obj_path)
    os.system('cp ' + scripts_dir +  'cleanit.cl ' + obj_path)

    #delete the previous instance of run.idl
    os.system('rm -rf ' + obj_path  + 'run.idl')
    #run the code
    os.system('echo “.comp %sfilterfourstar” > %srun.idl'%(obj_path,obj_path)) 
    os.system('echo “ffs” >> %srun.idl'%(obj_path))
    os.system('echo “exit” >> %srun.idl'%(obj_path))
    os.system('idl < %srun.idl'%(obj_path))


    #then delete all the useless files
    os.system('rm -rf %sout*.fits'%(obj_path))
    os.system('rm -rf %sfoo*.fits'%(obj_path))
    os.system('rm -rf %sdiff*.fits'%(obj_path))
    os.system('rm -rf %sbase*.fits'%(obj_path))
    os.system('rm -rf %s*.par'%(obj_path))

    #if you do not want to delete these files you can comment the above and uncomment this
    # os.system('mkdir bad_pix_outputs')
    # os.system('mv out*.fits bad_pix_outputs/')
    # os.system('mv foo*.fits bad_pix_outputs/')
    # os.system('mv diff*.fits bad_pix_outputs/')
    # os.system('mv base*.fits bad_pix_outputs/')
    # os.system('mv *.par bad_pix_outputs/')

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









    


