import runpy
from pathlib import Path

# ASCII filename alias so Streamlit Cloud reliably shows this page in the sidebar.
# The actual page content is maintained in the Korean-titled page file.
page_path = Path(__file__).with_name("01_하나님의_마음_창45.py")
runpy.run_path(str(page_path), run_name="__main__")
