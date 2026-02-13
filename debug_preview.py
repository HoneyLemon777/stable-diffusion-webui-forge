"""Debug script: Simulate find_preview logic to identify why thumbnails don't appear"""
import os
import sys
import sqlite3
import json

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("Civitai Helper Thumbnail Debug")
print("=" * 60)

# 1. Check preview files exist
sd_dir = r"D:\AntiGravity_Products\StableDiffusion_Project\models\Stable-diffusion"
lora_dir = r"D:\AntiGravity_Products\StableDiffusion_Project\models\Lora"

print("\n--- 1. Preview file check ---")
for d in [sd_dir, lora_dir]:
    previews = [f for f in os.listdir(d) if ".preview." in f]
    models = [f for f in os.listdir(d) if f.endswith((".safetensors", ".ckpt"))]
    print(f"\n{os.path.basename(d)}/:")
    print(f"  Models: {len(models)}")
    print(f"  Previews: {len(previews)}")
    
    models_with_preview = 0
    models_without_preview = 0
    for m in models:
        base = os.path.splitext(m)[0]
        preview = base + ".preview.png"
        exists = os.path.isfile(os.path.join(d, preview))
        if exists:
            models_with_preview += 1
        else:
            models_without_preview += 1
            print(f"  MISSING: {preview}")
    print(f"  With preview: {models_with_preview}")
    print(f"  Without preview: {models_without_preview}")

# 2. Simulate MassFileLister logic
print("\n--- 2. MassFileLister simulation ---")
for d in [sd_dir, lora_dir]:
    entries = list(os.scandir(d))
    files_lower = {}
    files_cased = {}
    for entry in entries:
        try:
            st = entry.stat(follow_symlinks=False)
            data = (entry.name, st.st_mtime, st.st_ctime)
            files_lower[entry.name.lower()] = data
            files_cased[entry.name] = data
        except Exception as e:
            print(f"  scandir error: {entry.name}: {e}")
    
    print(f"\n{os.path.basename(d)}/:")
    print(f"  Total scandir entries: {len(entries)}")
    
    models = [f for f in os.listdir(d) if f.endswith((".safetensors", ".ckpt"))]
    found_count = 0
    not_found_count = 0
    for m in models:
        base = os.path.splitext(m)[0]
        found = False
        for ext in ["png", "jpg", "jpeg", "webp", "gif"]:
            for pattern in [f"{base}.{ext}", f"{base}.preview.{ext}"]:
                if pattern in files_cased or pattern.lower() in files_lower:
                    found = True
                    break
            if found:
                break
        if found:
            found_count += 1
        else:
            not_found_count += 1
            print(f"  NOT FOUND by lister: {m}")
    print(f"  Found by lister: {found_count}")
    print(f"  Not found by lister: {not_found_count}")

# 3. Check cache.db
print("\n--- 3. Cache DB check ---")
cache_db = r"D:\AntiGravity_Products\StableDiffusion_Project\cache\safetensors-metadata\cache.db"
if os.path.exists(cache_db):
    try:
        conn = sqlite3.connect(cache_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"  Tables: {[t[0] for t in tables]}")
        
        for t in tables:
            tname = t[0]
            cursor.execute(f'SELECT COUNT(*) FROM "{tname}"')
            count = cursor.fetchone()[0]
            print(f"  Table '{tname}': {count} rows")
            
            cursor.execute(f'PRAGMA table_info("{tname}")')
            cols = [c[1] for c in cursor.fetchall()]
            print(f"  Columns: {cols}")
            
            cursor.execute(f'SELECT * FROM "{tname}" LIMIT 2')
            for row in cursor.fetchall():
                row_str = str(row)[:300]
                print(f"    {row_str}")
        conn.close()
    except Exception as e:
        print(f"  DB error: {e}")

# 4. Check hashes cache  
print("\n--- 4. Hashes cache ---")
for subdir in ["hashes", "hashes-addnet"]:
    hashes_dir = os.path.join(r"D:\AntiGravity_Products\StableDiffusion_Project\cache", subdir)
    if os.path.exists(hashes_dir):
        all_files = []
        for root, dirs, files in os.walk(hashes_dir):
            all_files.extend(files)
        print(f"  {subdir}: {len(all_files)} files")

# 5. Check for old E: drive paths
print("\n--- 5. Old path (E: drive) check ---")
found_old = False
if os.path.exists(cache_db):
    try:
        conn = sqlite3.connect(cache_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for t in tables:
            tname = t[0]
            cursor.execute(f'PRAGMA table_info("{tname}")')
            cols = [c[1] for c in cursor.fetchall()]
            for col in cols:
                try:
                    cursor.execute(f'SELECT "{col}" FROM "{tname}" WHERE CAST("{col}" AS TEXT) LIKE "%private%AntiGravity%"')
                    old_rows = cursor.fetchall()
                    if old_rows:
                        found_old = True
                        print(f"  WARNING: Old path found in table={tname}, column={col}")
                        for row in old_rows[:2]:
                            print(f"    {str(row)[:200]}")
                except:
                    pass
        conn.close()
    except Exception as e:
        print(f"  DB error: {e}")

if not found_old:
    print("  No old paths found")

# 6. Check config.json
print("\n--- 6. config.json relevant settings ---")
config_path = r"D:\AntiGravity_Products\StableDiffusion_Project\config.json"
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)
    
    relevant = ["samples_format", "extra_networks", "ch_civiai_api_key", "ch_max_size", "ch_skip_nsfw", "ckpt_dir", "lora_dir"]
    for key in sorted(config.keys()):
        for rk in relevant:
            if rk in key.lower():
                val = config[key]
                if isinstance(val, str) and len(val) > 50:
                    val = val[:50] + "..."
                print(f"  {key}: {val}")

# 7. Simulate the complete find_preview path for first model
print("\n--- 7. Complete find_preview simulation ---")
test_model = os.path.join(sd_dir, "animij_v8.safetensors")
if os.path.exists(test_model):
    path, ext = os.path.splitext(test_model)
    print(f"  Model: {test_model}")
    print(f"  Path (no ext): {path}")
    
    # What find_preview constructs
    preview_exts = ["png", "jpg", "jpeg", "webp", "gif"]
    potential_files = []
    for e in preview_exts:
        potential_files.append(f"{path}.{e}")
        potential_files.append(f"{path}.preview.{e}")
    
    print(f"  Potential files to check:")
    for f in potential_files:
        dirname, filename = os.path.split(f)
        exists_os = os.path.isfile(f)
        # scandir check
        try:
            entries = {e.name: e for e in os.scandir(dirname)}
            exists_scandir = filename in entries
        except:
            exists_scandir = False
        print(f"    {filename}: os.path.isfile={exists_os}, scandir={exists_scandir}")
        if exists_os:
            break

print("\n" + "=" * 60)
print("Debug complete")
