import os
import sys

# Batasi thread sebelum numpy/joblib diimport untuk mencegah crash RLIMIT_NPROC di cPanel
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app as application
