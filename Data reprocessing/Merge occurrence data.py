import zipfile
import os
import math
import pandas as pd

# === 配置 ===
folder_path = r'G:\Fungi\data'   
output_dir  = r'G:\Fungi\merge'          
batch_size  = 200                    
csv_encoding = None                         


os.makedirs(output_dir, exist_ok=True)


zip_files = [f for f in sorted(os.listdir(folder_path))
             if zipfile.is_zipfile(os.path.join(folder_path, f))]

total_batches = math.ceil(len(zip_files) / batch_size)
print(total_batches)
for batch_idx in range(total_batches):
    print('batch',batch_idx+1)
    start = batch_idx * batch_size
    end   = start + batch_size
    batch_files = zip_files[start:end]

    merged_df = []  

    for zname in batch_files:
        zpath = os.path.join(folder_path, zname)
        with zipfile.ZipFile(zpath, 'r') as zf:

            csv_members = [m for m in zf.namelist() if m.lower().endswith('.csv')]
            if not csv_members:
                continue
            with zf.open(csv_members[0]) as csvfile:
                df = pd.read_csv(csvfile, encoding=csv_encoding)
                merged_df.append(df)


    if merged_df: 
        combined = pd.concat(merged_df, ignore_index=True)
        out_name = os.path.join(output_dir, f'merged_batch_{batch_idx+1:03}.csv')
        combined.to_csv(out_name, index=False)
        print(f'[{batch_idx+1}/{total_batches}] finish: {out_name}')
    else:
        print(f'[{batch_idx+1}/{total_batches}] jump')

print('Finish all!')
