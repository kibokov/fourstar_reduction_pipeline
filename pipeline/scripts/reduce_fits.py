'''
Script that contains functions that reduce the science data
'''

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning) 
import numpy as np
import glob
from astropy.io import fits
import imcombinepy as imc
import os


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

def flat_reduce(iniconf, norm_flat, all_sci_arrays, all_sci_nums, bad_pix_mask, chip_num = None):
    '''
    Function that flat reduces the coadded science images at each dither position

    '''
    # flat_reduced_sci = iniconf['all info']["flat_reduced_sci"]
    # flat_reduced_sci = os.getcwd().replace('/scripts','') + '/pipeline/relevant_fits/flat_reduced_sci'
    flat_reduced_sci = iniconf['all info']['output_dir'] + '/' + iniconf['all info']['obj_id'] + '/relevant_fits/flat_reduced_sci' 

    sci_name = iniconf['all info']["sci_name"]

    flat_reduce_sci_names = []

    flat_reduced_sci_arrays = []

    #loop through each science image
    for k, ai in enumerate(all_sci_arrays):
        #divide by the flat field now

        image_flat_reduce = ai/norm_flat

        #apply the mask again to be extra sure
        image_flat_reduce[bad_pix_mask == 0] = np.nan

        #save this image
        temp_name = flat_reduced_sci + "/" + sci_name + "_" + all_sci_nums[k] + '_' + str(chip_num) + "_flat_reduce_sci.fits"
        save_fits(image_flat_reduce, temp_name, header = True)

        flat_reduce_sci_names.append(temp_name)

        flat_reduced_sci_arrays.append(image_flat_reduce)

    return flat_reduced_sci_arrays, flat_reduce_sci_names



def estimate_sky(iniconf, flat_reduce_sci_names, bad_pix_mask, chip_num = None, save_relevant = True):
    '''
    Function that estimates the sky by adding with rejection the science images at different dither positions

    the science images will need to have some header info to be able to combine

    '''

    #we just coadded all the flat fielded science images at different dither positions with rejection to estimate the sky 

    # sky_path = iniconf['all info']["sky_dir"]
    sky_path = os.getcwd().replace('/scripts','') + '/pipeline/relevant_fits/skies'
    sky_name = iniconf['all info']["sky_name"]
    
    sky_name = sky_path + "/" + sky_name +'_' + str(chip_num) + ".fits"

    kw = dict(combine='median', scale="median", reject='sc', sigma=(2,2), memlimit=5.e+9)
    if save_relevant == True:

        sky_est = imc.fitscombine(fpaths = flat_reduce_sci_names, offsets=None,output=sky_name, overwrite=True,**kw)
    elif save_relevant == False:
        sky_est = imc.fitscombine(fpaths = flat_reduce_sci_names, offsets=None,output=None, overwrite=True,**kw)

    #as flat reduce_sci_names are not needed anymore, we delete it
    for fii in flat_reduce_sci_names:
        os.remove(fii)

    #due to the dithering, the sky estimate should not have any nan values in it. 
    #But also the imcombine removes all the nans. So this sky_est has no nans in it.

    return sky_est


def subtract_sky(iniconf,sci_images, sky_est, num_range_sci, bad_pix_mask, chip_num = None, save_relevant = True):
    '''
    Function that subtracts the estimated sky from the science images
    '''

    sci_name = iniconf['all info']['sci_name']
    # sky_reduce_path = iniconf['all info']['sky_subtract_sci']
    sky_reduce_path = os.getcwd().replace('/scripts','') + '/pipeline/relevant_fits/sky_subtract_sci'

    sky_subtracts = []

    for k, sci in enumerate(sci_images):
        temp = sci - sky_est
        #we will apply the mask again to be extra extra sure
        temp[bad_pix_mask == 0] = np.nan

        sky_subtracts.append(temp)
        temp_name = sky_reduce_path + "/" + sci_name + "_" + num_range_sci[k] +'_' + str(chip_num)+ "_skyflat_reduce_sci.fits"
        #save this fits
        # if save_relevant == True:
            # save_fits(temp, temp_name)


    return sky_subtracts
