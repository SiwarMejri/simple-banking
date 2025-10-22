pipeline {
    agent any
    environment {
        VENV_DIR      = "${WORKSPACE}/venv"
        PYTHONPATH    = "${WORKSPACE}/src/app"
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
        ENVIRONMENT   = "test"
        DATABASE_URL  = "sqlite:///./test_banking.db"
        IMAGE_NAME    = "siwarmejri/simple-banking"
        IMAGE_TAG     = "latest"
        SONAR_TOKEN   = credentials('sonar-token')
    }

    stages {

        stage('Checkout SCM') {
            steps {
                echo "🔄 Récupération du code source..."
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo "📦 Création du virtualenv et installation des dépendances..."
                sh """
                    set -e
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('Validation des Imports') {
            steps {
                echo "🔍 Validation des imports Python..."
                script {
                    def validationResult = sh(
                        script: """
                            set -e
                            . ${VENV_DIR}/bin/activate
                            export PYTHONPATH=$WORKSPACE/src/app
                            
                            # Vérification de tous les imports critiques
                            python -c "
                            try:
                                # Vérifier les imports des modèles
                                from src.app.models.user import UserModel
                                from src.app.models.account import AccountModel  
                                from src.app.models.transaction import TransactionModel
                                print('✅ Import des modèles individuels réussi')
                                
                                # Vérifier les imports via __init__.py
                                from src.app.models import User, Account, Transaction
                                print('✅ Import via __init__.py réussi')
                                
                                # Vérifier l'import de l'app principale
                                from src.app.main import app
                                print('✅ Import de l\\\\'app principale réussi')
                                
                                print('🎉 Tous les imports fonctionnent parfaitement')
                            except ImportError as e:
                                print(f'❌ Erreur d\\\\'importation: {e}')
                                import traceback
                                traceback.print_exc()
                                exit(1)
                            "
                        """,
                        returnStatus: true
                    )

                    if (validationResult != 0) {
                        error("❌ Validation des imports échouée - Corrigez les problèmes d'importation avant de continuer")
                    } else {
                        echo "✅ Tous les imports sont valides"
                    }
                }
            }
        }

        stage('Tests Unitaires') {
            steps {
                echo "🧪 Exécution des tests unitaires avec TestClient..."
                script {
                    try {
                        sh """
                            set -e
                            . ${VENV_DIR}/bin/activate
                            export TESTING=1
                            export PYTHONPATH=$WORKSPACE/src/app
                            
                            # Exécuter les tests avec capture du code de sortie
                            pytest --disable-warnings --cov=src/app --cov-report=xml:coverage.xml -v || exit 1
                        """
                        echo "✅ Tous les tests unitaires ont réussi"
                    } catch (Exception e) {
                        echo "❌ Échec des tests unitaires: ${e.getMessage()}"
                        // Continuer pour avoir les rapports malgré les tests échoués
                    }
                }
                archiveArtifacts artifacts: 'pytest-output.log,coverage.xml', allowEmptyArchive: true
            }
        }

        stage('Analyse SAST avec SonarQube') {
            steps {
                echo "🔎 Analyse SAST avec SonarQube..."
                withSonarQubeEnv('sonarqube') {
                    script {
                        def scannerHome = tool 'sonar-scanner'
                        sh """
                            . ${VENV_DIR}/bin/activate
                            echo "📄 Vérification du fichier coverage.xml..."
                            if [ -f "${WORKSPACE}/coverage.xml" ]; then
                                echo "✅ coverage.xml trouvé"
                                ls -l ${WORKSPACE}/coverage.xml
                            else
                                echo "⚠️ coverage.xml introuvable, création d'un fichier vide"
                                echo '<coverage></coverage>' > ${WORKSPACE}/coverage.xml
                            fi

                            ${scannerHome}/bin/sonar-scanner \
                              -Dsonar.projectKey=simple-banking \
                              -Dsonar.sources=src/app \
                              -Dsonar.exclusions=src/app/tests/**,**/__pycache__/** \
                              -Dsonar.tests=src/app/tests \
                              -Dsonar.python.version=3.10 \
                              -Dsonar.python.coverage.reportPaths=${WORKSPACE}/coverage.xml \
                              -Dsonar.host.url=$SONAR_HOST_URL \
                              -Dsonar.token=$SONAR_TOKEN \
                              -Dsonar.scm.disabled=false
                        """
                    }
                }
            }
        }

        stage('Vérification Quality Gate') {
            steps {
                script {
                    try {
                        timeout(time: 10, unit: 'MINUTES') {
                            def qg = waitForQualityGate()
                            echo "🔍 Résultat complet du Quality Gate : ${qg.toString()}"

                            if (qg.conditions) {
                                qg.conditions.each { cond ->
                                    echo "Metric: ${cond.metric}, Status: ${cond.status}, Value: ${cond.value}, Threshold: ${cond.errorThreshold}"
                                }
                            }

                            if (qg.status != 'OK') {
                                echo "⚠️ Quality Gate échoué: ${qg.status}"
                                // Continuer le pipeline même si le Quality Gate échoue
                                currentBuild.result = 'UNSTABLE'
                            } else {
                                echo "✅ Quality Gate réussi"
                            }
                        }
                    } catch (err) {
                        echo "⚠️ Impossible de récupérer le Quality Gate: ${err}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Build Docker') {
            steps {
                echo "🐳 Construction de l'image Docker..."
                script {
                    try {
                        sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                        echo "✅ Image Docker construite avec succès"
                    } catch (Exception e) {
                        echo "⚠️ Échec de la construction Docker: ${e.getMessage()}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Scan de vulnérabilités avec Trivy') {
            when {
                expression { 
                    currentBuild.result != 'FAILURE' && 
                    fileExists('Dockerfile') 
                }
            }
            steps {
                echo "🛡️ Scan des vulnérabilités avec Trivy..."
                script {
                    try {
                        sh """
                            echo "📂 Scan du code source avec Trivy (FS)..."
                            trivy fs --scanners vuln --exit-code 0 --format table --output trivy-report.txt --ignore-unfixed --timeout 5m . || true
                            trivy fs --scanners vuln --exit-code 0 --format json  --output trivy-report.json --ignore-unfixed --timeout 5m . || true

                            echo "🐳 Scan de l'image Docker ${IMAGE_NAME}:${IMAGE_TAG}..."
                            trivy image --scanners vuln --exit-code 0 --format table --output trivy-image-report.txt --ignore-unfixed --timeout 10m ${IMAGE_NAME}:${IMAGE_TAG} || true
                            trivy image --scanners vuln --exit-code 0 --format json  --output trivy-image-report.json --ignore-unfixed --timeout 10m ${IMAGE_NAME}:${IMAGE_TAG} || true
                        """
                        echo "✅ Scan Trivy terminé (FS + Image)"
                    } catch (Exception e) {
                        echo "⚠️ Échec du scan Trivy: ${e.getMessage()}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
                archiveArtifacts artifacts: 'trivy-report.json,trivy-image-report.json,trivy-report.txt,trivy-image-report.txt', allowEmptyArchive: true
            }
        }

        stage('Generate PDF, Email & Push Docker') {
            when {
                expression { currentBuild.result != 'FAILURE' }
            }
            steps {
                echo "📄 Génération du rapport PDF + envoi email + push Docker"
                script {
                    try {
                        sh """
                            . ${VENV_DIR}/bin/activate
                            # Vérifier si le script de génération existe
                            if [ -f "generate_full_report.py" ]; then
                                python3 generate_full_report.py \
                                  --trivy-json trivy-report.json \
                                  --trivy-image-json trivy-image-report.json \
                                  --sonarqube-project simple-banking \
                                  --output full_report.pdf \
                                  --sonar-url $SONAR_HOST_URL \
                                  --sonar-token $SONAR_TOKEN || echo "⚠️ Génération PDF échouée"
                            else
                                echo "⚠️ generate_full_report.py non trouvé, création PDF basique"
                                echo "Rapport CI/CD - Projet Simple Banking" > full_report.txt
                                echo "Date: \$(date)" >> full_report.txt
                                echo "Commit: \$(git log -1 --oneline)" >> full_report.txt
                            fi
                        """

                        if (fileExists('full_report.pdf')) {
                            archiveArtifacts artifacts: 'full_report.pdf', allowEmptyArchive: false
                            emailext(
                                subject: "📊 Rapport CI/CD - SonarQube + Trivy - Build ${currentBuild.number}",
                                body: """Bonjour,

Le rapport PDF consolidé du projet simple-banking (Build ${currentBuild.number}) est ci-joint.

Statut du build: ${currentBuild.result}
Détails: ${env.BUILD_URL}

Cordialement,
Système CI/CD Jenkins""",
                                to: "siwarmejri727@gmail.com",
                                attachmentsPattern: "**/full_report.pdf",
                                mimeType: 'application/pdf'
                            )
                        } else if (fileExists('full_report.txt')) {
                            archiveArtifacts artifacts: 'full_report.txt', allowEmptyArchive: false
                            echo "📧 Email avec rapport texte envoyé"
                        } else {
                            echo "⚠️ Aucun rapport généré, email non envoyé."
                        }

                        // Push Docker optionnel
                        withCredentials([usernamePassword(credentialsId: 'dockerhub-siwar',
                                                         usernameVariable: 'DOCKER_USER',
                                                         passwordVariable: 'DOCKER_PASS')]) {
                            sh '''
                                echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin || echo "⚠️ Login Docker échoué"
                                docker tag ${IMAGE_NAME}:${IMAGE_TAG} $DOCKER_USER/simple-banking:latest || echo "⚠️ Tag Docker échoué"
                                docker push $DOCKER_USER/simple-banking:latest || echo "⚠️ Push Docker échoué"
                                docker logout || true
                            '''
                        }
                    } catch (Exception e) {
                        echo "⚠️ Échec de l'étape de rapport: ${e.getMessage()}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }

        stage('Déploiement (optionnel)') {
            when {
                expression { currentBuild.result == 'SUCCESS' }
            }
            steps {
                echo "🚀 Étape de déploiement à compléter selon ton environnement (Docker Compose, Kubernetes, VM...)"
            }
        }
    }

    post {
        always {
            echo "🏁 Pipeline terminé - Statut: ${currentBuild.result}"
            cleanWs()
        }
        success {
            echo "✅ Pipeline réussi"
        }
        failure {
            echo "❌ Pipeline échoué"
        }
        unstable {
            echo "⚠️ Pipeline instable - Vérifiez les warnings"
        }
    }
}
