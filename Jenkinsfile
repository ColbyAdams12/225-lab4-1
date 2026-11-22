pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'
        DOCKER_IMAGE = 'cithit/adamscd5'
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/ColbyAdams12/225-lab4-1.git'
        KUBECONFIG = credentials('adamscd5-225')
    }

    stages {

        stage('Checkout') {
            steps {
                cleanWs()
                checkout([$class: 'GitSCM',
                    branches: [[name: '*/main']],
                    userRemoteConfigs: [[url: "${GITHUB_URL}"]]])
            }
        }

        // Install Python tools inside a Docker container
        stage('Install Testing Tools') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$PWD:/app" -w /app \
                      python:3.12-slim \
                      sh -c "python -m pip install --quiet flask pytest bandit pip-audit && python -m pip freeze > /dev/null"
                '''
            }
        }

        // Test the Flask application's home page
        stage('Python Tests') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$PWD:/app" -w /app \
                      python:3.12-slim \
                      sh -c "python -m pip install --quiet -r requirements.txt pytest && python -m pytest tests_main.py -v"
                '''
            }
        }

        // Scan Python code for security problems
        stage('Security Scan') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$PWD:/app" -w /app \
                      python:3.12-slim \
                      sh -c "python -m pip install --quiet bandit && python -m bandit -r main.py"
                '''
            }
        }

        // Scan dependencies for known vulnerabilities
        stage('Dependency Scan') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$PWD:/app" -w /app \
                      python:3.12-slim \
                      sh -c "python -m pip install --quiet pip-audit && python -m pip_audit -r requirements.txt"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.withRegistry(
                        'https://registry.hub.docker.com',
                        "${DOCKER_CREDENTIALS_ID}"
                    ) {
                        docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}")
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry(
                        'https://index.docker.io/v1/',
                        "${DOCKER_CREDENTIALS_ID}"
                    ) {
                        docker.image("${DOCKER_IMAGE}:${IMAGE_TAG}").push()
                    }
                }
            }
        }

        stage('Deploy to Dev Environment') {
            steps {
                script {
                    sh """
                        sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-dev.yaml
                        kubectl apply -f deployment-dev.yaml
                    """
                }
            }
        }

        stage('Check Kubernetes Cluster') {
            steps {
                script {
                    sh "kubectl get all"
                }
            }
        }
    }

    post {
        success {
            slackSend color: "good",
                message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        unstable {
            slackSend color: "warning",
                message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        failure {
            slackSend color: "danger",
                message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
    }
}
