from mcp.server.fastmcp import FastMCP

from allen_neuro_mcp.clients.sdk import AllenSDKCellTypesClient
from allen_neuro_mcp.services.cells import CellWorkflowService
from allen_neuro_mcp.services.simulators import SimulatorWorkflowService
from allen_neuro_mcp.tools.cells import register_cell_tools
from allen_neuro_mcp.tools.simulators import register_simulator_tools


def create_server(service: CellWorkflowService | None = None) -> FastMCP:
    mcp = FastMCP(
        "Allen Neuro MCP",
        instructions=(
            "Use these tools for bounded Allen Cell Types discovery, "
            "morphology inspection, and computational neuroscience modeling preparation."
        ),
    )

    if service is None:
        client = AllenSDKCellTypesClient()
        service = CellWorkflowService(client)

    simulator_service = SimulatorWorkflowService(service)

    register_cell_tools(mcp, service)
    register_simulator_tools(mcp, simulator_service)
    
    return mcp


def main() -> None:
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()