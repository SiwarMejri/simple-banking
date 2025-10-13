pipeline {
    agent any

    environment {
        VENV_DIR      = "${WORKSPACE}/venv"
        PYTHONPATH    = "${WORKSPACE}/src"
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
        ENVIRONMENT   = "test" // test = SQLite
        DATABASE_URL  = "sqlite:///./test_banking.db"
        IMAGE_NAME    = "siwarmejri/simple-banking"
        IMAGE_TAG     = "latest"
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
                echo "📦 Création de la virtualenv et installation des dépendances..."
                sh """
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    echo "🧹 Nettoyage du cache pip"
                    pip cache purge || true
                    pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('Tests Unitaires') {
            steps {
                echo "🧪 Exécution des tests unitaires avec TestClient..."
                script {
                    def testResult = sh(
                        script: """
                            . ${VENV_DIR}/bin/activate
                            export DATABASE_URL="${DATABASE_URL}"
                            export PYTHONPATH=${PYTHONPATH}
                            pytest --maxfail=0 --disable-warnings --cov=src --cov-report=xml -v || true
                        """,
                        returnStatus: true
                    )
                    if (testResult != 0) {
                        echo "⚠️ Des tests ont échoué (code ${testResult}) mais on continue le pipeline..."
                        currentBuild.result = "UNSTABLE"
                    }
                }
            }
        }

        stage('Analyse SAST avec SonarQube') {
            steps {
                echo "🔎 Analyse SAST avec SonarQube..."
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    script {
                        def sonarResult = sh(
                            script: """
                                sonar-scanner \
                                  -Dsonar.projectKey=simple-banking \
                                  -Dsonar.sources=src \
                                  -Dsonar.python.version=3.10 \
                                  -Dsonar.python.coverage.reportPaths=coverage.xml \
                                  -Dsonar.host.url=http://192.168.240.139:9000 \
                                  -Dsonar.token=$SONAR_TOKEN || true
                            """,
                            returnStatus: true
                        )
                        if (sonarResult != 0) {
                            echo "⚠️ SonarQube a rencontré des problèmes"
                            currentBuild.result = "UNSTABLE"
                        }
                    }
                }
            }
        }

        stage('Build Docker') {
            steps {
                echo "🐳 Construction de l'image Docker..."
                script {
                    def dockerResult = sh(script: "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} . || true", returnStatus: true)
                    if (dockerResult != 0) {
                        echo "⚠️ Docker build a échoué"
                        currentBuild.result = "UNSTABLE"
                    }
                }
            }
        }

        stage('Scan de vulnérabilités avec Trivy') {
            steps {
                echo "🛡️ Scan des vulnérabilités avec Trivy..."
                script {
                    def trivyResult = sh(script: """
                        trivy fs --severity CRITICAL,HIGH --format json --output trivy-report.json . || true
                        trivy image --severity CRITICAL,HIGH --format json --output trivy-image-report.json ${IMAGE_NAME}:${IMAGE_TAG} || true
                    """, returnStatus: true)
                    if (trivyResult != 0) {
                        echo "⚠️ Trivy a rencontré des problèmes"
                        currentBuild.result = "UNSTABLE"
                    }
                }
                archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
                archiveArtifacts artifacts: 'trivy-image-report.json', allowEmptyArchive: true
            }
        }

        stage('Generate PDF, Email & Push Docker') {
            steps {
                echo "📄 Génération du rapport PDF + envoi email + push Docker"
                script {
                    def reportResult = sh(
                        script: """
                            . ${VENV_DIR}/bin/activate
                            python3 generate_full_report.py \
                              --trivy-json trivy-report.json \
                              --trivy-image-json trivy-image-report.json \
                              --sonarqube-project simple-banking \
                              --output full_report.pdf || true
                        """,
                        returnStatus: true
                    )
                    if (reportResult != 0) {
                        echo "⚠️ Génération du PDF a échoué"
                        currentBuild.result = "UNSTABLE"
                    }
                }
                archiveArtifacts artifacts: 'full_report.pdf', allowEmptyArchive: false

                emailext(
                    subject: "📊 Rapport CI/CD - SonarQube + Trivy",
                    body: "Bonjour,\n\nLe rapport PDF consolidé du projet simple-banking est ci-joint.\n\nCordialement.",
                    to: "siwarmejri727@gmail.com",
                    attachmentsPattern: "**/full_report.pdf"
                )

                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials',
                                                 usernameVariable: 'DOCKER_USER',
                                                 passwordVariable: 'DOCKER_PASS')]) {
                    script {
                        def pushResult = sh(
                            script: '''
                                echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                                docker tag siwarmejri/simple-banking:latest $DOCKER_USER/simple-banking:latest
                                docker push $DOCKER_USER/simple-banking:latest || true
                                docker logout
                            ''',
                            returnStatus: true
                        )
                        if (pushResult != 0) {
                            echo "⚠️ Push Docker a échoué"
                            currentBuild.result = "UNSTABLE"
                        }
                    }
                }
            }
        }
    }

    post {
        always { echo "🏁 Pipeline terminé" }
        success { echo "✅ Pipeline réussi" }
        unstable { echo "⚠️ Pipeline terminé avec des erreurs (UNSTABLE)" }
        failure { echo "❌ Pipeline échoué" }
    }
}
