#!/usr/bin/env python3
import json
import requests
import base64
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import argparse
import os

def load_json(file_path):
    """Charge un fichier JSON s'il existe."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def fetch_sonarqube_metrics(project_key, sonar_url='http://192.168.240.139:9000', token=None):
    """Récupère les métriques principales de SonarQube pour un projet donné."""
    api_url = f"{sonar_url}/api/measures/component?component={project_key}&metricKeys=bugs,vulnerabilities,code_smells,coverage,duplicated_lines_density,ncloc"
    headers = {}
    if token:
        token_bytes = f"{token}:".encode('utf-8')  # username vide
        token_b64 = base64.b64encode(token_bytes).decode('utf-8')
        headers['Authorization'] = f"Basic {token_b64}"
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"⚠️ Erreur HTTP {response.status_code} SonarQube: {response.text}")
        return {}
    except Exception as e:
        print(f"⚠️ Erreur SonarQube: {e}")
        return {}

def format_trivy_results(trivy_data):
    """Formate les résultats Trivy pour affichage dans un tableau PDF."""
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

def create_table(data, col_widths, header_color, row_colors=[colors.white, colors.HexColor("#F2F2F2")]):
    """Crée un tableau stylé avec lignes alternées (zebra)."""
    table = Table(data, colWidths=col_widths)
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), header_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
    ])
    for i in range(1, len(data)):
        bg_color = row_colors[i % len(row_colors)]
        style.add('BACKGROUND', (0,i), (-1,i), bg_color)
    table.setStyle(style)
    return table

def generate_pdf(trivy_fs, trivy_img, sonar_metrics, output_file):
    """Génère le PDF final consolidé SonarQube + Trivy avec style professionnel."""
    doc = SimpleDocTemplate(output_file, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Heading1Center', parent=styles['Heading1'], alignment=1))
    styles.add(ParagraphStyle(name='NormalJustify', parent=styles['Normal'], alignment=4, leading=14))

    # Titre principal
    elements.append(Paragraph("Rapport CI/CD - SonarQube + Trivy", styles['Heading1Center']))
    elements.append(Spacer(1, 15))

    # Résumé exécutif
    elements.append(Paragraph("Résumé exécutif", styles['Heading2']))
    resume = """
    Ce rapport présente les résultats des analyses de qualité de code et sécurité avec SonarQube,
    ainsi que les vulnérabilités détectées dans le système et l'image Docker par Trivy.
    """
    elements.append(Paragraph(resume, styles['NormalJustify']))
    elements.append(Spacer(1, 15))

    # Section SonarQube
    elements.append(Paragraph("Résultats SonarQube", styles['Heading2']))
    if sonar_metrics and 'component' in sonar_metrics:
        measures = {m['metric']: m['value'] for m in sonar_metrics['component']['measures']}
        data = [
            ["Métrique", "Valeur"],
            ["Bugs", measures.get("bugs", "0")],
            ["Vulnérabilités", measures.get("vulnerabilities", "0")],
            ["Code Smells", measures.get("code_smells", "0")],
            ["Couverture (%)", measures.get("coverage", "0")],
            ["Lignes de code", measures.get("ncloc", "0")],
            ["Densité duplications (%)", measures.get("duplicated_lines_density", "0")]
        ]
        table = create_table(data, [250, 150], colors.HexColor("#4F81BD"))
        elements.append(table)
    else:
        elements.append(Paragraph("⚠️ Impossible de récupérer les données SonarQube.", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Section Trivy Filesystem
    elements.append(Paragraph("Analyse Trivy - Système de fichiers", styles['Heading2']))
    fs_rows = format_trivy_results(trivy_fs)
    if len(fs_rows) == 1:
        elements.append(Paragraph("✅ Aucune vulnérabilité critique ou haute trouvée.", styles['Normal']))
    fs_table = create_table(fs_rows, [100, 100, 80, 100, 100], colors.HexColor("#C0504D"))
    elements.append(fs_table)
    elements.append(Spacer(1, 20))

    # Section Trivy Image
    elements.append(Paragraph("Analyse Trivy - Image Docker", styles['Heading2']))
    img_rows = format_trivy_results(trivy_img)
    if len(img_rows) == 1:
        elements.append(Paragraph("✅ Aucune vulnérabilité critique ou haute trouvée dans l'image.", styles['Normal']))
    img_table = create_table(img_rows, [100, 100, 80, 100, 100], colors.HexColor("#9BBB59"))
    elements.append(img_table)

    # Fin du PDF
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
