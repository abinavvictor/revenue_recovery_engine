import pytest
from src.graph import create_graph

@pytest.fixture
def app():
    return create_graph()