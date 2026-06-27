# allen-neuro-mcp

`allen-neuro-mcp` is an MCP-based computational neuroscience workflow server for working with Allen Institute Cell Types data.

Instead of acting as a thin wrapper around Allen API endpoints, this project exposes higher-level research workflows: discovering cells, inspecting metadata and electrophysiology features, downloading morphology reconstructions, computing morphology summaries, packaging modeling-ready bundles, and generating starter simulator projects.

The long-term goal is to help AI assistants and researchers move from biological data discovery toward reproducible computational modeling.

---

## Problem Statement

The Allen Cell Types Database provides rich biological data, including cell metadata, electrophysiology features, and morphology reconstructions. However, moving from that raw data to a modeling workflow often requires several manual steps:

1. Find suitable cells.
2. Inspect metadata and electrophysiology features.
3. Determine whether morphology reconstruction is available.
4. Download morphology files.
5. Parse and summarize reconstruction data.
6. Package metadata, ephys, and morphology into reproducible local artifacts.
7. Prepare simulator-specific starter projects.
8. Keep track of provenance and limitations.

For computational neuroscience and NeuroAI workflows, this gap matters. A researcher or AI assistant should not merely retrieve raw records. It should help organize biological evidence into reproducible modeling artifacts while preserving scientific honesty about what the model does and does not claim.

---

## Solution

`allen-neuro-mcp` provides a workflow-oriented MCP server over Allen Cell Types data.

The project is designed around scientific intent rather than endpoint mirroring.

A generic API wrapper looks like this:

```text
Allen API endpoint
    ↓
MCP tool
    ↓
raw response
```

`allen-neuro-mcp` is designed like this:

```text
research question
    ↓
workflow tool
    ↓
Allen data retrieval
    ↓
normalization + validation
    ↓
provenance + warnings
    ↓
modeling-ready artifact
```

Current capabilities include:

* Searching Allen Cell Types specimens.
* Retrieving normalized and raw cell metadata.
* Retrieving precomputed electrophysiology features.
* Downloading SWC morphology reconstructions.
* Parsing SWC morphology files.
* Computing morphology summaries.
* Creating local modeling bundles.
* Generating NEURON starter projects from morphology-aware bundles.
* Exposing these workflows through MCP tools.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/kireetijosyula41/allen-neuro-mcp.git
cd allen-neuro-mcp
```

### 2. Create and activate an environment

Using conda:

```bash
conda create -n allen-neuro-mcp python=3.11
conda activate allen-neuro-mcp
```

Or using `venv`:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install the package in editable mode

```bash
pip install -e .
```

If dependencies are not installed automatically, install:

```bash
pip install mcp pydantic allensdk
```

For generated NEURON projects, install NEURON in the generated project environment:

```bash
pip install neuron numpy matplotlib
```

---

## Running Tests

Run the full test suite:

```bash
pytest
```

Run selected tests:

```bash
pytest tests/test_swc.py
pytest tests/test_morphology_summary.py
pytest tests/test_neuron_project_builder.py
pytest tests/test_simulator_workflow_service.py
```

---

## Running the MCP Server

From the repo root:

```bash
python -m allen_neuro_mcp
```

The process may appear to hang. That is expected. The MCP server is waiting over stdio for an MCP client.

Example MCP client configuration:

```json
{
  "mcpServers": {
    "allen-neuro-mcp": {
      "command": "/path/to/python",
      "args": ["-m", "allen_neuro_mcp"],
      "cwd": "/path/to/allen-neuro-mcp"
    }
  }
}
```

For example, if using a conda environment:

```json
{
  "mcpServers": {
    "allen-neuro-mcp": {
      "command": "/opt/anaconda3/envs/allen-neuro-mcp/bin/python",
      "args": ["-m", "allen_neuro_mcp"],
      "cwd": "/Users/your-name/path/to/allen-neuro-mcp"
    }
  }
}
```

---

## Existing Functionality

### v0.1: Allen Cell Types metadata and electrophysiology workflow

v0.1 established the core project architecture.

It added:

* Pydantic schemas for public response contracts.
* A fake client for offline testing.
* An AllenSDK-backed client for real data access.
* A workflow service for Cell Types operations.
* MCP tools for core Cell Types workflows.
* Local modeling bundle generation.

Core MCP tools:

```text
search_cell_types
get_cell_metadata
get_cell_ephys_features
prepare_modeling_bundle
```

Example Python usage:

```python
from allen_neuro_mcp.clients.sdk import AllenSDKCellTypesClient
from allen_neuro_mcp.schemas import CellSearchFilters
from allen_neuro_mcp.services.cells import CellWorkflowService

