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
            // Utiliser bash explicitement
            def testResult = sh(
                script: """
                    #!/bin/bash
                    . ${VENV_DIR}/bin/activate
                    export DATABASE_URL="${DATABASE_URL}"
                    export PYTHONPATH=$WORKSPACE/src
                    pytest --maxfail=0 --disable-warnings --cov=src --cov-report=xml -v | tee pytest-output.log
                """,
                returnStatus: true
            )

            if (testResult != 0) {
                echo "⚠️ Certains tests ont échoué, voir la console et pytest-output.log"
                currentBuild.result = "UNSTABLE"
            } else {
                echo "✅ Tous les tests unitaires ont réussi"
            }
        }

        // Archive le log
        archiveArtifacts artifacts: 'pytest-output.log', allowEmptyArchive: false
    }
}


stage('Analyse SAST avec SonarQube') {
    when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
    steps {
        echo "🔎 Analyse SAST avec SonarQube..."
        withSonarQubeEnv('sonarqube') { // Nom exact configuré dans Jenkins
            withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                script {
                    // Récupération du chemin de l'installation Jenkins du scanner
                    def scannerHome = tool 'sonar-scanner'
                    sh """
                        ${scannerHome}/bin/sonar-scanner \
                          -Dsonar.projectKey=simple-banking \
                          -Dsonar.sources=src \
                          -Dsonar.python.version=3.10 \
                          -Dsonar.python.coverage.reportPaths=coverage.xml \
                          -Dsonar.host.url=http://192.168.240.139:9000 \
                          -Dsonar.login=$SONAR_TOKEN
                    """
                }
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
                sh """
                    trivy fs --severity CRITICAL,HIGH --format json --output trivy-report.json . || true
                    trivy image --severity CRITICAL,HIGH --format json --output trivy-image-report.json ${IMAGE_NAME}:${IMAGE_TAG} || true
                """
                archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
                archiveArtifacts artifacts: 'trivy-image-report.json', allowEmptyArchive: true
            }
        }

        stage('Generate PDF, Email & Push Docker') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                echo "📄 Génération du rapport PDF + envoi email + push Docker"
                sh """
                    . ${VENV_DIR}/bin/activate
                    python3 generate_full_report.py \
                      --trivy-json trivy-report.json \
                      --trivy-image-json trivy-image-report.json \
                      --sonarqube-project simple-banking \
                      --output full_report.pdf
                """
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
                    sh '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker tag siwarmejri/simple-banking:latest $DOCKER_USER/simple-banking:latest
                        docker push $DOCKER_USER/simple-banking:latest
                        docker logout
                    '''
                }
            }
        }
    }

    post {
        always { echo "🏁 Pipeline terminé" }
        success { echo "✅ Pipeline réussi" }
        failure { echo "❌ Pipeline échoué" }
    }
}  
