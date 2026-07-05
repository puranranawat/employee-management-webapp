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