client = AllenSDKCellTypesClient()
service = CellWorkflowService(client)

response = service.search(
    CellSearchFilters(
        species="mouse",
        structure="VISp",
        require_reconstruction=True,
        limit=3,
    )
)

print(response.model_dump())
```

Example search output includes normalized cell information such as:

```text
specimen_id
specimen_name
species
structure_acronym
structure_layer_name
dendrite_type
cre_line
has_reconstruction
```

---

## Extended Functionality

### v0.2: Morphology-aware modeling bundles

v0.2 extended the project from metadata/ephys access into morphology-aware data preparation.

It added:

* SWC morphology parser.
* Morphology summary computation.
* Reconstruction download support through AllenSDK.
* SHA256 checksums for generated artifacts.
* Morphology-aware modeling bundles.
* Warnings for reconstruction limitations.

A morphology-aware bundle contains:

```text
metadata.json
ephys_features.json
reconstruction.swc
morphology_summary.json
manifest.json
README.md
```

The morphology summary includes features such as:

```text
node_count
edge_count
soma_node_count
axon_node_count
basal_dendrite_node_count
apical_dendrite_node_count
unknown_node_count
total_cable_length_um
branch_point_count
terminal_tip_count
max_path_distance_um
bounding_box_um
warnings
```

Example Python usage:

```python
from allen_neuro_mcp.clients.sdk import AllenSDKCellTypesClient
from allen_neuro_mcp.services.cells import CellWorkflowService

service = CellWorkflowService(AllenSDKCellTypesClient())

bundle = service.prepare_bundle(
    specimen_id=485909730,
    include_morphology=True,
)

print(bundle.model_dump())
```

---

### v0.3: NEURON simulator scaffold generation

v0.3 extends the project from morphology-aware data packaging into simulation-preparation workflows.

It added:

* `SimulatorProject` schema.
* `SimulatorProjectBuilder` interface.
* `NEURONProjectBuilder`.
* `SimulatorWorkflowService`.
* MCP tool: `generate_simulator_project`.
* Real-data smoke test script.

The simulator workflow takes a specimen ID, creates a morphology-aware bundle, and then generates a local NEURON starter project.

```text
specimen_id
    ↓
metadata/ephys retrieval
    ↓
morphology reconstruction download
    ↓
morphology summary
    ↓
modeling bundle
    ↓
NEURON starter project
```

Generated project layout:

```text
.cache/allen-neuro-mcp/sim_projects/485909730/neuron/
  README.md
  requirements.txt
  run.py
  manifest.json
  metadata.json
  ephys_features.json
  morphology_summary.json
  reconstruction.swc
```

Example Python usage:

```python
from allen_neuro_mcp.clients.sdk import AllenSDKCellTypesClient
from allen_neuro_mcp.services.cells import CellWorkflowService
from allen_neuro_mcp.services.simulators import SimulatorWorkflowService

cell_service = CellWorkflowService(AllenSDKCellTypesClient())
simulator_service = SimulatorWorkflowService(cell_service)

project = simulator_service.generate_project(
    specimen_id=485909730,
    simulator="neuron",
)

print(project.model_dump())
```

Run the smoke script:

```bash
python scripts/smoke_generate_neuron_project.py
```

Compile-check the generated script:

```bash
python -m py_compile .cache/allen-neuro-mcp/sim_projects/485909730/neuron/run.py
```

Run the generated NEURON project:

```bash
cd .cache/allen-neuro-mcp/sim_projects/485909730/neuron
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Expected generated outputs:

```text
voltage_trace.csv
voltage_trace.png
```

