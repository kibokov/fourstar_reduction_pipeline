'''
This is the script that combines the flat fields using a python function equivalent to IRAF imcombine. 

This function is from https://github.com/ysBach/imcombinepy. Instructions for installation are at the link.

'''
import numpy as np
import glob
from astropy.io import fits
import imcombinepy as imc
import os
import matplotlib.pyplot as plt

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
    
    
def use_imcombine(file_names=None,output=None, kw=None):
    '''
    This function uses the imcombine feature "imc.fitscombine" to combine fits files
    
    Sometimes there is only one file "to combine", in that case, we cannot use this
    feature and have to use the file as it is.
    '''
    
    if len(file_names) == 1:
        #no "combination" needed. Just rename the file to the "output" file
        org_file = file_names[0]
        comb_data, hdr = fits.getdata(org_file,header = True)
        if output is not None:
            fits.writeto(output,comb_data,hdr,overwrite=True)
    else:
        comb_data = imc.fitscombine(fpaths = file_names, offsets=None,output=output, overwrite=True,**kw)
        
    return comb_data
    
def save_fits(array,file_name, header=False):

    if header==False:
        hdu = fits.PrimaryHDU(array)
        hdu.writeto(file_name, overwrite = True)

    else:
        #the only reason header is needed is the pixel units 
        hdu = fits.PrimaryHDU()
        hdr = hdu.header
        hdr['BUNIT'] = 'du'

        hdu = fits.PrimaryHDU(array, header = hdr)
        hdu.writeto(file_name, overwrite = True)

    return


# def gen_file_names(nmin, nmax, nzeros,data_path,kind = "fsr"):
def gen_file_names(iniconf=None,kind = None,verbose=True,chip_num=None):
    '''
    Function that will generate the list of file names to be read. 

    Parameters:
    ----------------
    iniconf: dictionary of .ini file 
    kind: string, "flats" or "science"
    '''

    #the path to all the image data
    final_data_path = iniconf['all info']['data_dir']
    # date = iniconf['all info']['date']
    # final_data_path = data_path + "/" + date


    file_kind = iniconf['all info']['kind']
    #chip_num = iniconf['all info']['which_chip']
    verbose = iniconf['all info']['verbose']

    if verbose == True:
        print_stage("The data lies at this path : " + final_data_path)
        
    if kind == "flats":
        num_range = iniconf['all info']['flats'].split(',')
    if kind == "science":
        num_range = iniconf['all info']['science'].split(',')

    ##if two numbers are provided, we compute the range between the two
    ## if more than two numbers are provided then no need
  
    if len(num_range) == 2:
        num_range_f = []
        nmin = int(num_range[0])
        nmax = int(num_range[1])
        all_ns = np.arange(nmin, nmax+1)
        num_zeros = len(num_range[0].replace(str(nmin),""))
        for k in all_ns:
            num_range_f.append( "0"*num_zeros + str(k) )
    else:
        num_range_f = num_range

        
    all_files = []
    for ni in num_range_f:
        all_files.append(glob.glob(final_data_path + "/" + file_kind + "*" + ni + "*_" + chip_num + "*"))
        
    
    all_file_names = np.concatenate(all_files)

    if verbose == True:
        print("All the %s files being read are :"%kind)
        print(all_file_names)

    return all_file_names, num_range_f


def imcombine_flats(iniconf,all_file_names,bad_pix_mask,median_norm=False,chip_num=None):
    '''
    Function that combines all the flats into a single master flat
        
    Parameters:
    -------------
    iniconf : dictionary, the .ini file 
    all_file_names: list, list of all the paths+name of the flat fields to be combined
    output_file : string, the name of the output file
    median_norm : bool, should the resulting combined flat be normalized such that median = 1
    
    Returns:
    ----------------
    total_fits : array, the combined fits file
    output_name : string, the path where the combined fits file is stored
    
    '''
    flat_file_name = iniconf['all info']['flat_name'] 

    # outputs_dir = iniconf['all info']['flats_dir']
    outputs_dir = os.getcwd().replace('/scripts','') + '/pipeline/relevant_fits/flat_fields'
    #chip_num = iniconf['all info']['which_chip']

    flat_range = iniconf['all info']['flats'].split(",")
    common_tag = "_" + flat_range[0] + "_" 

    output_name = outputs_dir + "/" + flat_file_name + common_tag + chip_num + ".fits"
    
    #first modifies the header info. Converts 'DU/PIXEL' --> 'du'
    #this package has some weird pixel units formatting requirements
    
    for i in range(len(all_file_names)):
        fits.setval(all_file_names[i], 'BUNIT', value='du')
        
    #the dictionary that carries all the info for passing to imcombine function
    #median combinaton, median scaling and rejection method is sigma clipping
    kw = dict(combine='mean', scale="median", reject='ccdclip', sigma=(1000, 2), memlimit=5.e+9)
    #the sigma of (1000,2) is used to mimic cosmic ray rejection. 
    #this trick is described in the documentation of the imcombinepy package.

    #the offsets are none because we do not have WCS info
    
