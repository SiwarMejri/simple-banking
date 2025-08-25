pipeline { 
    agent any

    environment {
        VENV_DIR       = "${WORKSPACE}/venv"
        PYTHONPATH     = "${WORKSPACE}/src"
        PIP_CACHE_DIR  = "${WORKSPACE}/.pip-cache"
        ENVIRONMENT    = "test" // test pour SQLite, dev/prod pour PostgreSQL
        DATABASE_URL   = "sqlite:///./test_banking.db"
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials') // récupère ton token depuis Jenkins
        IMAGE_NAME     = "siwarmejri/simple-banking"
        IMAGE_TAG      = "latest"
    }

    stages {

        stage('Checkout SCM') {
            steps {
                echo "🔄 Récupération du code source depuis GitHub..."
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']], // adapte si tu utilises 'master'
                    doGenerateSubmoduleConfigurations: false,
                    extensions: [[$class: 'CleanBeforeCheckout']], // nettoie workspace avant checkout
                    userRemoteConfigs: [[
                        url: 'https://github.com/SiwarMejri/simple-banking.git',
                        credentialsId: 'github-credentials' // ID des credentials GitHub configurés dans Jenkins
                    ]]
                ])
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
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Scan de vulnérabilités avec Trivy') {
            steps {
                echo "🛡️ Scan des vulnérabilités avec Trivy..."
                sh """
                    # Scan du code source
                    trivy fs --severity CRITICAL,HIGH --format json --output trivy-report.json . || true
                    # Scan de l'image Docker
                    trivy image --severity CRITICAL,HIGH --format json --output trivy-image-report.json ${IMAGE_NAME}:${IMAGE_TAG} || true
                """
                archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
                archiveArtifacts artifacts: 'trivy-image-report.json', allowEmptyArchive: true
            }
        }

        stage('Push Docker Image') {
            steps {
                echo '📤 Push de l\'image Docker vers DockerHub...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials',
                                                 usernameVariable: 'DOCKER_USER',
                                                 passwordVariable: 'DOCKER_PASS')]) {
                    // Connexion sécurisée à DockerHub
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'

                    // Tag et push de l'image
                    sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} $DOCKER_USER/${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker push $DOCKER_USER/${IMAGE_NAME}:${IMAGE_TAG}"

                    // Déconnexion pour sécurité
                    sh 'docker logout'
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

