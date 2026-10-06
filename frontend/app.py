from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from automation.audit_logger import AuditLogger
from automation.config_generator import generate_interface_config
from automation.drift_detector import build_expected_configuration
from automation.policy_engine import detect_conflicts
from automation.validator import validate_intent
from intent.intent_parser import load_intent


st.set_page_config(
    page_title="Intent Network Management",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------- Styling ----------
st.markdown(
    """
    <style>
    :root {
      --bg: #07111f;
      --panel: #0d1b2d;
      --panel2: #10233a;
      --line: #1e3550;
      --text: #edf5ff;
      --muted: #8da4bd;
      --accent: #43d9b2;
      --accent2: #4d8dff;
      --danger: #ff6b7a;
      --warning: #f6c85f;
    }
    .stApp { background: var(--bg); color: var(--text); }
    [data-testid="stHeader"] { background: rgba(7,17,31,0.95); }
    [data-testid="stSidebar"] { background: #091827; border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] * { color: #dce8f5; }
    .hero {
      padding: 24px 28px; border: 1px solid var(--line); border-radius: 18px;
      background: linear-gradient(135deg, #0d2035 0%, #0b1727 58%, #102a38 100%);
      margin-bottom: 18px;
    }
    .eyebrow { color: var(--accent); font-size: 12px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; }
    .hero h1 { margin: 6px 0 4px; font-size: 32px; letter-spacing: -1px; }
    .hero p { margin: 0; color: var(--muted); font-size: 14px; }
    .pill { display:inline-block; padding:5px 10px; border-radius:999px; font-size:12px; font-weight:700; margin-right:6px; }
    .pill-green { background:#10392f; color:#69e5c2; }
    .pill-blue { background:#102c54; color:#80adff; }
    .pill-gray { background:#172536; color:#9fb2c7; }
    .metric {
      background: var(--panel); border: 1px solid var(--line); border-radius: 14px;
      padding: 15px 17px; min-height: 105px;
    }
    .metric-label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .7px; }
    .metric-value { color: var(--text); font-size: 25px; font-weight: 800; margin-top: 7px; }
    .metric-sub { color: #7891aa; font-size: 11px; margin-top: 3px; }
    .section-title { margin: 22px 0 10px; font-size: 18px; font-weight: 800; }
    .role-card {
      background: var(--panel); border: 1px solid var(--line); border-radius: 14px;
      padding: 17px; height: 100%;
    }
    .role-name { font-weight: 800; font-size: 17px; text-transform: uppercase; }
    .role-priority { float:right; color: var(--accent); font-size:11px; text-transform:uppercase; }
    .policy-row { display:flex; justify-content:space-between; padding:7px 0; border-bottom:1px solid #152a40; color:#a9bad0; font-size:12px; }
    .policy-row:last-child { border-bottom:0; }
    .yes { color:#62dfbd; font-weight:700; }
    .no { color:#6e8197; font-weight:700; }
    .status-ok { color:#69e5c2; font-weight:800; }
    .status-bad { color:#ff7d89; font-weight:800; }
    .status-neutral { color:#f2c866; font-weight:800; }
    div[data-testid="stCodeBlock"] { border:1px solid var(--line); border-radius:12px; }
    .small-note { color: var(--muted); font-size: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=10)
def read_intent() -> dict:
    return load_intent(str(ROOT / "config" / "intent.yaml"))


def audit_files():
    directory = ROOT / "audit_logs"
    directory.mkdir(exist_ok=True)
    return sorted(directory.glob("audit_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def read_audit(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def metric_card(label, value, sub=""):
    st.markdown(
        f'<div class="metric"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def status_card(label, ok, detail):
    state = "PASS" if ok else "CHECK"
    css = "status-ok" if ok else "status-neutral"
    st.markdown(
        f'<div class="metric"><div class="metric-label">{label}</div>'
        f'<div class="metric-value {css}">{state}</div>'
        f'<div class="metric-sub">{detail}</div></div>',
        unsafe_allow_html=True,
    )


def run_precheck(intent):
    valid = validate_intent(intent)
    conflicts = detect_conflicts(intent)
    return valid, conflicts


def simulation_run(intent):
    valid, conflicts = run_precheck(intent)
    if not valid:
        return False, "Intent validation failed."
    if not conflicts:
        return False, "Policy conflicts were detected."

    native_config = generate_interface_config(intent)
    roles = list(intent["roles"].keys())
    logger = AuditLogger(str(ROOT / "audit_logs"))
    log_file = logger.log_event(
        intent_name=intent["intent"]["name"],
        campus_name=intent["campus"]["name"],
        execution_mode="simulation",
        result="SUCCESS",
        message=(
            "Role-based intent processed and configuration generated successfully. "
            "Live drift detection was not performed."
        ),
        roles=roles,
    )
    return True, str(log_file.relative_to(ROOT)), native_config


intent = read_intent()
valid, conflicts = run_precheck(intent)
native_config = generate_interface_config(intent)
expected = build_expected_configuration(intent)
roles = intent.get("roles", {})
interface = intent.get("policies", {}).get("interface", {})

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### ◈ INTENT NMS")
    st.caption("Campus LAN automation console")
    st.divider()
    page = st.radio(
        "NAVIGATION",
        ["Dashboard", "Intent", "Role Policies", "Configuration", "Execution", "Audit Logs", "Observability"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("**SYSTEM**")
    st.markdown('<span class="pill pill-green">● ONLINE</span>', unsafe_allow_html=True)
    st.caption("Simulation-ready")
    st.caption("Prometheus :8000")

# ---------- Hero ----------
st.markdown(
    f'''<div class="hero"><div class="eyebrow">Intent-Based Network Management</div>
    <h1>{intent["campus"]["name"]}</h1>
    <p>{intent["intent"]["description"]}</p>
    <div style="margin-top:14px"><span class="pill pill-blue">{intent["network"]["device_type"]}</span>
    <span class="pill pill-green">{intent["network"]["management_protocol"].upper()}</span>
    <span class="pill pill-gray">{intent["intent"]["name"]}</span></div></div>''',
    unsafe_allow_html=True,
)

# ---------- Dashboard ----------
if page == "Dashboard":
    st.markdown('<div class="section-title">Network workflow</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: status_card("Intent validation", valid, "YAML schema and required fields")
    with c2: status_card("Policy conflicts", conflicts, "Required campus roles")
    with c3: status_card("Config generation", True, "Cisco IOS-XE NETCONF XML")
    with c4: metric_card("Execution", "READY", "Simulation available")

    st.markdown('<div class="section-title">Campus policy snapshot</div>', unsafe_allow_html=True)
    cols = st.columns(len(roles))
    for col, (role, policy) in zip(cols, roles.items()):
        rows = "".join(
            f'<div class="policy-row"><span>{label}</span><span class="{"yes" if policy[key] else "no"}">{"ALLOWED" if policy[key] else "BLOCKED"}</span></div>'
            for key, label in [
                ("internet", "Internet"),
                ("academic_resources", "Academic resources"),
                ("internal_network", "Internal network"),
                ("student_network", "Student network"),
                ("teacher_network", "Teacher network"),
            ]
        )
        with col:
            st.markdown(
                f'<div class="role-card"><span class="role-name">{role}</span>'
                f'<span class="role-priority">{policy["priority"]}</span>{rows}</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-title">Current intent</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a: metric_card("Interface", interface.get("name", "—"), interface.get("description", ""))
    with b: metric_card("Roles", len(roles), "teachers / students / guests")
    with c: metric_card("Automation", "ENABLED", "validation • backup • verify • drift")

# ---------- Intent ----------
elif page == "Intent":
    st.markdown("## Intent definition")
    st.caption("Source: config/intent.yaml")
    st.code(yaml.safe_dump(intent, sort_keys=False), language="yaml")

    st.markdown("### Intent metadata")
    a, b, c = st.columns(3)
    with a: metric_card("Name", intent["intent"]["name"])
    with b: metric_card("Campus", intent["campus"]["name"])
    with c: metric_card("Protocol", intent["network"]["management_protocol"].upper())

# ---------- Roles ----------
elif page == "Role Policies":
    st.markdown("## Role-based access policies")
    st.caption("Policies are read directly from the current campus intent.")
    for role, policy in roles.items():
        with st.container(border=True):
            left, right = st.columns([1, 3])
            with left:
                st.subheader(role.title())
                st.caption(f"Priority: {policy['priority'].upper()}")
            with right:
                pcols = st.columns(5)
                for col, key, label in zip(
                    pcols,
                    ["internet", "academic_resources", "internal_network", "student_network", "teacher_network"],
                    ["Internet", "Academic", "Internal", "Student", "Teacher"],
                ):
                    with col:
                        st.metric(label, "ALLOW" if policy[key] else "BLOCK")

# ---------- Configuration ----------
elif page == "Configuration":
    st.markdown("## Generated configuration")
    st.caption("Generated by src/automation/config_generator.py")
    st.code(native_config, language="xml")

    a, b = st.columns(2)
    with a:
        st.markdown("### Expected state")
        st.json(expected)
    with b:
        st.markdown("### Interface intent")
        st.json(interface)

# ---------- Execution ----------
elif page == "Execution":
    st.markdown("## Execute intent workflow")
    st.warning("Live NETCONF deployment changes a real device. Use Simulation first and only enable live deployment when the Cisco device is reachable and authorized.")

    mode = st.radio("Execution mode", ["Simulation", "Live NETCONF"], horizontal=True)

    if mode == "Simulation":
        st.markdown("### Safe execution")
        st.write("Runs validation, conflict detection, configuration generation and audit logging without contacting Cisco IOS-XE.")
        if st.button("Run simulation", type="primary", use_container_width=True):
            with st.spinner("Processing intent..."):
                result = simulation_run(intent)
            if result[0]:
                st.success("Simulation completed successfully.")
                st.code(result[2], language="xml")
                st.info(f"Audit log created: {result[1]}")
                st.rerun()
            else:
                st.error(result[1])
    else:
        st.markdown("### Live NETCONF")
        st.error("The current repository's live deployment implementation prompts for the NETCONF password in the terminal and uses the configured Cisco endpoint. The web UI does not collect or store that password.")
        st.code("python main.py\n# Select 2: Live Cisco NETCONF Mode", language="bash")
        st.caption("This keeps the existing live deployment path unchanged and avoids putting device credentials into Streamlit session state.")

# ---------- Audit ----------
elif page == "Audit Logs":
    st.markdown("## Audit history")
    files = audit_files()
    if not files:
        st.info("No audit logs found yet.")
    else:
        for path in files:
            data = read_audit(path)
            if not data:
                continue
            result = data.get("result", "UNKNOWN")
            icon = "✅" if result == "SUCCESS" else "⚠️"
            with st.expander(f"{icon} {data.get('timestamp', '')} · {result} · {data.get('execution_mode', '')}"):
                st.json(data)

# ---------- Observability ----------
elif page == "Observability":
    st.markdown("## Observability")
    st.caption("Prometheus metrics are exposed by the existing server on port 8000 when main.py is running.")
    a, b = st.columns(2)
    with a:
        st.markdown("### Workflow components")
        st.markdown("- Intent validation\n- Configuration generation\n- NETCONF connection\n- Configuration deployment\n- Configuration verification\n- Drift detection")
    with b:
        st.markdown("### Metrics endpoint")
        st.code("http://localhost:8000/metrics", language="text")
        st.link_button("Open Prometheus metrics", "http://localhost:8000/metrics", use_container_width=True)

st.divider()
st.caption(f"Intent Network Management Console · Last loaded {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
