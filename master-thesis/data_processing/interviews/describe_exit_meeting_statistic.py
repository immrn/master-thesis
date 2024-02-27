import pandas as pd

df = pd.read_csv("./raw_data/exit_meeting.csv")

# Get counts for each column (excluding 'id')
column_counts = {col: df[col].value_counts() for col in df.columns if col != 'id'}

# Print counts for each column
for col, counts in column_counts.items():
    print()
    print(counts)