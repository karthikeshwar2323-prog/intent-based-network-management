# Intent Network Management Frontend

A Streamlit dashboard for the existing Intent-Based Network Management project.

## Run from the project root

```bash
source .venv/bin/activate
pip install -r frontend/requirements.txt
export PYTHONPATH="$PWD/src:$PYTHONPATH"
streamlit run frontend/app.py
```

The UI reads `config/intent.yaml` and uses the existing parser, validator, policy engine, configuration generator and audit logger.

### Pages

- Dashboard — workflow status and campus policy snapshot
- Intent — YAML intent viewer
- Role Policies — teachers, students and guests
- Configuration — generated Cisco IOS-XE NETCONF XML
- Execution — safe Simulation mode and guarded Live NETCONF guidance
- Audit Logs — previous JSON execution logs
- Observability — Prometheus endpoint information

Live deployment remains on the existing `main.py` path because the current implementation asks for the NETCONF password in the terminal. The frontend deliberately does not store that password.
