// Based on the course starter; checks use real tools and fail on errors.
pipeline {
    agent { label 'docker' }
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    environment {
        IMAGE_NAME = 'droralpern/flask-aws-monitor'
        DOCKERHUB_USERNAME = 'droralpern'
    }
    stages {
        stage('Clone Repository') {
            steps {
                checkout scm
                script {
                    env.IMAGE_TAG = sh(script: 'git rev-parse --short=12 HEAD', returnStdout: true).trim()
                }
            }
        }
        stage('Prepare Tools') {
            steps {
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install -r requirements-dev.txt
                    .venv/bin/python ci/install-tools.py
                    command -v shellcheck
                    docker version
                '''
            }
        }
        stage('Parallel Checks') {
            parallel {
                stage('Linting') {
                    steps { sh 'bash ci/check.sh lint' }
                }
                stage('Security Scan') {
                    steps { sh 'bash ci/check.sh security' }
                }
            }
        }
        stage('Python Tests') {
            steps { sh 'bash ci/check.sh test' }
        }
        stage('Offline Terraform Tests') {
            steps { sh 'bash ci/check-terraform.sh' }
        }
        stage('Validate Deployment Files') {
            steps { sh 'bash ci/validate-deployment.sh' }
        }
        stage('Build Docker Image') {
            steps { sh 'docker build --pull -t "$IMAGE_NAME:$IMAGE_TAG" app' }
        }
        stage('Scan Docker Image') {
            steps { sh 'bash ci/scan-image.sh' }
        }
        stage('Push to Docker Hub') {
            steps {
                withCredentials([file(credentialsId: 'dockerhub-config',
                    variable: 'DOCKER_CONFIG_FILE')]) {
                    sh 'bash ci/push-image.sh'
                }
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'reports/*.json,reports/*.xml', allowEmptyArchive: true
        }
        success { echo 'Checks, image build, security scan, and Docker Hub publication passed.' }
        failure { echo 'Pipeline failed. Review the failing stage and archived scan reports.' }
    }
}