Scientific limitation:

The generated NEURON project is a starter scaffold, not a fitted biophysical model. It packages real Allen metadata, ephys features, morphology summary, and SWC reconstruction, but the passive parameters are placeholders. The model has not yet been fit to Allen NWB sweeps or validated against recorded electrophysiology.

---

## MCP Tool Summary

Current tool surface:

```text
search_cell_types
get_cell_metadata
get_cell_ephys_features
download_cell_reconstruction
summarize_cell_morphology
prepare_modeling_bundle
generate_simulator_project
```

### `search_cell_types`

Search Allen Cell Types specimens by filters such as species, structure, dendrite type, and reconstruction availability.

### `get_cell_metadata`

Retrieve normalized and raw Allen metadata for a specimen.

### `get_cell_ephys_features`

Retrieve Allen precomputed electrophysiology features for a specimen.

### `download_cell_reconstruction`

Download an SWC reconstruction for a specimen with available morphology.

### `summarize_cell_morphology`

Parse the SWC reconstruction and compute morphology summary statistics.

### `prepare_modeling_bundle`

Create a local modeling bundle containing metadata, ephys features, provenance, and optionally morphology files.

### `generate_simulator_project`

Generate a local NEURON starter project from an Allen Cell Types specimen.

---

## Project Structure

```text
src/allen_neuro_mcp/
  __init__.py
  __main__.py
  cache.py
  errors.py
  schemas.py
  server.py

  clients/
    base.py
    sdk.py

  morphology/
    swc.py
    summary.py

  services/
    cells.py
    simulators.py

  simulators/
    base.py
    neuron.py

  tools/
    cells.py
    simulators.py

tests/
  fixtures/
  test_cache.py
  test_cells.py
  test_morphology_summary.py
  test_neuron_project_builder.py
  test_schemas.py
  test_simulator_base.py
  test_simulator_workflow_service.py
  test_swc.py

scripts/
  smoke_generate_neuron_project.py
```

---

## Changelog

### v0.3.0

Added simulator scaffold generation.

* Added `SimulatorProject` schema.
* Added simulator project-builder interface.
* Added `NEURONProjectBuilder`.
* Added `SimulatorWorkflowService`.
* Added MCP tool `generate_simulator_project`.
* Added real-data smoke test script for specimen `485909730`.
* Added generated NEURON starter project layout.

The generated NEURON project is a starter scaffold, not a fitted biophysical model.

### v0.2.0

Added morphology-aware modeling bundles.

* Added SWC parser.
* Added morphology summary computation.
* Added AllenSDK reconstruction download support.
* Added `download_cell_reconstruction`.
* Added `summarize_cell_morphology`.
* Added morphology-aware `prepare_modeling_bundle(include_morphology=True)`.
* Added checksums, manifests, warnings, and bundle README generation.

### v0.1.0

Added core Allen Cell Types workflow.

* Added cell search.
* Added metadata retrieval.
* Added electrophysiology feature retrieval.
* Added local modeling bundle generation.
* Added AllenSDK client.
* Added fake client and service tests.
* Added MCP server/tool registration.

---

## Design Principles

1. **Workflow-first, not endpoint-first**

   The project should expose scientific workflows, not merely raw API calls.

2. **Reproducibility**

   Generated artifacts should include manifests, provenance, checksums, and warnings.

3. **Scientific honesty**

   The system should clearly distinguish between raw data, derived summaries, starter scaffolds, fitted models, and validated models.

4. **Agent compatibility**

   Tools should be structured so an AI assistant can use them safely and predictably.

5. **Human inspectability**

   Generated projects should be readable, modifiable, and runnable by a human researcher.

---

## Current Status

Current milestone:

```text
v0.3 — NEURON simulator scaffold generation
```

The project currently supports the workflow:

```text
Allen Cell Types Database
    ↓
cell search
    ↓
metadata/ephys retrieval
    ↓
SWC morphology download
    ↓
morphology summary
    ↓
modeling bundle
    ↓
NEURON starter project
```

This makes `allen-neuro-mcp` a workflow-oriented bridge between biological cell data and computational neuroscience modeling preparation.
