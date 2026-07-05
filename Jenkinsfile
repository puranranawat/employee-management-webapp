pipeline {

    agent any

    tools {
        jdk 'JDK21'
        maven 'Maven3'
    }

    environment {
        IMAGE_NAME = "puranranawat/employee-management"
        IMAGE_TAG = "1.0"
    }

    stages {

        stage('Checkout Source') {
            steps {
                checkout scm
            }
        }

        stage('Verify Java') {
            steps {
                bat 'java -version'
            }
        }

        stage('Verify Maven') {
            steps {
                bat 'mvn -version'
            }
        }

        stage('Compile') {
            steps {
                bat 'mvn clean compile'
            }
        }

        stage('Run Unit Tests') {
            steps {
                bat 'mvn test'
            }
        }

        stage('Package Application') {
            steps {
                bat 'mvn package -DskipTests'
            }
        }

        stage('OWASP Dependency Check') {
    steps {

        bat '''
        if not exist dependency-check-report (
            mkdir dependency-check-report
        )

        C:\\dependency-check\\bin\\dependency-check.bat ^
        --project EmployeeManagement ^
        --scan . ^
        --format HTML ^
        --format XML ^
        --out dependency-check-report
        '''

    }
}

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('SonarQube') {

                        bat """
                        "${scannerHome}\\bin\\sonar-scanner.bat" ^
                        -Dsonar.projectKey=EmployeeManagement ^
                        -Dsonar.projectName=EmployeeManagement ^
                        -Dsonar.projectVersion=1.0 ^
                        -Dsonar.sources=src ^
                        -Dsonar.java.binaries=target/classes ^
                        -Dsonar.sourceEncoding=UTF-8
                        """
                    }
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

        stage('Trivy File System Scan') {
            steps {
                bat '''
                trivy fs ^
                --scanners vuln ^
                --format table ^
                .
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%IMAGE_TAG% .'
            }
        }

        stage('Trivy Docker Image Scan') {
            steps {
                bat '''
                trivy image ^
                --scanners vuln ^
                --timeout 30m ^
                %IMAGE_NAME%:%IMAGE_TAG%
                '''
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
                    docker push %IMAGE_NAME%:%IMAGE_TAG%
                    '''

                }

            }

        }

        stage('Deploy Container') {

            steps {

                bat '''
                docker stop employee-management 2>NUL
                docker rm employee-management 2>NUL

                docker run -d ^
                --name employee-management ^
                -p 8081:8080 ^
                %IMAGE_NAME%:%IMAGE_TAG%
                '''

            }

        }

    }

    post {

        success {

            echo '======================================='
            echo 'Pipeline completed successfully.'
            echo '======================================='

        }

        failure {

            echo '======================================='
            echo 'Pipeline failed.'
            echo '======================================='

        }

        always {

            cleanWs()

        }

    }

}
