from allen_neuro_mcp.server import create_server

def test_create_server() -> None:
    server = create_server()
    assert server is not None