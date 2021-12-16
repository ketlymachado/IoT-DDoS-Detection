import pandas as pd

data = pd.read_csv("../processed-data/CSV/botiot-ap-1-2f-dport-resampled.csv")

cols = ["dport", "CON", "attack"]

data.columns = cols

botiot = data.sample(frac=1)

botiot.to_csv("../processed-data/CSV/botiot-ap-1-2f-dport-resampled-shuffled.csv", index = False)

print("Shuffled dataset stored in botiot-ap-1-2f-dport-resampled-shuffled.csv.")