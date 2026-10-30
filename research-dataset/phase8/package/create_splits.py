import pandas as pd
from sklearn.model_selection import train_test_split

file = "/home/k8s/phase8/experiments/ml_dataset.csv"

data = pd.read_csv(file)

train, test = train_test_split(data, test_size=0.2, random_state=42)

train, val = train_test_split(train, test_size=0.2, random_state=42)

train.to_csv("/home/k8s/phase8/splits/train.csv",index=False)
val.to_csv("/home/k8s/phase8/splits/validation.csv",index=False)
test.to_csv("/home/k8s/phase8/splits/test.csv",index=False)

print("Splits created")
