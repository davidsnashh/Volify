import sys
import os
import requests
from src.polygon_api import PolygonOptionsAPI

def test_api_initialization():
    """Test that the API can be initialized"""
    api = PolygonOptionsAPI()
    assert api is not None

def test_get_options_chain():
    """Test fetching options chain"""
    api = PolygonOptionsAPI()
    spy_options = api.get_options_chain("SPY")
    
    # Basic validation of the response
    assert isinstance(spy_options, list)
    if spy_options:  # if we got data
        first_contract = spy_options[0]
        assert "ticker" in first_contract
        assert "strike" in first_contract
        assert "expiry" in first_contract