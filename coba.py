import pandas as pd

# Contoh DataFrame
data = {'Schedule': [100, 200, 300], 'OtherColumn': [1, 2, 3]}
df = pd.DataFrame(data)

# Mengubah DataFrame menjadi array
array = df.to_numpy()

schedule_array = df['Schedule'].to_numpy()
print(schedule_array)

