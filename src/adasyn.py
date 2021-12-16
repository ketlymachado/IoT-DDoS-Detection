import pandas as pd
from imblearn.over_sampling import ADASYN
from collections import Counter

data = pd.read_csv("../processed-data/CSV/botiot-ap-1-2f-dport.csv")

cols = ["dport", "CON", "attack"]

data.columns = cols

# Turning Dataframe to Numpy Arrays

# All columns except the last
X = data.iloc[:,:-1].values

# Only the last column
y = data.iloc[:,-1].values

print(f"Shape of Feature Matrix: {X.shape}")
print(f"Shape of Target Vector: {y.shape}")

print()
print(f"Original Target Variable Distribution: {Counter(y)}")

adasyn = ADASYN(sampling_strategy = "minority", n_neighbors = 5)

print("\nResampling the data...\n")
X_res, y_res = adasyn.fit_resample(X, y)

print(f"Resampled Target Variable Distribution: {Counter(y_res)}")

print("\nTurning Numpy Arrays to Dataframe...\n")

cols = ["dport", "CON"]

botiot = pd.DataFrame(X_res, columns=cols)

botiot["attack"] = y_res

botiot.to_csv("../processed-data/CSV/botiot-ap-1-2f-dport-resampled.csv", index = False)

print("Resampled dataset stored in botiot-ap-1-2f-dport-resampled.csv.")