import json
import requests
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import argparse
import os

def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        return {}

def fetch_sonarqube_metrics(project_key, sonar_url='http://192.168.240.139:9000', token=None):
    api_url = f"{sonar_url}/api/measures/component?component={project_key}&metricKeys=bugs,vulnerabilities,code_smells,coverage,duplicated_lines_density"
    headers = {}
    if token:
        headers['Authorization'] = f"Basic {token}"
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except:
        return {}

def add_title(pdf, title):
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(50, 800, title)
    pdf.setFont("Helvetica", 12)

def add_section(pdf, heading, text, y_pos):
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y_pos, heading)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y_pos - 20, text)

def generate_pdf(trivy_fs, trivy_img, sonar_metrics, output_file):
    pdf = canvas.Canvas(output_file, pagesize=A4)
    width, height = A4
    y = 800

    add_title(pdf, "Rapport CI/CD - SonarQube + Trivy")

    # SonarQube Metrics
    sonar_text = ""
    if sonar_metrics and 'component' in sonar_metrics:
        measures = sonar_metrics['component']['measures']
        sonar_text = ", ".join([f"{m['metric']}: {m['value']}" for m in measures])
    else:
        sonar_text = "Aucune donnée SonarQube disponible."

    add_section(pdf, "✅ SonarQube Metrics", sonar_text, y - 50)
    y -= 100

    # Trivy Filesystem Scan
    trivy_fs_text = ""
    if trivy_fs:
        for vuln in trivy_fs.get('Results', []):
            for v in vuln.get('Vulnerabilities', []):
                trivy_fs_text += f"{v.get('VulnerabilityID', '')} - {v.get('PkgName','')} - {v.get('Severity','')}\n"
    else:
        trivy_fs_text = "Aucune vulnérabilité critique ou haute trouvée."

    add_section(pdf, "🛡️ Trivy Filesystem Scan", trivy_fs_text, y)
    y -= 200

    # Trivy Image Scan
    trivy_img_text = ""
    if trivy_img:
        for vuln in trivy_img.get('Results', []):
            for v in vuln.get('Vulnerabilities', []):
                trivy_img_text += f"{v.get('VulnerabilityID', '')} - {v.get('PkgName','')} - {v.get('Severity','')}\n"
    else:
        trivy_img_text = "Aucune vulnérabilité critique ou haute trouvée dans l'image."

    add_section(pdf, "🛡️ Trivy Image Scan", trivy_img_text, y)
    y -= 200

    pdf.save()
    print(f"PDF généré : {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Génère un rapport PDF consolidé SonarQube + Trivy")
    parser.add_argument("--trivy-json", required=True, help="Chemin vers trivy-report.json (filesystem)")
    parser.add_argument("--trivy-image-json", required=True, help="Chemin vers trivy-image-report.json (image)")
    parser.add_argument("--sonarqube-project", required=True, help="Clé du projet SonarQube")
    parser.add_argument("--output", default="full_report.pdf", help="Nom du fichier PDF de sortie")
    parser.add_argument("--sonar-url", default="http://192.168.240.139:9000", help="URL SonarQube")
    parser.add_argument("--sonar-token", default=None, help="Token SonarQube pour authentification")
    args = parser.parse_args()

    trivy_fs = load_json(args.trivy_json)
    trivy_img = load_json(args.trivy_image_json)
    sonar_metrics = fetch_sonarqube_metrics(args.sonarqube_project, args.sonar_url, args.sonar_token)
    
    generate_pdf(trivy_fs, trivy_img, sonar_metrics, args.output)
