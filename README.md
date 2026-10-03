# Intent-Based Network Management and Automated Configuration System for Campus LANs

## 1. Project Overview

The **Intent-Based Network Management and Automated Configuration System for Campus LANs** is a Python-based network automation project that converts high-level network intent into Cisco IOS-XE configuration using YANG-modeled NETCONF.

The system is designed for a campus network environment with different user roles such as **teachers, students, and guests**.

Instead of manually configuring network devices, an administrator defines the desired network behavior in a YAML intent file. The system then validates the intent, processes role-based policies, detects policy conflicts, generates configuration, deploys the configuration through NETCONF, verifies the result, detects configuration drift, creates audit logs, and exposes operational metrics through Prometheus.

---

## 2. Problem Statement

Traditional campus network management often depends on manually configuring network devices.

Manual configuration can result in:

- Configuration errors
- Inconsistent device configurations
- Repetitive administrative work
- Configuration drift
- Difficulty tracking network changes
- Increased operational effort

This project provides an automated, intent-driven workflow where the administrator specifies **what the network should achieve**, while the system handles the configuration workflow.

---

## 3. Objectives

The main objectives of the project are:

1. Accept high-level network intent.
2. Represent network requirements using YAML.
3. Parse and validate the intent.
4. Define role-based campus network policies.
5. Detect policy conflicts.
6. Automatically generate Cisco IOS-XE configuration.
7. Use YANG-modeled NETCONF for device communication.
8. Apply configuration automatically.
9. Verify configuration after deployment.
10. Detect configuration drift.
11. Create configuration backups.
12. Maintain audit logs.
13. Provide Prometheus-based observability.
14. Support both simulation and live Cisco NETCONF execution.
15. Provide a controlled and traceable network automation workflow.

---

## 4. System Architecture

```text
                Campus Administrator
                         |
                         v
                High-Level Intent
                    YAML File
                         |
                         v
                  Intent Parser
                         |
                         v
                 Intent Validator
                         |
                         v
                   Policy Engine
                         |
                         v
                Conflict Detection
                         |
                         v
            Configuration Generation
                         |
                         v
                  YANG / NETCONF
                         |
                         v
                  Cisco IOS-XE
                         |
              +----------+----------+
              |                     |
              v                     v
       Configuration            Verification
          Backup                     |
                                     v
                              Drift Detection
                                     |
                         +-----------+-----------+
                         |                       |
                         v                       v
                    Audit Logs              Prometheus
                                                 |
                                                 v
                                           Observability
