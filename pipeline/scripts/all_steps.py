


from fits_combine import gen_file_names, imcombine_flats, imcombine_science, get_bad_pixel_mask
from reduce_fits import flat_reduce, estimate_sky, subtract_sky
import numpy as np
import glob
from compute_mosaic import compute_mosaic
from astropy.io import fits
import os


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



def fourstar_pipeline(iniconf):
    '''
    Function that runs the entire pipeline

    Parameters:
    ---------------
    iniconf: dictionary, .ini file arguments
    
    Returns:
    --------------
    None

    Notes:
    --------------
    The steps in the pipeline:

    1. First combine all the relevant flats and normalize them such that median value = 1. 
    2. Each frame number is a different dither position. We will first add the science images at a single dither position. 
        Note that we are doing this all for just chip. Also, each dither position (aka frame number) has some number of loops. All the images over that loop will be added.
    3. We flat reduce these combined science images at each dither position by dividing them by the normalized flat field computed in step 1.
    3. Combine these coadded science images (with no shifting and with rejection) at different dither positions to make an estimate for the sky. 
        The resulting image should be an estimate of the average sky (that is why we do dithering in the first place!)
    4. Once this sky is obtained, subtract this from the science frames (which have already been flat fielded)
    5. Once this all is done, we want to combine the science frames at different dither positions to get the final fits file. 
        We employ a method that computes the pixel offset between some reference frame and all other frames in a fast manner.
        Using imcombinepy, we provide it these offsets and it combines all the science images into a mosaic.
    6. We have our final reduced FOURSTAR data!

    '''
    #first generate all the names of the fits files 
    all_chip_num = iniconf['all info']['which_chip'].split(',')
    save_relevant_str = iniconf['all info']['save_relevant']
    if save_relevant_str == 'True':
        save_relevant = True
    elif save_relevant_str == 'False':
        save_relevant = False
        
    for chip_num in all_chip_num:
        chip_num = chip_num.strip(' ')
        all_flat_names, _ = gen_file_names(iniconf=iniconf,kind = "flats", chip_num = chip_num)

        #get the bad pixel mask
        bad_pix_mask = get_bad_pixel_mask(iniconf, all_flat_names, chip_num =chip_num, save_relevant = save_relevant)

        #compute the normalized flat
        norm_flat = imcombine_flats(iniconf,all_flat_names,bad_pix_mask,median_norm=True, chip_num = chip_num)

        #first create all the science file names so that they can be read easily
        all_sci_names, num_range_sci = gen_file_names(iniconf=iniconf,kind = "science",verbose=False,chip_num = chip_num)
        #list of coadded science images at each dither position is returned below
        all_sci_org_coadd_arrays = imcombine_science(iniconf,all_sci_names, num_range_sci,bad_pix_mask, chip_num = chip_num, save_relevant = save_relevant)

        #flat reduce all the coadded science images at each dither pos
        flat_reduced_sci_arrays,flat_reduced_sci_names = flat_reduce(iniconf, norm_flat, all_sci_org_coadd_arrays, num_range_sci, bad_pix_mask, chip_num = chip_num)

        #combine the flat fielded science images at different dither positions to estimate the sky 
        sky_est = estimate_sky(iniconf, flat_reduced_sci_names, bad_pix_mask, chip_num = chip_num, save_relevant = save_relevant)

        #sky subtract the science images
        sky_sub_scis = subtract_sky(iniconf,flat_reduced_sci_arrays, sky_est, num_range_sci, bad_pix_mask, chip_num = chip_num, save_relevant = save_relevant)

        #coadd all the science images at different dither positions into a master mosaic
        compute_mosaic(iniconf,sky_sub_scis, num_range_sci, chip_num = chip_num)
        
        print('chip ' + str(chip_num) + ' has been processed!!!')

    #if save_relevant is False, then delete all the files there.
    

    return 






    





