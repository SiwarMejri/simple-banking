pipeline {
    agent any

    environment {
        VENV_DIR = "${WORKSPACE}/venv"
        DATABASE_URL = "sqlite:///./test_banking.db"
        PYTHONPATH = "${WORKSPACE}/src"
        IMAGE_NAME = "simple-banking"
        IMAGE_TAG = "latest"
        SONAR_HOST_URL = "http://192.168.240.139:9000"
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
                    pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('Test') {
            steps {
                echo "🧪 Exécution des tests..."
                sh """
                    . ${VENV_DIR}/bin/activate
                    export DATABASE_URL="$DATABASE_URL"
                    export PYTHONPATH="$PYTHONPATH"
                    pytest --maxfail=1 --disable-warnings -q
                """
            }
        }

        stage('Analyse SAST avec SonarQube') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                echo "🔎 Analyse SAST avec SonarQube..."
                withSonarQubeEnv('sonarqube') {
                    withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                        sh '''
                            sonar-scanner \
                              -Dsonar.projectKey=simple-banking \
                              -Dsonar.sources=src \
                              -Dsonar.host.url=$SONAR_HOST_URL \
                              -Dsonar.token=$SONAR_TOKEN
                        '''
                    }
                }
            }
        }

        stage('Build Docker') {
            steps {
                echo '🐳 Construction de l\'image Docker...'
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Scan de vulnérabilités avec Trivy') {
            steps {
                echo "🛡️ Scan des vulnérabilités avec Trivy..."
                sh '''
                    trivy fs --severity CRITICAL,HIGH --format json --output trivy-report.json . || true
                    trivy image --severity CRITICAL,HIGH --format json --output trivy-image-report.json ${IMAGE_NAME}:${IMAGE_TAG} || true
                '''
                archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
                archiveArtifacts artifacts: 'trivy-image-report.json', allowEmptyArchive: true
            }
        }

        stage('Generate Full PDF Report') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                echo "📄 Génération du rapport PDF consolidé SonarQube + Trivy..."
                sh """
                    . ${VENV_DIR}/bin/activate
                    python3 generate_full_report.py \
                      --trivy-json trivy-report.json \
                      --trivy-image-json trivy-image-report.json \
                      --sonarqube-project simple-banking \
                      --output full_report.pdf
                """
                archiveArtifacts artifacts: 'full_report.pdf', allowEmptyArchive: false
            }
        }

        stage('Send PDF Report by Email') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                emailext(
                    subject: "📊 Rapport CI/CD - SonarQube + Trivy",
                    body: "Bonjour,\n\nLe rapport PDF consolidé du projet simple-banking est ci-joint.\n\nCordialement.",
                    to: "siwarmejri727@gmail.com",
                    attachmentsPattern: "**/full_report.pdf"
                )
            }
        }
    }

    post {
        always { echo "🏁 Pipeline terminé" }
        success { echo "✅ Pipeline réussi" }
        failure { echo "❌ Pipeline échoué" }
    }
}
