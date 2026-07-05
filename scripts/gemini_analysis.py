"""
============================================================
AI-Powered DevSecOps Pipeline
Gemini Security Analysis
Part 1 - Collect Security Reports
============================================================
"""

import os
import json
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from google import genai


# ============================================================
# CONFIGURATION
# ============================================================

WORKSPACE = Path.cwd()

REPORTS_DIR = WORKSPACE / "reports"

TRIVY_FS_REPORT = REPORTS_DIR / "trivy-fs-report.json"
TRIVY_IMAGE_REPORT = REPORTS_DIR / "trivy-image-report.json"
JENKINS_INFO = REPORTS_DIR / "jenkins-build-info.txt"

OWASP_XML = WORKSPACE / "dependency-check-report" / "dependency-check-report.xml"


# SonarQube

SONAR_URL = "http://localhost:9000"

SONAR_PROJECT = "EmployeeManagement"

SONAR_TOKEN = os.getenv("SONAR_TOKEN")


# Gemini

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ============================================================
# CHECK REQUIRED FILES
# ============================================================

required_files = [
    TRIVY_FS_REPORT,
    TRIVY_IMAGE_REPORT,
    JENKINS_INFO,
    OWASP_XML
]

print("=" * 60)
print("Checking required security reports...")
print("=" * 60)

for file in required_files:

    if file.exists():

        print(f"[OK] {file.name}")

    else:

        print(f"[ERROR] Missing : {file}")
        raise FileNotFoundError(file)

print()


# ============================================================
# LOAD JSON
# ============================================================

def load_json(file_path):

    with open(file_path, "r", encoding="utf-8") as file:

        return json.load(file)


# ============================================================
# LOAD TEXT
# ============================================================

def load_text(file_path):

    with open(file_path, "r", encoding="utf-8") as file:

        return file.read()


# ============================================================
# LOAD XML
# ============================================================

def load_xml(file_path):

    tree = ET.parse(file_path)

    return tree.getroot()


# ============================================================
# READ REPORTS
# ============================================================

print("=" * 60)
print("Loading reports...")
print("=" * 60)

trivy_fs = load_json(TRIVY_FS_REPORT)

print("Loaded Trivy File System Report")

trivy_image = load_json(TRIVY_IMAGE_REPORT)

print("Loaded Trivy Docker Image Report")

jenkins_build = load_text(JENKINS_INFO)

print("Loaded Jenkins Build Information")

owasp_report = load_xml(OWASP_XML)

print("Loaded OWASP Dependency Check Report")

print()


# ============================================================
# SONARQUBE API
# ============================================================

print("=" * 60)
print("Connecting to SonarQube...")
print("=" * 60)

try:

    response = requests.get(

        f"{SONAR_URL}/api/measures/component",

        params={

            "component": SONAR_PROJECT,

            "metricKeys": ",".join([

                "bugs",
                "vulnerabilities",
                "code_smells",
                "coverage",
                "duplicated_lines_density",
                "security_rating",
                "reliability_rating",
                "sqale_rating"

            ])

        },

        auth=(SONAR_TOKEN, "")

    )

    response.raise_for_status()

    sonar_report = response.json()

    print("Connected to SonarQube")

except Exception as error:

    sonar_report = {}

    print("Unable to fetch SonarQube report")

    print(error)


print()


# ============================================================
# VERIFY GEMINI KEY
# ============================================================

print("=" * 60)
print("Checking Gemini API...")
print("=" * 60)

if GEMINI_API_KEY:

    print("Gemini API Key Found")

else:

    raise Exception("Gemini API Key not found")


print()


# ============================================================
# SUMMARY
# ============================================================

print("=" * 60)
print("Security reports successfully collected")
print("=" * 60)

print()

print("Trivy File Report Type :", type(trivy_fs))
print("Trivy Image Report Type:", type(trivy_image))
print("OWASP Report Type      :", type(owasp_report))
print("Sonar Report Type      :", type(sonar_report))

print()

print("Ready for Gemini Analysis...")



# ============================================================
# PART 2 - PARSE SECURITY REPORTS
# ============================================================

print("=" * 60)
print("Parsing Security Reports...")
print("=" * 60)


# ------------------------------------------------------------
# Trivy File System Report
# ------------------------------------------------------------

trivy_fs_total = 0

for result in trivy_fs.get("Results", []):

    vulnerabilities = result.get("Vulnerabilities", [])

    trivy_fs_total += len(vulnerabilities)

print(f"Trivy File System Vulnerabilities : {trivy_fs_total}")


