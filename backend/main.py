from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os

from ai_engine import get_all_cases, rule_checker, run_ai_diagnosis, log_human_review

app = FastAPI(title="NetSage AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReviewPayload(BaseModel):
    case_id: str
    ai_diagnosis: str
    action: str 
    corrected_fault: str
    reason: str

@app.get("/api/cases")
def fetch_cases():
    """Returns all 30 cases for the dashboard."""
    return get_all_cases()

@app.post("/api/diagnose/{case_id}")
def diagnose_case(case_id: str):
    """Runs Rule Checker and AI Diagnosis on a specific case."""
    cases = get_all_cases()
    case = next((c for c in cases if c['Case_ID'] == case_id), None)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
 
    rules = rule_checker(case['Show_Commands_Output'])

    ai_result = run_ai_diagnosis(case)
    
    return {
        "case_details": case,
        "rule_checker_findings": rules,
        "ai_response": ai_result
    }

@app.post("/api/review")
def submit_review(payload: ReviewPayload):
    """Step 5: Logs the human review decision."""
    log_human_review(
        payload.case_id, 
        payload.ai_diagnosis, 
        payload.action, 
        payload.corrected_fault, 
        payload.reason
    )
    return {"status": "success", "message": "Review logged successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)