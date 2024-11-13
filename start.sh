#!/bin/bash
Xvfb :99 -screen 0 1920x1080x16 &
sleep 1
streamlit run main.py --server.address=0.0.0.0 --server.port=8501