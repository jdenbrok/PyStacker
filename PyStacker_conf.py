"""
This is a wrapper to perform stacking either using an existing PyStructure, or prepared input 3D cubes.

MODIFICATION HISTORY
    -   v1.0 21 January 2023
"""
__author__ = "J. den Brok"
__version__ = "v1.0"
__email__ = "jakob.den_brok@cfa.harvard.edu"
__credits__ = ["L. Neumann","M. Jimenez-Donaire", "E. Rosolowsky","A. Leroy "]


#general modules needed for routines
import numpy as np
import pandas as pd
import os.path
from os import path
import shutil
from astropy.io import fits
from datetime import date
import argparse
import configparser
today = date.today()
date_str = today.strftime("%Y_%m_%d")

#import relevant PyStructure and PyStacker functions
import sys
sys.path.append("./scripts_PyStructure/")
sys.path.append("./scripts_stacking/")
from stacking import *

from create_database import *


#Step 1: Prepare ------------------------------------------------
#require input of config file
parser = argparse.ArgumentParser(description="Run PyStacker")
parser.add_argument("-c","--config",required = True)
parser.add_argument("-m","--mode",required = True,choices=['PyStruc', '3D_cube'], type = str, help = "PyStruc or 3D_cube")
args, leftovers = parser.parse_known_args()


conf_file = args.config
mode = args.mode


if mode == "PyStruc":
    
   
    #load in the configure file
    config = configparser.ConfigParser()
    config.read(conf_file)
    
    conf_default = {item[0]: eval(item[1]) for item in config.items('Default')}
    conf_optional = {item[0]: eval(item[1]) for item in config.items('Optional')}
    
    get_stack(conf_default["fnames"], conf_default["prior"], conf_default["lines"], conf_default["final_direc"], dir_data = conf_default["data_direc"], xtype = conf_default["xtypes"], **conf_optional)



elif mode == "3D_cube":

    #generate a folder for temporary files
    if os.path.exists("./Temp_Files/"):
        shutil.rmtree('./Temp_Files')
    os.makedirs("./Temp_Files/")
    
    stack_file = './Temp_Files/stack_temp.txt'
    cube_file = './Temp_Files/cube_list_temp.txt'
    
   
    
    #load in the configure file
    config = configparser.ConfigParser()
    config.read(conf_file)
   
    conf_default = {item[0]: eval(item[1]) for item in config.items('Default')}
    conf_optional = {item[0]: eval(item[1]) for item in config.items('Optional')}
    conf_bands = {item[0]: eval(item[1]) for item in config.items('Band')}
    conf_cubes = {item[0]: eval(item[1]) for item in config.items('Cubes')}
    
  
    with open(cube_file,'a') as cube_f:
        for cube in conf_cubes:
            cube_f.write(cube+", "+conf_cubes[cube][0]+", "+conf_cubes[cube][1]+"\n")
    
    with open(stack_file,'a') as band_f:
        for band in conf_bands:
            band_f.write(band+", "+conf_bands[band][0]+", "+conf_bands[band][1]+"\n")
   
    
    input = [conf_default["sources"],
            conf_default["ra_ctr"],
            conf_default["dec_ctr"],
            conf_default["posang_deg"],
            conf_default["incl_deg"],
            conf_default["dist_mpc"],
            conf_default["target_res"],
            conf_default["max_rad"],
            conf_default["data_direc"],
            conf_default["spacing_per_beam"],
            conf_default["velocity_map"],
            "./Temp_Files/",
            [conf_default["naxis_shuff"], conf_default["cdelt_shuff"]]]
     
    
    
    #create the file
    fnames = create_database(input,stack_file,cube_file,)
    head_tail = path.split(fnames[0])
    #add the shuffeling
    
   
    get_stack([head_tail[1]], conf_default["prior"], conf_default["lines"], conf_default["final_direc"], dir_data = head_tail[0]+"/", xtype = conf_default["xtypes"], **conf_optional)
    #perform the stacking
    
    #remove the temporary folder after the run is finished
    shutil.rmtree('./Temp_Files')
    
   
    

 
