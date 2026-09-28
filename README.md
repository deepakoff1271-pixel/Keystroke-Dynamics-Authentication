<div align="center">

# ⌨️ Keystroke Dynamics Authentication

**Behavioral biometric authentication — verify a user by *how* they type, not just *what* they type.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](#license)
[![Status](https://img.shields.io/badge/Status-Complete-brightgreen.svg)](#)

</div>

---

## 📖 Overview

Traditional passwords can be stolen, shared, or brute-forced. This project adds a
**software-only behavioral biometric layer** on top of a fixed-text password by
analyzing the user's typing rhythm — press-to-press delays, release-to-press
intervals, and hold times.

A Flask web application handles live data capture, feature extraction, and an
interactive analysis dashboard covering **variance analysis**, **Pearson
correlation**, **KNN classification**, **correlation-based KDA**, and **t-SNE
visualization**.

---

## ✨ Features

| | |
|---|---|
| 🎯 | **Live browser keystroke capture** with millisecond precision |
| 🧪 | **Automatic synthetic dataset generation** (5 defence + 33 attack profiles per password) |
| 📊 | **Variance analysis** for typing consistency |
| 🔗 | **Pearson correlation matrix** for pairwise similarity |
| 🤖 | **KNN classification** (k=3, Manhattan distance) with TAR / FRR / TRR / FAR |
| 🔐 | **Correlation-based KDA** with threshold sweep and EER estimation |
| 🗺️ | **t-SNE** for 2D cluster visualization |
| 🖥️ | **Interactive Flask dashboard** with Chart.js charts |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, Flask 3.0
- **Data / ML:** NumPy, pandas, scikit-learn
- **Visualization:** Chart.js (frontend), matplotlib & seaborn (offline plots)
- **Frontend:** Jinja2 templates, vanilla JavaScript, custom CSS

---

## 📁 Project Structure
