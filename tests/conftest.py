import os

# Scripts run as subprocesses print estimator names such as "Ĉ". On Windows a
# captured stdout defaults to cp1252, which cannot encode them; UTF-8 mode fixes
# that, as it does for anyone who redirects a script's output there.
os.environ.setdefault("PYTHONUTF8", "1")
