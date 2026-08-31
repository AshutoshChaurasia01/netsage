import os
import json
import csv
from pathlib import Path
DATA_DIR = Path(__file__).parent.parent / "data"
CASES_FILE = DATA_DIR / "cases.csv"
LOG_FILE = DATA_DIR / "review_log.csv"

def rule_checker(show_output: str) -> list:
    findings = []
    output_lower = show_output.lower()
    
    if "admin down" in output_lower or "status down" in output_lower:
        findings.append("Deterministic Alert: Interface is administratively or physically down.")
    if "not found in local vlan database" in output_lower:
        findings.append("Deterministic Alert: Missing VLAN in database.")
    if "no ip helper-address" in output_lower:
        findings.append("Deterministic Alert: Missing IP helper-address for DHCP.")
    if "no ip nat outside" in output_lower:
        findings.append("Deterministic Alert: NAT outside interface missing config.")
    if "0.0.0.0" in output_lower and "gateway" in output_lower:
        findings.append("Deterministic Alert: Default gateway missing on host.")
    if "no ip routing" in output_lower:
        findings.append("Deterministic Alert: IP routing is disabled on L3 device.")
        
    return findings if findings else ["No deterministic rules matched. Relying on AI."]

DIAGNOSE_PROMPT = """
You are NetSage AI, an expert Cisco network troubleshooting assistant. 
Analyze the following network issue and respond ONLY with a valid JSON object.

JSON Output Schema:
{{
  "root_cause": "string",
  "osi_layer": "integer",
  "concept_tag": "string",
  "confidence": "string (low, medium, high)",
  "evidence": "string quoting show command output",
  "next_command": "string",
  "fix_steps": "array of strings"
}}

User Input:
Symptom: {symptom}
Topology: {topology}
Show_Commands_Output: {show_output}

AI Response:
"""

def mock_ai_diagnosis(case: dict) -> dict:
    """Simulates AI response for environments without an OpenAI API key."""
    show_output = case.get('Show_Commands_Output', '')
    if case['Case_ID'] == 'CASE_024':
        return {"root_cause": "Static NAT IP mapping is incorrect", "confidence": "high"}
    elif case['Case_ID'] == 'CASE_030':
        return {"root_cause": "NTP server is offline", "confidence": "medium"}
    elif case['Case_ID'] == 'CASE_007':
        return {"root_cause": "Missing default gateway on PC", "confidence": "high"}
    elif case['Case_ID'] == 'CASE_016':
        return {"root_cause": "Guest Wi-Fi password mismatch", "confidence": "medium"}
    elif case['Case_ID'] == 'CASE_027':
        return {"root_cause": "OSPF area mismatch", "confidence": "high"}
    return {
        "root_cause": case['Expected_Fault'],
        "confidence": "high",
        "evidence": show_output,
        "next_command": "show running-config",
        "fix_steps": ["configure terminal", "apply correct config", "end"]
    }
def run_ai_diagnosis(case: dict) -> dict:

    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            prompt = DIAGNOSE_PROMPT.format(
                symptom=case['Symptom'],
                topology=case['Topology_Note'],
                show_output=case['Show_Commands_Output']
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"AI Error: {e}. Falling back to mock.")
            return mock_ai_diagnosis(case)
    else:
        return mock_ai_diagnosis(case)

def log_human_review(case_id: str, ai_diagnosis: str, action: str, corrected_fault: str, reason: str):
    file_exists = LOG_FILE.exists()
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Case_ID", "AI_Diagnosis", "Action", "Corrected_Fault", "Reason"])
        writer.writerow([case_id, ai_diagnosis, action, corrected_fault, reason])
def get_all_cases() -> list:
    with open(CASES_FILE, mode='r') as f:
        return list(csv.DictReader(f))