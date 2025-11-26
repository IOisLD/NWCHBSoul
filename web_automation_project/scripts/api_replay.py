import pandas as pd
import requests

def replay_post_excel(filepath="results/api_post_logs.xlsx"):
    df = pd.read_excel(filepath)
    for idx, row in df.iterrows():
        url = row["url"]
        headers = eval(row["headers"])  # convert string back to dict
        payload = row["post_data"]
        response = requests.post(url, json=payload, headers=headers)
        print(f"POST to {url} -> {response.status_code}")

if __name__ == "__main__":
    replay_post_excel()
