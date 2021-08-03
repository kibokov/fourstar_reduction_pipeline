# FOURSTAR Data Reduction Pipeline

## Dependencies
This code will require a number of standard python packages, including:
* Standard utilities: numpy
* .fits file handling: astropy.io, imcombinepy (https://github.com/ysBach/imcombinepy)
* source finding: sep (https://sep.readthedocs.io/en/v1.1.x/)
* Shell/Command Line handling: os, sys, configparser, glob, argparse

The sep python packages will have to be installed. The other packages usually come with a default Python Anaconda installation. The imcombinepy package will be installed on running the setup.py script after cloning this repository.

## Setting up the Pipeline

Clone the repository onto your local machine by running below command in the directory of choice
```
> git clone https://github.com/kibokov/FOURSTAR_reduction_pipeline.git
```
Then run the setup.py script
```
> python3 setup.py
```

## Pipeline Structure 

The ```pipeline``` directory contains all the files needed to run the pipeline. You usually would not need to poke around in that directory. You will only need to work with files in the outermost folder like  ```sci_info.txt```. For details on what goes into this text file, look at the file itself. This pipeline has the capability of running data reduction on multiple objects in one go. This is only if all these objects have the same flat field. 

The ```pied_piper.py``` is the python script that will run the entire pipeline. It will read in the frame numbers from ```sci_info.txt```. It will loop over all the 4 chips one by one and reduce them. There is an option to run this process in 'Parallel' or in 'Serial'.

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

3. The final outputs will be stored in at the path provided in the ```sci_info.txt```. At this path, a folder is made for each object. All the reduced data for that object is stored in this folder. The "filtered_" tag in the file refers to the data that has been filtered for bad pixels using ring median filter.

## Some Notes

1. The image reduction pipeline is fairly quick. For example, it will take a total of 40 seconds to process a single chip where the a total of 5 science frames are used.

2. When the pipeline is being run, a number of warning messages will pop up like "FutureWarning: Using a non-tuple sequence for multidimensional indexing is deprecated". These are not a cause of worry. These are just some messages from the imcombinepy package. 

