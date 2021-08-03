import numpy as np
import glob
from astropy.io import fits
import imcombinepy as imc
import sep
import os
from scipy import stats

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

def embed_single(org_array):
    '''
    Function that embeds the original 2048 x 2048 array into a larger 2d array so that a mosaic can be made
    This is done for both original science frame and its segmentation array

    '''
    ylen,xlen = np.shape(org_array)
    #this should be 2048 x 2048
    #ylen is the number of rows
    #xlen is the number of columns

    #if we have a 2048x 2048 array, we want to put this in an array 1.5 times larger 
    empty_array = np.ones(shape = (int(ylen*2), int(xlen*2)) )*(-100)
    #we just do times -100 so that those padded pixels can be easily identified later

    #now we embed this array
    empty_array[int(ylen/2):int(3*ylen/2),int(xlen/2):int(3*xlen/2)]=org_array

    return empty_array


def awesome(main_frame, sub_frame, sigma_thres, radius_thre):
    '''
    input:
    main_frame : the frame stands still (frame 0)
    sub_frame : the single frame gets moved (frame 1,2,3,4....)
    sigma_thres : sigma threshold used by sep for source extraction (do sth like 10 or 20)
    radius_thre : radius threshold for filtering potential bad pixels blended in the sources (do sth like 2 or 3)
    
    output:
    x_move, y_move : the x, y offset between main_frame and sub_frame
    ( for example,
    sub_frame = np.roll(sub_frame, x_move,axis = 1) 
    & sub_frame = np.roll(sub_frame, y_move,axis = 1)
    )
    '''
    
    #make sure data can go into sep
    main_frame = main_frame.copy(order='C')
    sub_frame = sub_frame.copy(order='C')
    
    
    #doing source extraction via sep
    bkg_main = sep.Background(main_frame)
    main_frame = main_frame - bkg_main
    objects_main = sep.extract(main_frame, sigma_thres, err=bkg_main.globalrms)
    
    bkg_sub = sep.Background(sub_frame)
    sub_frame = sub_frame - bkg_sub
    objects_sub = sep.extract(sub_frame, sigma_thres, err=bkg_sub.globalrms)
    
    #filter the sources that are too small (bad pixels)
    objects_main = objects_main[np.logical_not(np.isnan(objects_main['a']))&np.logical_not(np.isnan(objects_main['b']))]
    objects_sub = objects_sub[np.logical_not(np.isnan(objects_sub['a']))&np.logical_not(np.isnan(objects_sub['b']))]
    
    objects_main = objects_main[(( objects_main['a']**2 + objects_main['b']**2)**0.5 > radius_thre)]
    objects_sub = objects_sub[((objects_sub['a']**2+objects_sub['b']**2)**0.5 > radius_thre)]
    
    #get x,y of sources from each frame and filter the nan values
    objx_1to0 = (objects_sub['x'])[np.logical_not(np.isnan(objects_sub['x']))&np.logical_not(np.isnan(objects_sub['y']))]
    objy_1to0 = (objects_sub['y'])[np.logical_not(np.isnan(objects_sub['x']))&np.logical_not(np.isnan(objects_sub['y']))]
    
    objx_0 = (objects_main['x'])[np.logical_not(np.isnan(objects_main['x']))&np.logical_not(np.isnan(objects_main['y']))]
    objy_0 = (objects_main['y'])[np.logical_not(np.isnan(objects_main['x']))&np.logical_not(np.isnan(objects_main['y']))]
    
    #compute all the possible x offset between objs of two frames
    matrix_x0 = np.tile(objx_0, (len(objx_1to0), 1))
    matrix_x1 = np.tile(objx_1to0, (len(objx_0), 1 )).T
    delta_x = matrix_x0-matrix_x1

    #compute all the possible y offset between objs of two frames
    matrix_y0 = np.tile(objy_0, (len(objy_1to0), 1))
    matrix_y1 = np.tile(objy_1to0, (len(objy_0), 1 )).T
    delta_y = matrix_y0-matrix_y1

    #make them integers and combine the x and y axis
    int_delta_x = delta_x.astype(int)
    int_delta_y = delta_y.astype(int)
    
    new_mat = np.zeros((len(int_delta_x),len(int_delta_x[0]),2))
    new_mat[:,:,0]=int_delta_x
    new_mat[:,:,1]=int_delta_y

    new_mat = np.concatenate(new_mat, axis=0)
    
    #find out the (x,y) offset that appear the most frequently 
    u, counts = np.unique(new_mat, axis=0, return_counts=True)
    most = u[counts==np.max(counts)]
    x_move = most[0,0].astype(int)
    y_move = most[0,1].astype(int)
    
    return x_move, y_move
    

