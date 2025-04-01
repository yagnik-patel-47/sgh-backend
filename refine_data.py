import pandas as pd

df = pd.read_csv("sites.csv")
df["url"] = df["url"].apply(
    lambda x: (
        "https://" + str(x)
        if not (str(x).startswith("https://") or str(x).startswith("http://"))
        else str(x)
    )
)
df["url"] = df["url"].apply(lambda x: x.rstrip("/"))  # Remove trailing slashes
df["url"] = df["url"].apply(lambda x: x.rstrip("#"))  # Remove trailing hashes
df["url"] = df["url"].apply(lambda x: x.rstrip("?"))  # Remove trailing question marks
df["url"] = df["url"].apply(lambda x: x.rstrip("&"))  # Remove trailing ampersands

df.to_csv("sites.csv", index=False)

print("URLs updated.")
