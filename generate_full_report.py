import json
import requests
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import argparse
import base64
import os

# === Chargement des données JSON ===
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

# === Récupération des métriques SonarQube ===
def fetch_sonarqube_metrics(project_key, sonar_url='http://192.168.240.139:9000', token=None):
    api_url = f"{sonar_url}/api/measures/component?component={project_key}&metricKeys=bugs,vulnerabilities,code_smells,coverage,duplicated_lines_density,ncloc"
    headers = {}

    if token:
        # Encodage Base64 de "<token>:"
        encoded_token = base64.b64encode(f"{token}:".encode()).decode()
        headers['Authorization'] = f"Basic {encoded_token}"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"⚠️ Erreur SonarQube HTTP: {http_err} ({response.status_code})")
        print(f"URL: {api_url}")
        print("💡 Vérifie ton token et tes permissions dans SonarQube (Administration > Security > Tokens).")
        return {}
    except Exception as e:
        print(f"⚠️ Erreur SonarQube: {e}")
        return {}

# === Formatage des résultats Trivy ===
def format_trivy_results(trivy_data):
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

# === Génération du PDF ===
def generate_pdf(trivy_fs, trivy_img, sonar_metrics, output_file):
    doc = SimpleDocTemplate(output_file, pagesize=A4, title="Rapport CI/CD - SonarQube + Trivy")
    elements = []
    styles = getSampleStyleSheet()

    # Styles personnalisés
    styles.add(ParagraphStyle(name='SubTitle', fontSize=12, textColor=colors.HexColor("#4B4B4B"), spaceAfter=8))
    styles.add(ParagraphStyle(name='Advice', fontSize=10, textColor=colors.HexColor("#555555"), leftIndent=15, spaceAfter=6))
    styles.add(ParagraphStyle(name='Section', fontSize=14, textColor=colors.HexColor("#1F4E79"), spaceAfter=10, leading=16))
    styles.add(ParagraphStyle(name='NormalGray', fontSize=10, textColor=colors.HexColor("#333333"), spaceAfter=8))

    # === Titre principal ===
    elements.append(Paragraph("📊 Rapport CI/CD - SonarQube + Trivy", styles['Title']))
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("Résumé exécutif", styles['Section']))
    elements.append(Paragraph(
        "Ce rapport consolide les résultats des analyses <b>SonarQube</b> (qualité du code, sécurité) et <b>Trivy</b> (vulnérabilités systèmes et images Docker).",
        styles['NormalGray']
    ))
    elements.append(Spacer(1, 20))

    # === Section SonarQube ===
    elements.append(Paragraph("✅ Résultats SonarQube", styles['Section']))

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
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1F4E79")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(table)

        # 🧠 Ajout d’un résumé intelligent
        bugs = measures.get("bugs", "0")
        vulns = measures.get("vulnerabilities", "0")
        smells = measures.get("code_smells", "0")
        coverage = measures.get("coverage", "0")
        advice_text = f"""
        📘 <b>Résumé SonarQube :</b><br/>
        - Bugs détectés : {bugs}<br/>
        - Vulnérabilités : {vulns}<br/>
        - Code Smells : {smells}<br/>
        - Couverture de tests : {coverage}%<br/>
        <br/>
        💡 <b>Conseil :</b> Corrige en priorité les vulnérabilités critiques et les bugs majeurs.<br/>
        Si la couverture est inférieure à 60%, augmente les tests unitaires.<br/>
        Révise les modules avec des code smells récurrents pour améliorer la maintenabilité.
        """
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(advice_text, styles['Advice']))

    else:
        elements.append(Paragraph("⚠️ Impossible de récupérer les données SonarQube.", styles['NormalGray']))
        elements.append(Paragraph(
            "💡 Conseil : Vérifie ton token SonarQube et les permissions d'accès API dans Jenkins.",
            styles['Advice']
        ))

    elements.append(Spacer(1, 20))

    # === Section Trivy Filesystem ===
    elements.append(Paragraph("🛡️ Analyse Trivy - Système de fichiers", styles['Section']))
    fs_rows = format_trivy_results(trivy_fs)
    fs_table = Table(fs_rows if len(fs_rows) > 1 else [["CVE", "Package", "Severity", "Installed Version", "Fixed Version"]],
                     colWidths=[100, 100, 80, 100, 100])
    fs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#C0504D")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
    ]))
    elements.append(fs_table)

    if len(fs_rows) == 1:
        elements.append(Paragraph("✅ Aucune vulnérabilité critique ou haute trouvée.", styles['NormalGray']))
    else:
        elements.append(Paragraph("💡 Conseil : Corrige en priorité les dépendances avec sévérité 'HIGH' ou 'CRITICAL'.", styles['Advice']))

    elements.append(Spacer(1, 20))

    # === Section Trivy Image ===
    elements.append(Paragraph("🐳 Analyse Trivy - Image Docker", styles['Section']))
    img_rows = format_trivy_results(trivy_img)
    img_table = Table(img_rows if len(img_rows) > 1 else [["CVE", "Package", "Severity", "Installed Version", "Fixed Version"]],
                      colWidths=[100, 100, 80, 100, 100])
    img_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#9BBB59")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
    ]))
    elements.append(img_table)

    if len(img_rows) == 1:
        elements.append(Paragraph("✅ Aucune vulnérabilité critique trouvée dans l'image.", styles['NormalGray']))
    else:
        elements.append(Paragraph(
            "💡 Conseil : Mets à jour ton image Docker de base (Debian, Ubuntu, etc.) et les paquets vulnérables.",
            styles['Advice']
        ))

    # === Synthèse globale ===
    elements.append(Spacer(1, 25))
    elements.append(Paragraph("📈 Analyse Globale & Recommandations CI/CD", styles['Section']))
    elements.append(Paragraph("""
    🔹 Intègre SonarQube et Trivy dans chaque build du pipeline pour un contrôle qualité continu.<br/>
    🔹 Active les seuils d’échec (quality gates) pour bloquer les builds vulnérables.<br/>
    🔹 Automatise les mises à jour de dépendances via Dependabot ou Renovate.<br/>
    🔹 Exporte régulièrement les rapports pour suivi et conformité sécurité.<br/>
    🔹 Surveille les performances du pipeline et les tendances de vulnérabilités au fil du temps.
    """, styles['Advice']))

    doc.build(elements)
    print(f"✅ Rapport PDF généré : {output_file}")

# === Point d’entrée ===
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
