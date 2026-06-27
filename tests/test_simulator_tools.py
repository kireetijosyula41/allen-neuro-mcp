from mcp.server.fastmcp import FastMCP

from allen_neuro_mcp.cache import FileCache
from allen_neuro_mcp.services.cells import CellWorkflowService
from allen_neuro_mcp.services.simulators import SimulatorWorkflowService
from allen_neuro_mcp.tools.simulators import register_simulator_tools


def test_register_simulator_tools(fake_client, tmp_path) -> None:
    mcp = FastMCP("test-server")

    cache = FileCache(tmp_path)
    cell_service = CellWorkflowService(fake_client, cache=cache)
    simulator_service = SimulatorWorkflowService(cell_service, cache=cache)

    register_simulator_tools(mcp, simulator_service)

    assert mcp is not None