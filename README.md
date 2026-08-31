# NetSage AI: Automated Network Diagnostic Platform
Team members details
Team member 1:
Name : Ashutosh Chaurasia
Roll No : 0176Al231033
Email id: ashutoshc9211@gmail.com
Team member 2:
Name : Divyanshi Rajput
Roll No: 0176AL231046
Email id : divyanshirajput70@gmail.com
Team member 3:
Name : Bhumika Gahwade
Roll no : 0176AL231042
Email id : bhumikag131204@gmail.com
# Comprehensive System Documentation
# 1. Executive Summary & Problem Statement
1.1 Problem Statement
In modern network management and educational lab environments (such as Cisco Packet Tracer), diagnosing multi-layer network failures requires extensive manual CLI execution (show commands), expert knowledge across OSI layers, and careful verification before executing remediation steps.
Key challenges include:
•	Time-Consuming Troubleshooting: Junior engineers spend considerable time analyzing verbose CLI outputs to locate misconfigurations (e.g., sub-interface shutdown, incorrect wildcard masks, missing ACL entries).
•	Risk of Destructive Remediation: Direct execution of AI-generated configuration commands in network environments introduces catastrophic risks if the model hallucinates or provides incorrect CLI parameters.
•	Lack of Structured Rules: Pure LLM solutions lack deterministic guarantees, whereas traditional rule engines lack semantic reasoning capabilities to interpret complex topologies.
1.2 System Objective
NetSage AI bridges this gap by combining deterministic rule-based validation with structured prompt engineering and a mandatory Human-in-the-Loop (HITL) verification gate. The system reads symptoms and show-command outputs, suggests likely causes and next steps, and always requires a human to review before accepting the fix.

# 2. Proposed Solution
NetSage AI provides an end-to-end automated network diagnostic workspace:
1.	Hybrid Diagnostics: Combines static pattern matching (checker.py / ai_engine.py) for known status errors with LLM prompt templates (diagnose_prompt.md) to extract root causes and evidence.
2.	Structured JSON Output: Standardizes diagnostic results into strict fields: root_cause, osi_layer, concept_tag, confidence, evidence, next_command, and fix_steps.
3.	Human Oversight Gate: Provides an interactive operations dashboard where network engineers can inspect diagnoses, review evidence, edit proposed CLI commands, and approve or reject remediation before deployment.
4.	Auditability: Logs agreement rates, false positives, and engineer overrides into a central model audit log (review_log.csv) to fulfill Responsible AI requirements.

# 3. Solution Architecture
NetSage AI follows a modular 4-tier architecture:
Tier	Component	Description
DATA TIER	data/cases.csv	Dataset containing 30 structured multi-layer Cisco Packet Tracer scenarios (VLAN, Gateway, DHCP, DNS, Routing, ACL, NAT, Wireless) with attributes: Case_ID, Symptom, Topology_Note, Show_Commands_Output, Expected_Fault, OSI_Layer, Concept_Tag, Severity.
DIAGNOSTIC CORE	engine.py / ai_engine.py	System prompt orchestration & JSON output parser. Sends data to LLM (or Mock AI fallback) and parses the response.
	checker.py (Rule Checker)	Deterministic engine containing regular expressions and rule checks (e.g., detecting admin down, no ip helper-address, no ip nat outside).
	prompts/diagnose
_prompt.md	System prompt enforcing OSI layer identification, evidence extraction, few-shot examples, and strict JSON output schema.
HITL GATE	app.py / index.html + style.css	Interactive Dashboard providing case selection, real-time diagnostic visualizers, and human deployment approval controls (Accept / Edit / Reject).
AUDIT & LOGGING	data/review_log.csv	Documentation tracking agreement metrics, overrides, and edge cases requiring human correction (Responsible AI log).






# 4. Detailed Design & Module Descriptions
File / Component	Responsibility
data/cases.csv	Dataset containing 30 structured test cases covering multiple network fault types.
prompts/diagnose_prompt.md	System prompt enforcing OSI layer identification, evidence extraction, 3 worked examples (few-shot), and strict JSON output schema.
src/checker.py (or rule_checker function)	Deterministic engine containing regular expressions and rule checks executed before AI inference to catch basic config errors.
src/engine.py (or ai_engine.py)	Orchestrator module combining deterministic checks, prompt generation, LLM API calls, and response formatting.
src/app.py (or main.py + frontend)	Interactive dashboard providing case selection, real-time diagnostic visualizers, and human deployment approval controls.
data/review_log.csv	Audit log tracking AI vs. Human agreement metrics, false positives, and documented corrections.

# 5. System Workflow & Flowchart
Below is the end-to-end workflow from case selection to human approval and audit logging:
 

# 6. Primary Use Case
Use Case UC-01: Inter-VLAN Routing Diagnosis and Verification
•	Primary Actor: Network Engineer / Student Lab Operator
•	Pre-conditions: cases.csv loaded into the NetSage AI dashboard; Packet Tracer scenario context available.
Main Success Scenario:
1.	The operator selects scenario CASE_022 ("VLAN 10 cannot talk to VLAN 20").
2.	NetSage AI parses the captured Show_Commands_Output: show ip int brief: Vlan20 admin down
3.	The deterministic rule_checker flags status: "Deterministic Alert: Interface is administratively or physically down."
4.	The AI Engine presents the exact JSON fix steps:
json
{
  "root_cause": "Switch Virtual Interface (SVI) for VLAN 20 is shut down",
  "confidence": "high",
  "fix_steps": [
    "configure terminal",
    "interface vlan 20",
    "no shutdown",
    "end"
  ]
}
5.	The operator reviews the evidence, selects "Accept" (or "Edit" if modification is needed), and submits the decision.
6.	Post-conditions: The audit record is saved to review_log.csv and the fix is approved for lab deployment.

# 7. Responsible AI & Model Auditability
To satisfy the "Human Review" safety rule, NetSage AI strictly enforces a Human-in-the-Loop (HITL) policy. The system includes a built-in Responsible AI Log (review_log.csv).
During testing, the AI model intentionally failed on 5 complex cases (e.g., hidden ACLs blocking NAT, passive interfaces blocking OSPF). The human operator stepped in, rejected the initial AI diagnosis, provided the corrected fault, and logged the reasoning.
Example Audit Log Entry:
•	Case ID: CASE_024 (Static NAT for web server not working)
•	AI Diagnosis: "Static NAT IP mapping is incorrect"
•	Action Taken: Edited
•	Corrected Fault: "NAT translation fails because underlying ACL denies the inside IP"
•	Reason: "AI missed the hidden ACL denying the inside IP. Human corrected."

# 8. Tech Stack Used
Category	Technology / Tool	Purpose
Language	Python 3.10+	Core development environment for backend logic, data processing, and AI integration.
User Interface	FastAPI / Streamlit / HTML+JS	Building the interactive Operations Dashboard for case selection and human review.
Data Processing	Pandas / CSV Module	Loading, querying, and displaying structured CSV case data.
Path Handling	pathlib	Dynamic, platform-agnostic file path resolution.
Data Interchange	JSON	Structured prompt inputs and diagnostic outputs.
AI Integration	OpenAI API (Mock fallback available)	LLM inference for semantic reasoning and root cause analysis.
Documentation	Markdown & Mermaid.js	System architectural design, flowcharts, and audit logs.
Target System	Cisco IOS CLI / Packet Tracer	Target environment for network diagnostics.

