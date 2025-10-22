pipeline {
    agent any
    environment {
        VENV_DIR      = "${WORKSPACE}/venv"
        PYTHONPATH    = "${WORKSPACE}/src"  // Pointe vers src/ pour les imports corrects
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
                echo "📦 Création de la virtualenv et installation des dépendances..."
                sh """
                    set -e
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
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
                            set -e
                            set -o pipefail  # Correction : Propager les erreurs de pytest (même avec piping vers tee)
                            . ${VENV_DIR}/bin/activate
                            export TESTING=1
                            export PYTHONPATH=${WORKSPACE}/src  # Assure que PYTHONPATH pointe vers src/
                            pytest --disable-warnings --cov=src/app --cov-report=xml:coverage.xml -v | tee pytest-output.log
                        """,
                        returnStatus: true
                    )

                    if (testResult != 0) {
                        echo "⚠️ Certains tests ont échoué, voir pytest-output.log"
                        error("❌ Build échoué à cause des tests unitaires")
                    } else {
                        echo "✅ Tous les tests unitaires ont réussi"
                    }
                }
                archiveArtifacts artifacts: 'pytest-output.log', allowEmptyArchive: false
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
                            ls -l ${WORKSPACE}/coverage.xml || echo "⚠️ coverage.xml introuvable !"

                            ${scannerHome}/bin/sonar-scanner \
                              -Dsonar.projectKey=simple-banking \
                              -Dsonar.sources=src/app \
                              -Dsonar.exclusions=src/app/tests/** \
                              -Dsonar.tests=src/app/tests \
                              -Dsonar.python.version=3.10 \
                              -Dsonar.python.coverage.reportPaths=${WORKSPACE}/coverage.xml \
                              -Dsonar.host.url=$SONAR_HOST_URL \
                              -Dsonar.token=$SONAR_TOKEN
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
                                error("❌ Pipeline échoué à cause du Quality Gate")
                            } else {
                                echo "✅ Quality Gate réussi"
                            }
                        }
                    } catch (err) {
                        echo "⚠️ Impossible de récupérer le Quality Gate ou erreur: ${err}"
                    }
                }
            }
        }

        stage('Build Docker') {
            steps {
                echo "🐳 Construction de l'image Docker..."
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Scan de vulnérabilités avec Trivy') {
            steps {
                echo "🛡️ Scan des vulnérabilités avec Trivy..."
                script {
                    sh """
                        echo "📂 Scan du code source avec Trivy (FS)..."
                        trivy fs --scanners vuln --exit-code 0 --format table --output trivy-report.txt --ignore-unfixed --timeout 5m .
                        trivy fs --scanners vuln --exit-code 0 --format json  --output trivy-report.json --ignore-unfixed --timeout 5m .

                        echo "🐳 Scan de l'image Docker ${IMAGE_NAME}:${IMAGE_TAG}..."
                        trivy image --scanners vuln --exit-code 0 --format table --output trivy-image-report.txt --ignore-unfixed --timeout 10m ${IMAGE_NAME}:${IMAGE_TAG}
                        trivy image --scanners vuln --exit-code 0 --format json  --output trivy-image-report.json --ignore-unfixed --timeout 10m ${IMAGE_NAME}:${IMAGE_TAG}
                    """
                    echo "✅ Scan Trivy terminé (FS + Image)"
                }
                archiveArtifacts artifacts: 'trivy-report.json,trivy-image-report.json,trivy-report.txt,trivy-image-report.txt', allowEmptyArchive: true
            }
        }

        stage('Generate PDF, Email & Push Docker') {
            steps {
                echo "📄 Génération du rapport PDF + envoi email + push Docker"
                sh """
                    . ${VENV_DIR}/bin/activate
                    python3 generate_full_report.py \
                      --trivy-json trivy-report.json \
                      --trivy-image-json trivy-image-report.json \
                      --sonarqube-project simple-banking \
                      --output full_report.pdf \
                      --sonar-url $SONAR_HOST_URL \
                      --sonar-token $SONAR_TOKEN
                """
                archiveArtifacts artifacts: 'full_report.pdf', allowEmptyArchive: false

                script {
                    if (fileExists('full_report.pdf')) {
                        emailext(
                            subject: "📊 Rapport CI/CD - SonarQube + Trivy",
                            body: "Bonjour,\n\nLe rapport PDF consolidé du projet simple-banking est ci-joint.\n\nCordialement.",
                            to: "siwarmejri727@gmail.com",
                            attachmentsPattern: "**/full_report.pdf",
                            mimeType: 'application/pdf'
                        )
                    } else {
                        echo "⚠️ PDF non généré, email non envoyé."
                    }
                }

                withCredentials([usernamePassword(credentialsId: 'dockerhub-siwar',
                                                 usernameVariable: 'DOCKER_USER',
                                                 passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} $DOCKER_USER/simple-banking:latest
                        docker push $DOCKER_USER/simple-banking:latest
                        docker logout
                    '''
                }
            }
        }

        stage('Déploiement (optionnel)') {
            steps {
                echo "🚀 Étape de déploiement à compléter selon ton environnement (Docker Compose, Kubernetes, VM...)"
            }
        }
    }

    post {
        always { echo "🏁 Pipeline terminé" }
        success { echo "✅ Pipeline réussi" }
        failure { echo "❌ Pipeline échoué" }
    }
}
