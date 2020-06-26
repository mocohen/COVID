#!/bin/bash

curl -o states-daily.csv 'https://covidtracking.com/api/v1/states/daily.csv'
/Users/bethanys08/.pyenv/shims/jupyter nbconvert --to python Covid\ Metrics.ipynb
/Users/bethanys08/.pyenv/shims/python Covid\ Metrics.py

git add images/*
git commit -m "updated graphs"
git push
