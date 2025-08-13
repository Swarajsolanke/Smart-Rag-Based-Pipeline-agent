# tests/test_end_to_end.py
"""
A simple smoke test to ensure imports don't crash.
"""
def test_imports():
    import src.app
    import src.agents.decision_agent
    import src.pipelines.embedding_pipeline
    assert True
