#########################################################################
#                                                                       #
# Project           :                                                   #
#                                                                       #
# Program name      : feature-selection.py                              #
#                                                                       #
# Authors           : Kétly Gonçalves Machado, Daniel Macêdo Batista    #
#                                                                       #
# Purpose           :                                                   #
#                                                                       #
#########################################################################


import argparse
import csv
import pandas as pd

# Parser to argument f, which determines the file to perform feature selection
parser = argparse.ArgumentParser(description = "Feature Selection")
parser.add_argument("-f", action = "store", dest = "f", required = True,
                    help = "File to perform feature selection.")

args = parser.parse_args()

# Constructs a dataframe based on the csv file
data = pd.read_csv(args.f)

# Features from the original data
cols = ["pkSeqID","stime","flgs","proto","saddr","sport","daddr","dport","pkts","bytes","state","ltime",
        "seq","dur","mean","stddev","smac","dmac","sum","min","max","soui","doui","sco","dco","spkts",
        "dpkts","sbytes","dbytes","rate","srate","drate","attack","category","subcategory"]

data.columns = cols

# Removing unwanted features from data (according to previous analysis)
# axis = 1 means columns
data = data.drop(["pkSeqID", "stime", "flgs", "saddr", "daddr", "seq", "dur", "stddev", "smac", "dmac", 
                    "soui", "doui", "sco", "dco", "category", "subcategory"], axis=1)

# Drops instances with NaN values on features sport and dport and alters its data type
data = data.dropna(axis = 0)
data["sport"] = pd.to_numeric(data["sport"], errors="coerce")
data["dport"] = pd.to_numeric(data["dport"], errors="coerce")

# Converts categorical features to dummies and adds it to the data
data = pd.concat([data, pd.get_dummies(data["proto"])], axis=1)
data = pd.concat([data, pd.get_dummies(data["state"])], axis=1)

# Drops categorical features after previous step
data = data.drop(["proto", "state"], axis=1)

# Drops label column and adds it to the end
label = data["attack"]
data = data.drop(["attack"], axis=1)
data = pd.concat([data, label], axis=1)

# Drops features after correlation analysis
#data = data.drop(["sport", "dport", "mean", "min", "max", "rate", "srate", "icmp", "ipv6-icmp",
#                  "tcp", "udp", "ACC", "INT", "NRS", "REQ", "RST", "URP"], axis=1)
data = data[["ltime", "attack"]]

#data.to_csv(args.f[0:-4] + "-fs" + ".csv", index = False)
#data = data.sample(frac=1)
data.to_csv(args.f[0:-4] + "-eefs" + ".csv", index = False)

ni = len(data[data["attack"] == 0].index)
ai = len(data[data["attack"] == 1].index)

print("After Preliminary Feature Selection...")
print(f"Total normal instances = {ni}")
print(f"Total DDoS attack instances = {ai}")
print(f"Final number of instances (normal + attack) = {ni + ai}")
print("\n")