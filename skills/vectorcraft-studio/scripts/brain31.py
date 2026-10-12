"""Portable entry point; legacy brain.py contract remains unchanged."""
from pathlib import Path
import os,sys
import brain
if __name__=='__main__':
    if not any(a=='--vault' or a.startswith('--vault=') for a in sys.argv[1:]):
        sys.argv[1:1]=['--vault',os.environ.get('VECTORCRAFT_BRAIN',str(Path.home()/'Documents/Design Brain'))]
    brain.main()
