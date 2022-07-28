from glob import glob
import numpy as np
import os
from scipy import stats
import pandas as pd
import pingouin as pg


def get_well_framerate(path,well):
    
    arrayPos_well = 0
    framePos_time = 0
    list_frames = glob(path+"/-"+str(well)+"*")
    frame_time = np.zeros([2,int(len(list_frames)/2)])
    
    for i in list_frames:
        i = i.rsplit("\\",1)[1]
        
        if ".tif" in i:
            
            #well=i.lstrip("-").split("--")[0]

            time = int(i.lstrip("-").split("--T")[2].split("--")[0])
            channel = i.lstrip("-").split("--CO")[1].split("--")[0]
            
            if (channel == "4") or (channel== "5"):
                channelPos = 0
            elif channel == "6":
                channelPos = 1
                if framePos_time == int(len(list_frames)/2):
                    framePos_time = 0 
               
            #print(channelPos,framePos_time)
            frame_time[channelPos,framePos_time] = time
            framePos_time += 1
    mean_frame_time = np.mean(np.mean(np.diff(frame_time,axis=1),axis=1))
    sum_frame_time = np.mean(np.sum(np.diff(frame_time,axis=1),axis=1))
    if mean_frame_time == np.nan:
        mean_frame_time = 0
    return (mean_frame_time, sum_frame_time)

def joined_find(folder, subfolder, keyword, folder_measurements = "Measurements", file_type = ".xlsx", exclude = False):
    measurements = os.path.join(folder, subfolder,folder_measurements).replace("\\","/")
    
    if exclude:
        measurements_file_search = os.path.join(measurements,"*{}{}".format(keyword, file_type))
        
    else:
        measurements_file_search = os.path.join(measurements,"*{}*{}".format(keyword, file_type))
        
    measurements_file_path = glob(measurements_file_search)
    return measurements_file_path

def assign_compounds(value,dict_compound):
    #assign_compounds("A1")
    n = [j for i,j in zip(dict_compound.values(),dict_compound.keys()) if value in i.values()];
    if n == []:
        return "Blank"
    else:
        return n[0]


def assign_phase(time,dict_program_clean):
    n = dict_program_clean.get(time)
    return n

def negpos_scale(df_):
    df_scale = df_.copy()

    df_scale[df_ < 0] = df_[df_ < 0] / df_[df_ < 0].min().abs()
    df_scale[df_ > 0] = df_[df_ > 0] / df_[df_ > 0].max() 
    return df_scale

# assign stars to p-values
def sign_stars(df_in,form="symbol"):
    df_sign_ref = df_in.copy()
    df_sign = df_in.copy()
    if form == "symbol":
        df_sign[(df_sign_ref > 0.05)] = "ns"
        df_sign[(df_sign_ref < 0.05)&(df_sign_ref > 0.01)] = "*"
        df_sign[(df_sign_ref < 0.01)&(df_sign_ref > 0.001)] = "**"
        df_sign[(df_sign_ref < 0.001)]= "***"
    elif form == "num":
        df_sign[(df_sign_ref > 0.05)] = 0
        df_sign[(df_sign_ref < 0.05)&(df_sign_ref > 0.01)] = 1
        df_sign[(df_sign_ref < 0.01)&(df_sign_ref > 0.001)] = 2
        df_sign[(df_sign_ref < 0.001)]= 3
    return df_sign


# Calculate the difference between the sample Control and the global Control medians and correct all experiments to the global median
def standardize_globalMedian(df_,collist_x, reference, index_columns):
    df_selcols = df_.reset_index()[collist_x].set_index("Drug")

    if type(index_columns) == list: 
        drop_ = ["Experiment ID"] + index_columns
        index_ = ["Experiment ID","Drug"] + index_columns

    else:
        drop_ = ["Experiment ID"] + [index_columns]
        index_ = ["Experiment ID","Drug"] + [index_columns]

    global_control_medians = df_selcols.drop(drop_,axis=1).loc["Control"].median()
    norm_delta = df_selcols.loc["Control"].groupby(["Experiment ID"]).median() - global_control_medians
    norm_delta = norm_delta.drop("Concentration (µM)",axis=1)
    df_standardized_x = df_selcols.reset_index().set_index(index_) - norm_delta
    df_standardized_x[df_standardized_x < 0] = 0 
    return df_standardized_x

# Calculate different statistics on a dataframe always compared to the control.
def calculate_stats(df_,func,list_drugs,measurement_x, concentrations = False):
    """ Calculate different statistics on a dataframe always compared to the control.
        
        df_ : pandas dataframe with column Experiment ID and Drug and measurements as listed in measurements_x
        
        measurements_x: list of measurements
        
        concentrations: if True requires column "Concentration µM", now different concentrations are considered in the calculations
        
        func: 
            mannWhitney" --> Mann-Whitney-U test 
            effSize" --> hedges effect size 
            deltaMedian" --> relative difference to the median
    """
    readout = {}
    measure = {}
    
    for drug in list_drugs[1:]:
        expids = df_.set_index("Drug").loc[drug]["Experiment ID"].unique()  
        x = df_.set_index(["Experiment ID","Drug"]).loc[expids].droplevel(0).loc["Control"]     
        if concentrations:
            y = df_.set_index(["Drug","Concentration (µM)"]).loc[drug]
            
            conc = {}
            for concentration in y.index.unique():
                measure = {}
                for col_i in measurement_x:
                    y_conc = y.loc[concentration]
                    if func == "mannWhitney":
                        measure[col_i]=stats.mannwhitneyu(x[col_i].replace([np.inf, -np.inf], np.nan).dropna(),y_conc[col_i].replace([np.inf, -np.inf], np.nan).dropna())[1]
                    elif func == "effSize":
                        measure[col_i]=pg.compute_effsize(x[col_i].replace([np.inf, -np.inf], np.nan).dropna(),y_conc[col_i].replace([np.inf, -np.inf], np.nan).dropna(),eftype='hedges')
                    elif func == "deltaMedian":
                        measure[col_i]= (y_conc[col_i].replace([np.inf, -np.inf], np.nan).dropna().median() - x[col_i].replace([np.inf, -np.inf], np.nan).dropna().median() ) / x[col_i].dropna().median()
                    conc[concentration] = measure
                readout[(drug, concentration)]=conc[concentration]
        
        else:
            y = df_.set_index(["Drug"]).loc[drug]
            measure = {}

            for col_i in measurement_x:
                if func == "mannWhitney":
                    measure[col_i]=stats.mannwhitneyu(x[col_i].replace([np.inf, -np.inf], np.nan).dropna(),y[col_i].replace([np.inf, -np.inf], np.nan).dropna())[1]
                elif func == "effSize":
                    measure[col_i]=pg.compute_effsize(x[col_i].replace([np.inf, -np.inf], np.nan).dropna(),y[col_i].replace([np.inf, -np.inf], np.nan).dropna(),eftype='hedges')
                elif func == "deltaMedian":
                    measure[col_i]= (y[col_i].replace([np.inf, -np.inf], np.nan).dropna().median() - x[col_i].replace([np.inf, -np.inf], np.nan).dropna().median() ) / x[col_i].dropna().median()

            readout[drug]=measure

    return pd.DataFrame(readout).T