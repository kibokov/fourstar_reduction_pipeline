# FOURSTAR Data Reduction Pipeline

## Dependencies
This code will require a number of standard python packages, including:
* Standard utilities: numpy
* .fits file handling: astropy.io, imcombinepy (\url{https://github.com/ysBach/imcombinepy})
* source finding: sep (https://sep.readthedocs.io/en/v1.1.x/)
* Shell/Command Line handling: os, sys, configparser, glob, argparse

The imcombine and sep python packages will have to be installed. The other packages usually come with a default Python Anaconda installation.


## Setting up the Pipeline

Clone the repository onto your local machine by running below command in the directory of choice
```
> git clone https://github.com/kibokov/
```

## Pipeline Structure 

The ```pipeline``` directory contains all the files needed to run the pipeline. You usually would not need to poke around in that directory. You will only need to work with files in the outermost folder like  ```sci_info.txt```.  You will put all information needed for image reduction in ```sci_info.txt```.  This txt file contains the information of which band is being reduced (this is for file naming purposes), the FOURSTAR data path, flat frame range and science frame range.  You can also provide difference science frame ranges to reduce as well. More details on the format and examples are given inside the txt file.

The ```pied_piper.py``` is the python script that will run the entire pipeline. It will read in the frame numbers from ```sci_info.txt```. It will loop over all the 4 chips one by one and reduce them.

Inside the  ```pipeline``` directory, the ```relevant_fits``` directory contains all fits files that were useful during the image reduction process like master flats, bad pixel masks etc. The master flats and bad pixel masks will always be stored. Some of the other files during the reduction process need to saved as well and will be saved there (eg. flat reduces science images). However, if you do not wish for these files to accumulate over time and be saved, you can turn the ```save_relevant``` flag to ```False``` in the ```fourstar_pipeline.ini``` file in ```pipeline``` directory, . By default it is at False.

## Running the Pipeline

1. Modify the  ```sci_info.txt``` file. Provide it information about the flat frames numbers, science frames etc. 

2. Run the pipeline by
```
> python3 pied_piper.py
```
The above command by default reads the ```sci_info.txt``` file. However, in case you change the name or wish to provide a different one, you can specify that through the ini fiag as below
```
> python3 pied_piper.py -t sci_info.txt
```

3. The final outputs will be stored in the ```final_outputs``` directory.


## Some Notes

1. The image reduction pipeline is fairly quick. For example, it will take a total of 40 seconds to process a single chip where the a total of 5 science frames are used.

2. When the pipeline is being run, a number of warning messages will pop up like "FutureWarning: Using a non-tuple sequence for multidimensional indexing is deprecated". These are not a cause of worry. These are just some messages from the imcombinepy package. 

3. In the very final step when the reduced science images at each dither position is going to be coadded into a single mosaic, in this very final step, pixel rejection is not implemented. This is because a separate pixel rejections scheme will be applied on these files. The complete integration is yet to happen.