def shift_arrays(iniconf, shift_frame,xshift, yshift, num_sci, chip_num):
    '''
    Parameters:
    --------------
    xshift : int, the shift of main object in embedded array to the right 
    yshift: int, the shift of main object in embedded array to the bottom
    '''

    #first shift the shift frame

    # save_path = iniconf['all info']["pre_mosaic_sci"]
    # save_path = os.getcwd().replace('/scripts','') + '/pipeline/relevant_fits/pre_mosaic_sci'
    save_path = iniconf['all info']['output_dir'] + '/' + iniconf['all info']['obj_id'] + '/relevant_fits/pre_mosaic_sci' 

    save_name = iniconf['all info']["sci_name"]

    #we first shift the arrays in x and then in y
    shift_frame_x = np.roll(shift_frame,xshift,axis = 1)
    shift_frame_xy = np.roll(shift_frame_x, yshift, axis = 0)
    
    #before saving this as a fits, we convert all the -100 to a nan

    shift_frame_xy[shift_frame_xy == -100] = np.nan

    shift_name = save_path + "/" + save_name + "_" + num_sci + "_" + str(chip_num) + "_pre_mosaic_sci.fits"
    #save these shifted arrays so that they can be imcombined
    save_fits(shift_frame_xy, shift_name,header = True )

    return shift_name


def compute_mosaic(iniconf,all_sci_frames, num_range_sci, chip_num = None):
    '''
    The function that uses the pixel offsets between each dither position in science images to combine them
    into a total mosaic. 
    '''

    #we trim the science frames from the edges to avoid weird edge effects
    all_sci_frames = np.array(all_sci_frames)
    all_sci_frames = all_sci_frames[:, 10:len(all_sci_frames)-10,50:len(all_sci_frames)-50]
    
    all_sci_embed = []

    for k in range(len(all_sci_frames)):
        sci_embed = embed_single(all_sci_frames[k])
        all_sci_embed.append(sci_embed)
    
    
    main_sci_frame = all_sci_embed[0]
    other_sci_frames = all_sci_embed[1:]

    #now compute the shifts
    all_xshifts = []
    all_yshifts = []

    for k in range(len(other_sci_frames)):

        tempx,tempy = awesome(main_sci_frame,other_sci_frames[k], 10, 2.5)

        all_xshifts.append(tempx)
        all_yshifts.append(tempy)

    all_pre_mosaic_names = []

    main_sci_frame[main_sci_frame == -100] = np.nan
        

    # save_path = iniconf['all info']["pre_mosaic_sci"]
    # save_path = os.getcwd().replace('/scripts','') + '/pipeline/relevant_fits/pre_mosaic_sci'
    save_path = iniconf['all info']['output_dir'] + '/' + iniconf['all info']['obj_id'] + '/relevant_fits/pre_mosaic_sci' 


    save_name = iniconf['all info']["sci_name"]
    #save the main frame first 
    main_name = save_path + "/" + save_name + "_" + num_range_sci[0] + '_' + str(chip_num)+ "_pre_mosaic_sci.fits" 
    #save these shifted arrays so that they can be imcombined
    save_fits(main_sci_frame, main_name, header=True)

    for k in range(len(all_xshifts)):
        temp_name = shift_arrays(iniconf, other_sci_frames[k] ,all_xshifts[k], all_yshifts[k],num_range_sci[1:][k],chip_num)
        all_pre_mosaic_names.append(temp_name)
        
    all_pre_mosaic_names.append( main_name)

    #now add all the mosaic using imcombine method 

    kw = dict(combine='mean', zero="median", reject=None, memlimit=5.e+9)

    output_dir = iniconf['all info']["output_dir"] + "/" + iniconf['all info']['obj_id'] 
    # output_dir = os.getcwd() + "/final_outputs" 

    final_reduced_name = iniconf['all info']["final_reduced_name"]

    sci_range = iniconf['all info']['science'].split(",")
    common_tag = "_" + sci_range[0] + "_" + sci_range[1] + "_" 

    final_name =  output_dir + "/" + final_reduced_name + common_tag + str(chip_num) + '.fits'

    imc.fitscombine(fpaths = all_pre_mosaic_names, offsets=None,output=final_name, overwrite=True,**kw)

    #as all pre_mosaics have been combined. we delete all the premosaic files
    for fii in all_pre_mosaic_names:
        os.remove(fii)


    return

