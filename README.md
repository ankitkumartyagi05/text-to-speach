# Text To Speech App

## Install
pip install -r requirements.txt

## Run
python app.py

## Backend setup
- Local Flask development serves the API and frontend from `app.py`.
- Deployed builds use `api/index.py` as the Vercel Python entrypoint.
- The browser client calls `/session-status` and `/generate-audio` on the current origin.
