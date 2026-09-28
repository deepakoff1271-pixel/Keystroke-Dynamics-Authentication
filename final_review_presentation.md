---
marp: true
theme: default
paginate: true
style: |
  section {
    font-family: "Trebuchet MS", "Segoe UI", sans-serif;
    background: linear-gradient(180deg, #07111f 0%, #050c18 100%);
    color: #ecf3ff;
  }
  h1, h2 {
    color: #f4b35d;
  }
  strong {
    color: #39d0c5;
  }
---

# Keystroke Dynamics Authentication
## Final Review Presentation

Finished Flask-based behavioral authentication project with live collection, processing, and analysis.

---

# Problem Statement

Traditional passwords are easy to steal, share, or brute-force.

This project adds a software-only behavioral biometric layer that checks **how** a password is typed, not just whether it is correct.

---

# Completed System

- Web-based keystroke data collection in the browser
- Fixed-text feature extraction for **PP**, **RP**, and **HT**
- Synthetic dataset generation for defence and attack profiles
- Statistical and ML analysis through the dashboard
- Presentation-ready deliverables in one folder

---

# Core Algorithms

- **Variance analysis** for typing consistency
- **Pearson correlation** for similarity comparison
- **KNN classification** with Manhattan distance
- **Correlation-based KDA** with threshold sweep and EER estimation
- **t-SNE** for cluster visualization

---

# Application Workflow

1. Open the Flask app
2. Choose a password on the collection page
3. Type the password naturally and press Enter
4. Save the keystroke timing vector
5. Open the dashboard and inspect the models

---

# Dashboard Output

The dashboard now shows:

- Variance tables and bar charts
- Correlation matrices
- KNN error rates and acceptance metrics
- Correlation-KDA summary values
- t-SNE scatter plots of user clusters

---

# Deliverables

- Completed app source in a dedicated project folder
- Updated tutorial for setup and usage
- Final review deck in slide format
- Local CSV data generation and collection flow

---

# Conclusion

The project is now packaged as a working end-to-end demo for keystroke dynamics authentication.

It demonstrates data capture, feature extraction, statistical analysis, and machine learning evaluation in a single application.
