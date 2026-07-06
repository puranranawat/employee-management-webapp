pipeline {

    agent any

    tools {
        jdk 'JDK21'
        maven 'Maven3'
    }

environment {
    IMAGE_NAME = "puranranawat/employee-management"
    IMAGE_TAG = "1.0"

    REPORT_DIR = "reports"

    ECR_REPOSITORY = "733050719452.dkr.ecr.eu-north-1.amazonaws.com/employee-management"
}
    stages {

        stage('Checkout Source') {
            steps {
                checkout scm
            }
        }

        stage('Verify Maven') {
    steps {
        bat 'mvn -version'
    }
}

stage('Verify Trivy') {
    steps {
        bat 'trivy --version'
    }
}

stage('Compile') {
    steps {
        bat 'mvn clean compile'
    }
}

        stage('Verify Java') {
            steps {
                bat 'java -version'
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

        stage('Create Reports Directory') {
    steps {
        bat '''
        if not exist reports (
            mkdir reports
        )
        '''
    }
}

stage('Trivy File System Scan') {
    steps {
        bat '''
        trivy fs ^
        --scanners vuln ^
        --format json ^
        -o reports\\trivy-fs-report.json ^
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
        --format json ^
        -o reports\\trivy-image-report.json ^
        %IMAGE_NAME%:%IMAGE_TAG%
        '''
    }
}
stage('Save Build Information') {
    steps {
        bat '''
        echo Build Number : %BUILD_NUMBER% > reports\\jenkins-build-info.txt
        echo Build ID : %BUILD_ID% >> reports\\jenkins-build-info.txt
        echo Job Name : %JOB_NAME% >> reports\\jenkins-build-info.txt
        echo Build URL : %BUILD_URL% >> reports\\jenkins-build-info.txt
        echo Workspace : %WORKSPACE% >> reports\\jenkins-build-info.txt
        '''
    }
}
        stage('AI Security Analysis') {
    steps {

        withCredentials([

            string(
                credentialsId: 'gemini-api-key',
                variable: 'GEMINI_API_KEY'
            ),

            string(
                credentialsId: 'sonar-token',
                variable: 'SONAR_TOKEN'
            )

        ]) {

            bat '''
            python scripts\\gemini_analysis.py
            '''

        }

    }
}
        
stage('AWS CLI Verification') {
    steps {
        bat '''
        aws --version
        aws sts get-caller-identity
        '''
    }
}

        stage('Login to Amazon ECR') {
    steps {

        withCredentials([
            usernamePassword(
                credentialsId: 'aws-credentials',
                usernameVariable: 'AWS_ACCESS_KEY_ID',
                passwordVariable: 'AWS_SECRET_ACCESS_KEY'
            )
        ]) {

            bat '''
            aws configure set aws_access_key_id %AWS_ACCESS_KEY_ID%
            aws configure set aws_secret_access_key %AWS_SECRET_ACCESS_KEY%
            aws configure set region eu-north-1

            aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 733050719452.dkr.ecr.eu-north-1.amazonaws.com
            '''

        }
    }
}

        stage('Push Image to Amazon ECR') {
    steps {

        bat '''
        docker tag %IMAGE_NAME%:%IMAGE_TAG% 733050719452.dkr.ecr.eu-north-1.amazonaws.com/employee-management:%IMAGE_TAG%

        docker push 733050719452.dkr.ecr.eu-north-1.amazonaws.com/employee-management:%IMAGE_TAG%
        '''

    }
}



stage('Deploy to Amazon EKS') {
    steps {

        bat '''
        aws eks update-kubeconfig --region eu-north-1 --name employee-management-cluster

        kubectl apply -f k8s/deployment.yaml

        kubectl apply -f k8s/service.yaml

        kubectl rollout status deployment/employee-management
        '''

    }
}

        
        stage('Verify Deployment') {
    steps {

        bat '''
        kubectl rollout status deployment/employee-management

        kubectl get deployments

        kubectl get pods

        kubectl get svc
        '''

    }
}



    }

post {

    success {

        archiveArtifacts artifacts: 'reports/*.*', fingerprint: true

        echo '======================================='
        echo 'Pipeline completed successfully.'
        echo '======================================='

    }

    failure {

        echo '======================================='
        echo 'Pipeline failed.'
        echo '======================================='

    }

}

}