# ------------------------------------------------------------
# Trivy Docker Image Report
# ------------------------------------------------------------

trivy_image_total = 0

for result in trivy_image.get("Results", []):

    vulnerabilities = result.get("Vulnerabilities", [])

    trivy_image_total += len(vulnerabilities)

print(f"Trivy Docker Image Vulnerabilities : {trivy_image_total}")


# ------------------------------------------------------------
# OWASP Dependency Check Report
# ------------------------------------------------------------

dependency_count = 0

for element in owasp_report.iter():

    if element.tag.endswith("dependency"):

        dependency_count += 1

print(f"Dependencies Scanned : {dependency_count}")


# ------------------------------------------------------------
# SonarQube Metrics
# ------------------------------------------------------------

print()

print("SonarQube Metrics")

print("-" * 40)

if sonar_report:

    measures = sonar_report.get("component", {}).get("measures", [])

    for metric in measures:

        metric_name = metric.get("metric")

        metric_value = metric.get("value")

        print(f"{metric_name} : {metric_value}")

else:

    print("No SonarQube data found.")


print()

print("=" * 60)
print("Security Report Parsing Completed")
print("=" * 60)


# ============================================================
# CREATE SUMMARY OBJECT
# ============================================================

security_summary = {

    "trivy_fs_vulnerabilities": trivy_fs_total,

    "trivy_image_vulnerabilities": trivy_image_total,

    "dependencies_scanned": dependency_count,

    "sonarqube": sonar_report

}


print()

print("Summary Created Successfully")

print(json.dumps(security_summary, indent=4))


# ============================================================
# PART 3 - GOOGLE GEMINI AI ANALYSIS
# ============================================================

print()
print("=" * 60)
print("Starting Google Gemini AI Analysis...")
print("=" * 60)


# ------------------------------------------------------------
# Configure Gemini
# ------------------------------------------------------------

print("Gemini Key Length:", len(GEMINI_API_KEY))
print("Gemini Key Starts With:", GEMINI_API_KEY[:6])

client = genai.Client(api_key=GEMINI_API_KEY)


# ------------------------------------------------------------
# Build Prompt
# ------------------------------------------------------------

prompt = f"""
You are an expert DevSecOps Security Engineer.

Analyze the following security scan results.

Project Name:
Employee Management System

Build Information:

{jenkins_build}

Security Summary:

{json.dumps(security_summary, indent=4)}

Please generate a professional security assessment report using the following format.

1. Build Summary

2. Overall Security Status

3. Root Cause Analysis

4. Trivy File System Analysis

5. Docker Image Analysis

6. OWASP Dependency Analysis

7. SonarQube Analysis

8. Security Recommendations

9. Deployment Readiness

10. Final Conclusion

Keep the report professional and suitable for a university dissertation.
"""


print("Prompt Created Successfully")
print()


# ------------------------------------------------------------
# Send Prompt to Gemini
# ------------------------------------------------------------

try:

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
if response.text:

    ai_report = response.text

else:

    ai_report = "No AI response received."

    print("=" * 60)
    print("Gemini Analysis Completed Successfully")
    print("=" * 60)

except Exception as error:

    print("Gemini API Error")

    print(error)

    ai_report = None


# ============================================================
# PART 4 - SAVE AI SECURITY REPORT
# ============================================================

print()
print("=" * 60)
print("Saving AI Security Report...")
print("=" * 60)

if ai_report:

    # --------------------------------------------------------
    # Save as TXT
    # --------------------------------------------------------

    txt_file = REPORTS_DIR / "ai-security-report.txt"

    with open(txt_file, "w", encoding="utf-8") as file:
        file.write(ai_report)

    print("TXT Report Saved")


    # --------------------------------------------------------
    # Save as Markdown
    # --------------------------------------------------------

    md_file = REPORTS_DIR / "ai-security-report.md"

    with open(md_file, "w", encoding="utf-8") as file:
        file.write(ai_report)

    print("Markdown Report Saved")


    # --------------------------------------------------------
    # Save as JSON
    # --------------------------------------------------------

    json_file = REPORTS_DIR / "ai-security-report.json"

    report_json = {
        "project": "Employee Management System",
        "generated_by": "Google Gemini",
        "status": "SUCCESS",
        "report": ai_report
    }

    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(report_json, file, indent=4)

    print("JSON Report Saved")


    # --------------------------------------------------------
    # Display Report
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("AI SECURITY REPORT")
    print("=" * 60)
    print()

    print(ai_report)

    print()
    print("=" * 60)
    print("All Reports Generated Successfully")
    print("=" * 60)

else:

    print("AI Report was not generated.")



