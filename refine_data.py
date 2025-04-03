import pandas as pd

df = pd.read_csv("sites.csv")
df["url"] = df["url"].apply(
    lambda x: (
        "https://" + str(x).strip()
        if not (str(x).startswith("https://") or str(x).startswith("http://"))
        else str(x).strip()
    )
)
df["url"] = df["url"].apply(lambda x: x.rstrip("/"))  # Remove trailing slashes
df["url"] = df["url"].apply(lambda x: x.rstrip("#"))  # Remove trailing hashes
df["url"] = df["url"].apply(lambda x: x.rstrip("?"))  # Remove trailing question marks
df["url"] = df["url"].apply(lambda x: x.rstrip("&"))  # Remove trailing ampersands
# Remove duplicate URLs
df = df.drop_duplicates(subset=["url"], keep="first")
df.to_csv("sites.csv", index=False)

print("URLs updated.")