#    comb_flat = imc.fitscombine(fpaths = all_file_names, offsets=None,output=output_name, overwrite=True,**kw)
    
    comb_flat = use_imcombine(file_names = all_file_names,output = output_name, kw = kw)
    
    total_fits = np.array(comb_flat)

    if median_norm == True:
        total_fits = total_fits/np.median(total_fits)

    total_fits[bad_pix_mask == 0] = np.nan
    #apply the bad pix mask to the flat to make all the bad pixels as nans

    output_name_1 = outputs_dir + "/" + flat_file_name + common_tag + chip_num + "_flat_norm_mask.fits"

    #we also save the normalized flat which has a mask applied to it
    #we do not overwrite the existing flat as it will have some useful information
    
    save_fits(total_fits,output_name_1, header=True)

    return total_fits


def imcombine_science(iniconf,all_sci_names, all_sci_nums, bad_pix_mask,chip_num=None,save_relevant = True):
    '''
    Function that adds the science images at the same dither position.
    Each science image number liek 238_*** is all the science images at a single dither position
    We may have taken many loops at a single position so we will have multiple images.

    '''

    #we need to loop over every dither frame number 

    sci_save = iniconf['all info']['sci_name']
    # coadded_org_sci = iniconf['all info']['coadded_org_sci']
    coadded_org_sci = os.getcwd().replace('/scripts','') + '/pipeline/relevant_fits/coadded_org_sci'

   
    all_coadd_sci_names = []
    all_coadd_sci_arrays = []

    #we loop over each science frame number (aka dither position) we have and combine all the corresponding ones
    for ni in all_sci_nums:

        sub_sci_names = [x for x in all_sci_names if ni in x]

        #make sure they have right unit so imcombine can add them
        for i in range(len(sub_sci_names)):
            fits.setval(sub_sci_names[i], 'BUNIT', value='du')

        #combine these fits files using mean and rejecting outliers
        kw = dict(combine='mean', zero="median", reject='ccdclip', sigma=(1000, 2), memlimit=5.e+9)

        output_name =  coadded_org_sci + "/" + sci_save + "_" + ni + '_' + str(chip_num) + "_sci_add.fits"
        
        
#        comb_flat = imc.fitscombine(fpaths = sub_sci_names, offsets=None,output=None, overwrite=True,**kw)
        
        comb_flat = use_imcombine(file_names = sub_sci_names,output = None,kw = kw)
        
        #now this fits combined science image is saved at the path "output_name"
        #however, it is also returned as comb_flat above.

        comb_flat = np.array(comb_flat)

        #we will apply the bad pix mask to this image 
        comb_flat[bad_pix_mask == 0] = np.nan

        #let us overwrite the previous fits file with the one with a bad pix mask applied
        if save_relevant == True:
            save_fits(comb_flat,output_name, header=True)
    

        #we append all these science images into a list that is finally returned
        all_coadd_sci_arrays.append(comb_flat) 

        #we also save the paths to these saved science combined images as they might be useful
        #note that these saved sciences do not have the bad pixel mask applied to them.
        all_coadd_sci_names.append(output_name)

    return all_coadd_sci_arrays


def get_bad_pixel_mask(iniconf, all_file_names, chip_num = None,save_relevant = True):
    '''
    Function that computes the bad pixel mask from the flat fields.
    '''

    all_flats = []
    for i in all_file_names:
        data_i = fits.open(i)[0].data
        all_flats.append(data_i)

    all_flats = np.array(all_flats)

    #compute the standard deviation at each pixel position in all the flat frames
    std_array = np.std(all_flats, axis = 0)

    std_std = np.std(std_array)

    mask = np.ones(shape = np.shape(all_flats[0]))
    #this will be (2048, 2048)

    #if the standard deviation in any of the pixels is lower than 5 sigma than the median value..we consider those as bad pixels
    mask[ std_array < np.median(np.concatenate(std_array)) - 5*std_std ] = 0

    #so the mask is 1 for good pixels and is 0 for bad pixels
    bad_pix_dir = os.getcwd().replace('/scripts','') + '/pipeline/relevant_fits/bad_pix_masks'

    mask_name = bad_pix_dir + "/" +  "bad_pix_mask_" + str(chip_num) + ".fits"
    if save_relevant == True:
        save_fits(mask,mask_name)

    #once the bad pix mask is saved, we also return it below

    return mask






















