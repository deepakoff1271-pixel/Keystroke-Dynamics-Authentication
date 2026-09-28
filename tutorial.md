# Keystroke Dynamics Authentication Project Tutorial

This folder contains the finished version of the keystroke dynamics authentication project.

## What is included
- Flask web app for home, collection, and dashboard views
- Synthetic keystroke dataset generation
- Feature extraction for Press-to-Press, Release-to-Press, and Hold Time
- Variance, correlation, KNN, correlation-based KDA, and t-SNE analysis
- Final review presentation source and exported slide deck

## Prerequisites
- Python 3.10 or later
- pip

## Install dependencies
Open a terminal in this folder and run:

```bash
pip install -r requirements.txt
```

## Run the app
Start the Flask server with:

```bash
python app.py
```

Then open:
- Home: http://127.0.0.1:5000/
- Data collection: http://127.0.0.1:5000/collect
- Analysis dashboard: http://127.0.0.1:5000/dashboard

## How the collection page works
1. Choose a password.
2. Select Defence or Attack mode.
3. Enter a participant ID.
4. Click Start capture.
5. Type the displayed password and press Enter.
6. The app stores the timing vector in the local `data/` folder.

## How the dashboard works
- Use the password selector to switch the analysis target.
- The Variance tab shows typing consistency.
- The Correlation tab shows pairwise Pearson similarity.
- The KNN tab shows TAR, FRR, TRR, and FAR.
- The Correlation KDA tab shows threshold-based authentication scores.
- The t-SNE tab visualizes the typing clusters in 2D.

## Project structure
- `app.py` - Flask routes and API endpoints
- `data_processor.py` - synthetic data generation and feature extraction
- `analyzer.py` - analysis algorithms
- `templates/` - HTML pages
- `static/` - CSS and JavaScript assets
- `data/` - generated CSV files
- `final_review_presentation.md` - slide source for the final review deck
- `Final_Review_Presentation.pptx` - exported presentation

## Notes
- The app auto-generates baseline synthetic data if the data folder is empty.
- If you collect your own samples, they are saved as CSV files alongside the generated dataset.
