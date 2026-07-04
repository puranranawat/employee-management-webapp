pipeline {
    agent any

    tools {
        jdk 'JDK17'
        maven 'Maven'
    }

    environment {
        SCANNER_HOME = tool 'SonarScanner'
        IMAGE_NAME = "puranranawat/employee-management:latest"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                bat 'mvn clean compile'
            }
        }

        stage('Test') {
            steps {
                bat 'mvn test'
            }
        }

        stage('Package') {
            steps {
                bat 'mvn clean package -DskipTests'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    bat """
                    "%SCANNER_HOME%\\bin\\sonar-scanner.bat" ^
                    -Dsonar.projectKey=employee-management ^
                    -Dsonar.projectName=employee-management ^
                    -Dsonar.sources=src ^
                    -Dsonar.java.binaries=target/classes
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('OWASP Dependency Check') {
            steps {
                dependencyCheck additionalArguments: '--scan .',
                odcInstallation: 'Dependency-Check'
            }
        }

        stage('Publish OWASP Report') {
            steps {
                dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME% .'
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {

                    bat '''
                    echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin
                    docker push %IMAGE_NAME%
                    '''
                }
            }
        }

        stage('Deploy Container') {
            steps {
                bat '''
                docker stop employee-management || exit 0
                docker rm employee-management || exit 0
                docker run -d --name employee-management -p 8081:8080 %IMAGE_NAME%
                '''
            }
        }
    }

    post {

        always {
            cleanWs()
        }

        success {
            echo 'Pipeline executed successfully.'
        }

        failure {
            echo 'Pipeline failed.'
        }
    }
}