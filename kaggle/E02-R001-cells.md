# E02-R001 Kaggle cells (copy-paste)

Runbook row 1 (`docs/KAGGLE-RUNBOOK.md`): download, checksum and inventory the
SynthSAEBench-16k world and SAE zoo. Pre-freeze OK: it reads file layouts and
shapes only and computes no outcome.

Settings: Accelerator **None** (CPU is enough; this saves GPU quota), Internet
**on**. Secret **HF_TOKEN** is optional (the repos are public; a token only
helps with rate limits). Run with **Save Version -> Save & Run All (Commit)**,
because an interactive session's `/kaggle/working` is deleted when it ends.
Expect well under an hour, most of it the zoo download (cell 3 prints the size
first).

Paste each block into its own code cell, in order. Cell 3 always saves the
repo file lists and checksums, so if cell 4 fails on an unexpected layout the
output still has what is needed to fix the loader.

```python
# 1. Hugging Face token (optional)
import os
try:
    from kaggle_secrets import UserSecretsClient
    os.environ["HF_TOKEN"] = UserSecretsClient().get_secret("HF_TOKEN")
    print("HF_TOKEN set")
except Exception as e:
    print("no HF_TOKEN, continuing anonymously:", type(e).__name__)
```

```python
# 2. Code and install (about 1 min)
!git clone -q https://github.com/santoshcheethiralame-dot/MissingMass /kaggle/working/MissingMass
%cd /kaggle/working/MissingMass
!git log --oneline -1
!pip install -q -e . safetensors huggingface_hub
import time, json, sys
T0 = time.time()
sys.path.insert(0, "src")
from crsafety import manifest
M = manifest.start("E02-R001", "E02",
                   "python analysis/e02/zoo.py inventory --out /kaggle/working/E02-R001 --world <local> --zoo <local>",
                   config=dict(world_repo="decoderesearch/synth-sae-bench-16k-v1",
                               zoo_repo="decoderesearch/synth-sae-bench-16k-v1-saes"),
                   seeds={}, packages=("numpy", "scipy", "crsafety", "safetensors", "huggingface_hub"))
print("manifest started, git", M["git_sha"], "dirty", M["git_dirty"])
```

```python
# 3. List, download and checksum both repos (the zoo is the long part)
from pathlib import Path
from huggingface_hub import HfApi, snapshot_download
from crsafety.manifest import sha256_file
api, OUT = HfApi(), Path("/kaggle/working/E02-R001"); OUT.mkdir(parents=True, exist_ok=True)
repos, local = {}, {}
for name, rid in [("world", "decoderesearch/synth-sae-bench-16k-v1"),
                  ("zoo", "decoderesearch/synth-sae-bench-16k-v1-saes")]:
    for rtype in ("model", "dataset"):
        try:
            info = api.repo_info(rid, repo_type=rtype, files_metadata=True); break
        except Exception as e:
            err = e
    else:
        raise SystemExit(f"{rid}: not found as model or dataset: {err}")
    files = {s.rfilename: s.size for s in info.siblings}
    print(f"{name}: {rid} ({rtype}) revision {info.sha}, {len(files)} files, {sum(v or 0 for v in files.values())/1e9:.2f} GB")
    t = time.time()
    local[name] = Path(snapshot_download(rid, repo_type=rtype, revision=info.sha))
    print(f"  downloaded in {(time.time()-t)/60:.1f} min -> {local[name]}")
    sums = {f: sha256_file(local[name] / f) for f in sorted(files) if (local[name] / f).is_file()}
    repos[name] = dict(repo=rid, repo_type=rtype, revision=info.sha, n_files=len(files),
                       bytes=sum(v or 0 for v in files.values()), sizes=files, sha256=sums)
(OUT / "repos.json").write_text(json.dumps(repos, indent=2) + "\n")
WORLD, ZOO = str(local["world"]), str(local["zoo"])
print("first zoo files:", sorted(repos["zoo"]["sizes"])[:12])
```

```python
# 4. E02-R001 inventory (runbook command, on the downloaded copies)
!python analysis/e02/zoo.py inventory --out /kaggle/working/E02-R001 --world {WORLD} --zoo {ZOO}
```

```python
# 5. Close the manifest and pack for download (Output panel -> E02-R001.zip)
import shutil
inv_ok = (OUT / "inventory.json").exists()
inv = json.loads((OUT / "inventory.json").read_text()) if inv_ok else {}
M["model_ids"] = [f'{r["repo"]}@{r["revision"]}' for r in repos.values()]
M["cost"]["gpu_hours"] = 0.0
manifest.finish(M, outputs=["inventory.json", "repos.json"], status="succeeded" if inv_ok else "failed",
                session_hours=round((time.time() - T0) / 3600, 3))
shutil.copy(manifest.path_for("E02-R001"), OUT / "manifest.json")
!cd /kaggle/working && zip -qr E02-R001.zip E02-R001 && ls -la E02-R001.zip
print(json.dumps({k: inv.get(k) for k in ("n_features", "d", "archs", "l0", "seeds", "n_saes", "widths",
                                          "missing", "cells", "expected")}, indent=1))
```

Afterwards: download `E02-R001.zip` from the version's Output tab and upload it
in the project thread; it is unzipped into `results/E02/E02-R001/` and the run
is closed with `tools/notebook.py set E02-R001 status=succeeded summary="..."`
(or `failed`, with what broke). The check is the printout of cell 5: 5 archs,
7 L0 values (15–45), 5 seeds, 175 SAEs, width 4096, nothing missing, 16,384
features in d = 768.
