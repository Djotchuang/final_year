from flask import render_template
from app import home

def test_index():
    assert home() == render_template('index.html')