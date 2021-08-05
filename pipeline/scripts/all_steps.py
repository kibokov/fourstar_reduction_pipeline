


from fits_combine import gen_file_names, imcombine_flats, imcombine_science,get_bad_pixel_mask
from reduce_fits import flat_reduce, estimate_sky, subtract_sky
import numpy as np
import glob
from badpix_filter import run_badpix_filtering
from compute_mosaic import compute_mosaic
from astropy.io import fits
import os
from astroquery.astrometry_net import AstrometryNet
from astropy.io import fits
from timeit import default_timer
import concurrent.futures
import functools


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

def run_in_parallel(func, iter_input):
    '''
    running a function in parallel.
    Parameters:
    -----------
        func: function, the function to be parallelized
        iter_input: list, the list of function inputs to loop over
    Returns:
    -----------
        results: list, entire function output
    '''
    print(len(iter_input))
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = list(executor.map(func,iter_input))
    return


def check_path_existence(all_paths=None):
    '''
    Creates directories if they do not exist

    Parameters:
    --------------
    all_paths: list, directory list to loop over
    '''
    for i,pi in enumerate(all_paths):
        if not os.path.exists(pi):
            if i < 2:
                print_stage('The path {:s} did not exist. It has now been made.'.format(pi),ch="-")
            os.makedirs(pi)
            #we give open access permissions to this newly made folder
            os.system('cd %s && cd .. && chmod 777 %s'%(pi,pi))
    return


def all_proc(iniconf,save_relevant,chip_num):

    chip_num = chip_num.strip(' ')
    all_flat_names, _ = gen_file_names(iniconf=iniconf,kind = "flats", chip_num = chip_num)

    # get the bad pixel mask
    bad_pix_mask = get_bad_pixel_mask(iniconf, all_flat_names, chip_num =chip_num, save_relevant = save_relevant)


        #compute the normalized flat
    norm_flat = imcombine_flats(iniconf,all_flat_names,bad_pix_mask,median_norm=True, chip_num = chip_num)

        #first create all the science file names so that they can be read easily
    all_sci_names, num_range_sci = gen_file_names(iniconf=iniconf,kind = "science",verbose=False,chip_num = chip_num)
        #list of coadded science images at each dither position is returned below
    all_sci_org_coadd_arrays = imcombine_science(iniconf,all_sci_names, num_range_sci, bad_pix_mask, chip_num = chip_num, save_relevant = save_relevant)

        #flat reduce all the coadded science images at each dither pos
    flat_reduced_sci_arrays,flat_reduced_sci_names = flat_reduce(iniconf, norm_flat, all_sci_org_coadd_arrays, num_range_sci,bad_pix_mask, chip_num = chip_num)

        #combine the flat fielded science images at different dither positions to estimate the sky
    sky_est = estimate_sky(iniconf, flat_reduced_sci_names, chip_num = chip_num, save_relevant = save_relevant)

        #sky subtract the science images
    sky_sub_scis = subtract_sky(iniconf,flat_reduced_sci_arrays, sky_est, num_range_sci, bad_pix_mask, chip_num = chip_num, save_relevant = save_relevant)

        #coadd all the science images at different dither positions into a master mosaic
    compute_mosaic(iniconf,sky_sub_scis, num_range_sci, chip_num = chip_num)
    
    obj_name = iniconf['all info']['obj_id']

    # if use_astrometry == False:
    print(obj_name +  ' chip ' + str(chip_num) + ' has been processed!!!')
        
    # if use_astrometry == True:
    #     # output_dir = os.getcwd() + "/final_outputs"
    #     output_dir = iniconf['all info']["output_dir"] + "/" + iniconf['all info']['obj_id'] 

    #     final_reduced_name = iniconf['all info']["final_reduced_name"]

    #     sci_range = iniconf['all info']['science'].split(",")
    #     common_tag = "_" + sci_range[0] + "_" + sci_range[1] + "_"
    #     final_name =  output_dir + "/" + final_reduced_name + common_tag + str(chip_num) + '.fits'
        
    #     ast = AstrometryNet()
    #     ast.api_key = api_key_str
    #     path = final_name
    #     hdu_list = fits.open(path , mode = 'update')
    #     hdr_= hdu_list[0].header

    #     #AstrometryNet.show_allowed_settings()

    #     # start of astrometry, outputs wcs header
    #     tstart = default_timer()
    #     wcs_header = ast.solve_from_image(path , force_image_upload=True, scale_est = 0.159,scale_units ='arcsecperpix', center_ra= RA, center_dec= DEC, radius = 1.2,solve_timeout=300)
    #     #wcs_header = ast.solve_from_image(path , force_image_upload=True, scale_est = 0.159,scale_units ='arcsecperpix',solve_timeout=200)
    #     tend = default_timer()

    #     print("match time = %.3g sec"%(tend-tstart))

    #     hdr_.update(wcs_header)
    #     itself = fits.open(path)[0].data
    #     prim_hdu = fits.PrimaryHDU(data=itself, header=hdr_)
    #     hdulist = fits.HDUList([prim_hdu])
    #     hdulist.writeto(path,overwrite=True)
    #     hdu_list.close()  
        # print(obj_name +  ' chip ' + str(chip_num) + ' has been processed!!!')
         
    return 


