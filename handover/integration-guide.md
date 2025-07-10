# Integration Guide: WP 3.1 + WP 3.2

## Objective
To document how WP 3.2 orchestrator executes and manages the WP 3.1 data pipeline end-to-end.

---

## Project Setup

### Repo Layout
- `AIEffect-3.1-to-3.2/`: Contains the 3 microservices: `energy-generator`, `energy-analyzer`, and `report-generator`.
- `AI-Effect-W3.2/`: Contains the orchestrator code and `config/energy-pipeline.json`.

### Required Docker Images
- `aieffect-31-to-32-energy-generator`
- `aieffect-31-to-32-energy-analyzer`
- `aieffect-31-to-32-report-generator`

---

## Build Instructions (from root of `AIEffect-3.1-to-3.2/`)
```bash
docker-compose -f docker-compose.yaml build
```

---

## Test the Services Manually (Optional)

```bash
docker run --rm -v "$PWD/data:/data" aieffect-31-to-32-energy-generator
docker run --rm -v "$PWD/data:/data" aieffect-31-to-32-energy-analyzer
docker run --rm -v "$PWD/data:/data" aieffect-31-to-32-report-generator
```

Expected: All containers run successfully and files are created in `/data`.

---

## Orchestration Execution (From WP 3.2)

### Step 1: Confirm the volumes are mounted in `docker-compose.yml`:
Located at: `AI-Effect-W3.2/docker/docker-compose.yml`
```yaml
volumes:
  - ../data:/data
```

### Step 2: Update the config path in `energy-pipeline.json`
Located at: `AI-Effect-W3.2/config/energy-pipeline.json`
```json
"command": "docker run -v /home/work/project/AIEffect-3.1-to-3.2/data:/data aieffect-31-to-32-energy-generator"
```
Do this for all three containers.

### Step 3: Run the orchestrator
From:
```bash
cd AI-Effect-W3.2/docker
docker-compose run --rm orchestrator python main.py
```

Expected Output:
- Container 1: `energy_data.csv` created
- Container 2: `output1.json` → `output2.json`
- Container 3: `energy_report.csv` created

---

## Troubleshooting Done

- FileNotFound errors resolved by using absolute volume mount paths.
- Adjusted orchestrator subprocess to inject correct paths dynamically.
- Fixed Dockerfile `COPY` errors by setting correct context and file locations.
- Validated output manually using:
```bash
cat data/output1.json
cat data/energy_report.csv
```

---

## Integration Success Criteria

- Orchestrator triggers WP 3.1 containers using subprocess
- Intermediate outputs handled via `/data/` volume
- Final report generated and validated
- Ready for WP 3.2 handover and mentor review
