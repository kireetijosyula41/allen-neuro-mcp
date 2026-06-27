from pathlib import Path

from allen_neuro_mcp.clients.sdk import AllenSDKCellTypesClient
from allen_neuro_mcp.services.cells import CellWorkflowService
from allen_neuro_mcp.services.simulators import SimulatorWorkflowService


def main() -> None:
    specimen_id = 485909730

    cell_service = CellWorkflowService(AllenSDKCellTypesClient())
    simulator_service = SimulatorWorkflowService(cell_service)

    project = simulator_service.generate_project(
        specimen_id=specimen_id,
        simulator="neuron",
    )

    project_dir = Path(project.project_directory)

    print("Generated NEURON project")
    print("=" * 48)
    print(f"Specimen ID: {project.specimen_id}")
    print(f"Simulator: {project.simulator}")
    print(f"Project directory: {project_dir}")
    print(f"Entrypoint: {project.entrypoint}")
    print()
    print("Files:")
    for file_name in project.files:
        path = project_dir / file_name
        status = "exists" if path.exists() else "missing"
        print(f"  - {file_name}: {status}")

    print()
    print("Warnings:")
    for warning in project.warnings:
        print(f"  - {warning}")

    print()
    print("Run instructions:")
    for instruction in project.run_instructions:
        print(f"  - {instruction}")


if __name__ == "__main__":
    main()