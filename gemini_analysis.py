import os
from pathlib import Path
import google.generativeai as genai

# ==========================================================
# Google Gemini API Key
# ==========================================================

# Recommended:
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Temporary (replace with environment variable later)
GEMINI_API_KEY = "AQ.Ab8RN6KF9sBqivsdwB1g7ng1xYo692TGj1t_aXI7dtx_8zTGzw"

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

# ==========================================================
# Report Files
# ==========================================================

REPORT_FOLDER = Path("reports")

JENKINS_LOG = REPORT_FOLDER / "jenkins-console.txt"
TRIVY_REPORT = REPORT_FOLDER / "trivy-report.txt"
SONAR_REPORT = REPORT_FOLDER / "sonar-report.txt"

OUTPUT_REPORT = REPORT_FOLDER / "ai-security-report.txt"


# ==========================================================
# Read File
# ==========================================================

def read_file(file_path):
    if file_path.exists():
        return file_path.read_text(encoding="utf-8", errors="ignore")
    return f"{file_path.name} not found."


# ==========================================================
# Read Reports
# ==========================================================

jenkins_log = read_file(JENKINS_LOG)
trivy_report = read_file(TRIVY_REPORT)
sonar_report = read_file(SONAR_REPORT)

# ==========================================================
# Prompt
# ==========================================================

prompt = f"""
You are an experienced DevSecOps Security Engineer.

Analyze the following reports.

===========================================================
JENKINS BUILD LOG
===========================================================

{jenkins_log}

===========================================================
TRIVY REPORT
===========================================================

{trivy_report}

===========================================================
SONARQUBE REPORT
===========================================================

{sonar_report}

===========================================================

Generate a professional security report using these sections.

1. Build Summary
2. Overall Security Status
3. Root Cause Analysis
4. Vulnerabilities Found
5. Severity Classification
6. SonarQube Findings
7. Trivy Findings
8. Recommended Fixes
9. Best Practices
10. Final Conclusion

Use professional language.
"""

# ==========================================================
# Gemini Analysis
# ==========================================================

print("=" * 60)
print("Sending reports to Gemini...")
print("=" * 60)

response = model.generate_content(prompt)

analysis = response.text

print("\n")
print("=" * 60)
print("AI SECURITY REPORT")
print("=" * 60)
print(analysis)

# ==========================================================
# Save Report
# ==========================================================

REPORT_FOLDER.mkdir(exist_ok=True)

with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
    f.write(analysis)

print("\n")
print("=" * 60)
print("Report saved to:")
print(OUTPUT_REPORT)
print("=" * 60)
