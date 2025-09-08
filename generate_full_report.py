import json
import requests
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import argparse
import os

def load_json(file_path):
    """Charge un fichier JSON s'il existe."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def fetch_sonarqube_metrics(project_key, sonar_url='http://192.168.240.139:9000', token=None):
    """
    Récupère les métriques principales de SonarQube pour un projet donné.
    """
    api_url = f"{sonar_url}/api/measures/component?component={project_key}&metricKeys=bugs,vulnerabilities,code_smells,coverage,duplicated_lines_density,ncloc"
    headers = {}
    if token:
        headers['Authorization'] = f"Basic {token}"
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️ Erreur SonarQube: {e}")
        return {}

def format_trivy_results(trivy_data):
    """
    Formate les résultats Trivy pour affichage dans un tableau PDF.
    """
    rows = [["CVE", "Package", "Severity", "Installed Version", "Fixed Version"]]
    for result in trivy_data.get('Results', []):
        for v in result.get('Vulnerabilities', []):
            rows.append([
                v.get('VulnerabilityID', ''),
                v.get('PkgName', ''),
                v.get('Severity', ''),
                v.get('InstalledVersion', ''),
                v.get('FixedVersion', '')
            ])
    return rows

def generate_pdf(trivy_fs, trivy_img, sonar_metrics, output_file):
    """Génère le PDF final consolidé SonarQube + Trivy"""
    doc = SimpleDocTemplate(output_file, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # === Titre principal ===
    elements.append(Paragraph("📊 Rapport CI/CD - SonarQube + Trivy", styles['Title']))
    elements.append(Spacer(1, 20))

    # === Résumé exécutif ===
    elements.append(Paragraph("Résumé exécutif", styles['Heading2']))
    resume = """
    Ce rapport consolide les résultats des analyses **SonarQube** (qualité du code, sécurité)
    et **Trivy** (vulnérabilités systèmes et images Docker).
    """
    elements.append(Paragraph(resume, styles['Normal']))
    elements.append(Spacer(1, 20))

    # === Section SonarQube ===
    elements.append(Paragraph("✅ Résultats SonarQube", styles['Heading2']))
    if sonar_metrics and 'component' in sonar_metrics:
        measures = {m['metric']: m['value'] for m in sonar_metrics['component']['measures']}
        data = [
            ["Métrique", "Valeur"],
            ["🐞 Bugs", measures.get("bugs", "0")],
            ["🔒 Vulnérabilités", measures.get("vulnerabilities", "0")],
            ["💨 Code Smells", measures.get("code_smells", "0")],
            ["📈 Couverture (%)", measures.get("coverage", "0")],
            ["📊 Lignes de code", measures.get("ncloc", "0")],
            ["📑 Densité duplications (%)", measures.get("duplicated_lines_density", "0")]
        ]
        table = Table(data, colWidths=[250, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4F81BD")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("⚠️ Impossible de récupérer les données SonarQube.", styles['Normal']))

    elements.append(Spacer(1, 20))

    # === Section Trivy Filesystem ===
    elements.append(Paragraph("🛡️ Analyse Trivy - Système de fichiers", styles['Heading2']))
    fs_rows = format_trivy_results(trivy_fs)
    if len(fs_rows) > 1:
        fs_table = Table(fs_rows, colWidths=[100, 100, 80, 100, 100])
    else:
        # Toujours afficher un tableau vide avec en-tête
        fs_rows = [["CVE", "Package", "Severity", "Installed Version", "Fixed Version"]]
        fs_table = Table(fs_rows, colWidths=[100, 100, 80, 100, 100])
    fs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#C0504D")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
    ]))
    elements.append(fs_table)
    if len(fs_rows) == 1:
        elements.append(Paragraph("✅ Aucune vulnérabilité critique ou haute trouvée.", styles['Normal']))

    elements.append(Spacer(1, 20))

    # === Section Trivy Image ===
    elements.append(Paragraph("🛡️ Analyse Trivy - Image Docker", styles['Heading2']))
    img_rows = format_trivy_results(trivy_img)
    if len(img_rows) > 1:
        img_table = Table(img_rows, colWidths=[100, 100, 80, 100, 100])
    else:
        img_rows = [["CVE", "Package", "Severity", "Installed Version", "Fixed Version"]]
        img_table = Table(img_rows, colWidths=[100, 100, 80, 100, 100])
    img_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#9BBB59")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
    ]))
    elements.append(img_table)
    if len(img_rows) == 1:
        elements.append(Paragraph("✅ Aucune vulnérabilité critique ou haute trouvée dans l'image.", styles['Normal']))

    # === Fin du PDF ===
    doc.build(elements)
    print(f"✅ Rapport PDF généré : {output_file}")

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
