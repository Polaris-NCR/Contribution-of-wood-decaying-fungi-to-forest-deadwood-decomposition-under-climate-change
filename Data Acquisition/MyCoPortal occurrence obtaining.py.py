import zipfile
import os
import pandas as pd
from pathlib import Path
import pandas as pd
import csv, json, time, random, sys
from io import BytesIO, StringIO
from zipfile import ZipFile

import numpy as np
import requests, pandas as pd
from tenacity import retry, stop_after_attempt, wait_random_exponential
from tqdm import tqdm


SPECIES_FILE = "species.txt"  
OUTDIR = Path(r"G:\Fungi\data")  
SYMBIOTA_URL = "https://www.mycoportal.org/portal/api/v2/occurrence/search"
GBIF_SEARCH = "https://api.gbif.org/v1/occurrence/search"
GBIF_DOWNLOAD = "https://api.gbif.org/v1/occurrence/download/request"
MAX_ROWS = 200_000  
PER_PAGE = 1000 
POLL_SEC     = 30                   
TIMEOUT_MIN  = 40                    


OUTDIR.mkdir(exist_ok=True)

session = requests.Session()
session.headers.update({"User-Agent":
                            "Mozilla/5.0 (compatible; MycoPortalBulk/1.0; +https://github.com/EmmaA)"})


@retry(stop=stop_after_attempt(5), wait=wait_random_exponential(multiplier=1, max=20))
def get_json(url, params):
    r = session.get(url, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def fetch_symbiota(species):
    records = []
    page = 1
    while True:
        payload = {
            "taxon": species,
            "per_page": PER_PAGE,
            "page": page,
            "include": "coordinates,dataset",
        }
        data = get_json(SYMBIOTA_URL, payload)
        recs = data.get("data", [])
        if not recs:
            break
        records.extend(recs)
        if len(records) >= MAX_ROWS or page >= data["meta"]["last_page"]:
            break
        page += 1
        time.sleep(0.8) 
    if not records:
        return None 

    df = (pd.json_normalize(records)
          .rename(columns=lambda c: c.replace(".", "_")))
    return df


def gbif_taxon_key(scientificName):
    js = get_json("https://api.gbif.org/v1/species/match",
                  {"name": scientificName})
    return js.get("acceptedUsageKey") or js.get("usageKey")

def gbif_download_key(taxonKey):
    body = {
        "creator": "emma.api@example.com",
        "notification_address": ["emma.api@example.com"],
        "sendNotification": "false",
        "format": "SIMPLE_CSV",
        "predicate": {
            "type": "equals",
            "key": "TAXON_KEY",
            "value": str(taxonKey)
        }
    }
    r = session.post(GBIF_DOWNLOAD, json=body, timeout=60)
    r.raise_for_status()
    return r.text.strip()


def gbif_wait_and_dl(jobkey, outfile):
    status_url = f"https://api.gbif.org/v1/occurrence/download/{jobkey}"
    while True:
        st = session.get(status_url, timeout=10).json()
        if st["status"] in ("SUCCEEDED", "KILLED", "CANCELLED"):
            break
        time.sleep(30)
    if st["status"] != "SUCCEEDED":
        return False
    dl_url = f"https://api.gbif.org/v1/occurrence/download/request/{jobkey}.zip"
    r = session.get(dl_url, timeout=600)
    with open(outfile, "wb") as f:
        f.write(r.content)
    return True


def fetch_gbif(species):
    key = gbif_taxon_key(species)
    if not key:
        return None
    jobkey = gbif_download_key(key)
    zip_path = OUTDIR / f"{species.replace(' ', '_')}_gbif.zip"
    ok = gbif_wait_and_dl(jobkey, zip_path)
    return zip_path if ok else None


def fetch_gbif_open(species):
    key = gbif_taxon_key(species)
    if not key:
        return None

    rows, offset, limit = [], 0, 300
    while True:
        res = get_json(GBIF_SEARCH,
                       {"taxonKey": key, "offset": offset, "limit": limit})
        batch = res.get("results", [])
        if not batch:
            break
        rows.extend(batch)
        offset += limit
        if offset >= MAX_ROWS:
            break
        time.sleep(0.7) 
    if not rows:
        return None

    df = (pd.json_normalize(rows)
          .rename(columns=lambda c: c.replace(".", "_")))
    outzip = OUTDIR / f"{species.replace(' ', '_')}_gbif.zip"
    with ZipFile(outzip, "w") as z:
        z.writestr(f"{species.replace(' ', '_')}.csv",
                   df.to_csv(index=False).encode("utf-8"))
    return outzip

file_path = r"G:\Fungi\Name.xls"
df = pd.read_excel(file_path, sheet_name=0, header=None)
data_list = df.values.tolist()
data_list = np.array(data_list)
spp = data_list[1:, 1].tolist()
FOLDER = Path(r"G:\Fungi\data")
ARCHIVE_EXTS = {
    ".zip", ".rar", ".7z",
    ".tar", ".tar.gz", ".tar.bz2", ".tar.xz",
    ".gz", ".bz2", ".xz"
}
archives = [
    p.name
    for p in FOLDER.iterdir()  # 不递归
    if p.is_file() and any(p.name.lower().endswith(ext) for ext in ARCHIVE_EXTS)
]
archives = [arc[:-9] for arc in archives]
archives = [s.replace('_', ' ') for s in archives]
spp = [species for species in spp if species not in archives]
print(len(spp))
spp = spp[750:1000]
print(spp)


def main():
    for sp in tqdm(spp, desc="Download"):
        safe = sp.replace(" ", "_")
        try:

            df = fetch_symbiota(sp)
            if df is not None:
                outzip = OUTDIR / f"{safe}.zip"
                csv_bytes = df.to_csv(None, index=False).encode("utf-8")
                with ZipFile(outzip, "w") as zf:
                    zf.writestr(f"{safe}.csv", csv_bytes)
                tqdm.write(f"✅ {sp} — Symbiota v2 ({len(df)} rows)")
                continue
            
            z = fetch_gbif_open(sp)
            if z:
                tqdm.write(f"✅ {sp} — GBIF backup ({z.name})")
            else:
                tqdm.write(f"⚠️  {sp} — no data in Symbiota/GBIF")
        except Exception as e:
            tqdm.write(f"‼️  {sp} — {type(e).__name__}: {e}")
            time.sleep(5) 


if __name__ == "__main__":
    main()
    folder_path = r'G:\Fungi\data'
    output_csv = r'G:\Fungi\merged_output.csv'

    merged_df = pd.DataFrame()


    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        print(file_path)

        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                csv_file = zip_ref.namelist()[0]

                with zip_ref.open(csv_file) as my_file:
                    temp_df = pd.read_csv(my_file)
                    merged_df = pd.concat([merged_df, temp_df], ignore_index=True)

    merged_df.to_csv(output_csv, index=False)