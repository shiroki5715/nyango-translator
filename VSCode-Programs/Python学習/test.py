import pandas as pd

# データフレームを作成
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [24, 28, 22],
    'City': ['New York', 'Los Angeles', 'London']
})

# データフレームを表示
print(df)

# 'Age'列の平均を計算
average_age = df['Age'].mean()
print(f'Average Age: {average_age}')

# 'City'が'London'の行をフィルタリング
df_london = df[df['City'] == 'London']
print(df_london)