def run_astrometry(iniconf,chip_num):
    '''
    Function that runs astrometry on the filtered data
    '''

    RA = float(iniconf['all info']["ra"])
    DEC = float(iniconf['all info']["dec"])
    api_key_str = iniconf['all info']["api_key"]

    output_dir = iniconf['all info']["output_dir"] + "/" + iniconf['all info']['obj_id'] 

    final_reduced_name = "filtered_" + iniconf['all info']["final_reduced_name"]

    sci_range = iniconf['all info']['science'].split(",")
    common_tag = "_" + sci_range[0] + "_" + sci_range[1] + "_"
    final_name =  output_dir + "/" + final_reduced_name + common_tag + str(chip_num.replace(" ","")) + '.fits'
    
    ast = AstrometryNet()
    ast.api_key = api_key_str
    path = final_name
    hdu_list = fits.open(path , mode = 'update')
    hdr_= hdu_list[0].header

    #AstrometryNet.show_allowed_settings()

    # start of astrometry, outputs wcs header

    try:
        tstart = default_timer()
        wcs_header = ast.solve_from_image(path , force_image_upload=True, scale_est = 0.159,scale_units ='arcsecperpix', center_ra= RA, center_dec= DEC, radius = 0.6,solve_timeout=500)
        #wcs_header = ast.solve_from_image(path , force_image_upload=True, scale_est = 0.159,scale_units ='arcsecperpix',solve_timeout=200)
        tend = default_timer()

    # print("match time = %.3g sec"%(tend-tstart))

        hdr_.update(wcs_header)
        itself = fits.open(path)[0].data
        prim_hdu = fits.PrimaryHDU(data=itself, header=hdr_)
        hdulist = fits.HDUList([prim_hdu])
        hdulist.writeto(path,overwrite=True)
        hdu_list.close()  
        print(' %s astrometry for chip %s has finished in %.3g sec!!!'%(iniconf['all info']['obj_id'],str(chip_num),tend-tstart  )  )

    except:
        hdu_list.close()
        print(' %s astrometry for chip %s has timed out :('%(iniconf['all info']['obj_id'],str(chip_num) )  )

    return


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
    use_astrometry_str = iniconf['all info']['use_astrometry']
    mode_pro_str = iniconf['all info']['Parallel_or_Serial']

    main_dir = iniconf['all info']['output_dir']
    temp_dir = iniconf['all info']['temp_dir']
    #the folder that will contain the object now
    flat_dir = main_dir + "/flat_fields"
    main_obj_dir = main_dir + '/' + iniconf['all info']['obj_id']
    relevant_dir = main_obj_dir + "/relevant_fits"
    relevant_dir_1 = main_obj_dir + "/relevant_fits/bad_pix_masks"
    relevant_dir_2 = main_obj_dir + "/relevant_fits/coadded_org_sci"
    relevant_dir_3 = main_obj_dir + "/relevant_fits/flat_reduced_sci"
    relevant_dir_4 = main_obj_dir + "/relevant_fits/pre_mosaic_sci"
    relevant_dir_5 = main_obj_dir + "/relevant_fits/skies"
    relevant_dir_6 = main_obj_dir + "/relevant_fits/sky_subtract_sci"
    #check all the paths exist. If not, make em.
    check_path_existence(all_paths=[main_dir, main_obj_dir,temp_dir,flat_dir, relevant_dir,relevant_dir_1,relevant_dir_2,relevant_dir_3,relevant_dir_4,relevant_dir_5,relevant_dir_6   ])


    if save_relevant_str == 'True':
        save_relevant = True
    elif save_relevant_str == 'False':
        save_relevant = False
            
    ##run the data reduction
    if mode_pro_str == 'Parallel':
        partial_all_proc = functools.partial(all_proc, iniconf, save_relevant)
    
        run_in_parallel(partial_all_proc, all_chip_num)
        
    elif mode_pro_str == 'Serial':
        for chip_num in all_chip_num:
            all_proc(iniconf, save_relevant, chip_num)

    #to bad pixel reduction now
    run_badpix_filtering(iniconf=iniconf)

    #run astrometry now 
    if use_astrometry_str == "True":
        # if mode_pro_str == 'Parallel':
        partial_run_astrometry = functools.partial(run_astrometry, iniconf)
        run_in_parallel(partial_run_astrometry, all_chip_num)
        # elif mode_pro_str == 'Serial':
        #     for chip_num in all_chip_num:
        #         run_astrometry(iniconf,chip_num)

    else:
        pass

    return 






    





