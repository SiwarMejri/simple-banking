pipeline {
    agent any

    environment {
        VENV_DIR       = "${WORKSPACE}/venv"
        PYTHONPATH     = "${WORKSPACE}/src"
        PIP_CACHE_DIR  = "${WORKSPACE}/.pip-cache"
        ENVIRONMENT    = "test" // test pour SQLite, dev/prod pour PostgreSQL
        DATABASE_URL   = "${env.ENVIRONMENT == 'test' ? 'sqlite:///./test_banking.db' : (env.DATABASE_URL ?: 'postgresql://postgres:admin@localhost/banking')}"
    }

    stages {

        stage('Checkout SCM') {
            steps {
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
                        sh """
                            ${tool 'sonar-scanner'}/bin/sonar-scanner \
                              -Dsonar.projectKey=simple-banking \
                              -Dsonar.sources=src \
                              -Dsonar.host.url=$SONAR_HOST_URL \
                              -Dsonar.login=$SONAR_TOKEN
                        """
                    }
                }
            }
        }

        stage('Build Docker') {
            steps {
                echo '🐳 Construction de l\'image Docker...'
                sh 'docker build -t simple-banking:latest .'
            }
        }

        stage('Scan de vulnérabilités avec Trivy') {
            steps {
                echo "🛡️ Scan des vulnérabilités avec Trivy..."
                sh """
                    # Scan du code source
                    trivy fs --severity CRITICAL,HIGH --format json --output trivy-report.json . || true
                    # Scan de l'image Docker
                    trivy image --severity CRITICAL,HIGH --format json --output trivy-image-report.json simple-banking:latest || true
                """
                archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
                archiveArtifacts artifacts: 'trivy-image-report.json', allowEmptyArchive: true
            }
        }

        stage('Push Docker Image') {
            steps {
                echo "📤 Push de l'image Docker vers DockerHub..."
                withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin

                        docker tag simple-banking:latest $DOCKER_USER/simple-banking:latest
                        docker push $DOCKER_USER/simple-banking:latest
                    '''
                }
            }
        }

        // Tu peux réactiver les étapes suivantes quand tu veux
        /*
        stage('Monitoring & Alertes') {
            steps {
                echo "📈 Vérification du monitoring et alertes..."
            }
        }

        stage('Reporting automatisé') {
            steps {
                echo "📝 Génération du reporting automatisé..."
            }
        }

        stage('Red Team / Simulation attaques (VM4)') {
            steps {
                echo "⚔️ Simulation attaques Red Team..."
            }
        }
        */
    }

    post {
        always { echo "🏁 Pipeline terminé" }
        success { echo "✅ Pipeline réussi" }
        failure { echo "❌ Pipeline échoué" }
    }
}

