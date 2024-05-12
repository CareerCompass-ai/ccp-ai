pipeline {
    agent any
    
    stages {
        stage('Install Python') {
            steps {
                // Install Python if it's not already installed
                // sh 'sudo apt-get update && apt-get install -y python3'
                sh 'python --version'
            }
        }
        
        stage('Checkout') {
            steps {
                // Checkout the repository
                git branch: 'main', url: 'https://github.com/htnphu/ccp-ai'
            }
        }
        
        stage('Build') {
            steps {
                // Display Python version
                sh 'python --version'
                // Install Python dependencies using pip
                // sh 'pip install -r ./pkg/requirements.txt'
                sh 'docker build -t ccp-ai .'
            }
        }
        
        // stage('Push') {
        //     steps {
        //         // Push the Docker image to Docker Hub
        //         withDockerRegistry(credentialsId: 'docker-phuhtn', url: 'https://index.docker.io/v1/') {
        //             sh 'docker version'
        //             sh 'docker build -t ccp-ai .'
        //             sh 'docker tag ccp-ai phuhtn/ccp-ai'
        //             sh 'docker push phuhtn/ccp-ai'
        //         }
        //     }
        // }
        // stage('Push') {
        //   steps {
        //       // Build the Docker image
        //       sh 'docker version'
        //       sh 'docker build -t ccp-ai .'
              
        //       // Tag the Docker image
        //       sh 'docker tag ccp-ai otishan23/ccp-ai'
              
        //       // Log in to Docker registry
        //       sh 'docker login -u otishan23 -p $DOCKER_REGISTRY_TOKEN'

        //       withCredentials([string(credentialsId: 'DOCKER_REGISTRY_TOKEN', variable: 'DOCKER_REGISTRY_TOKEN')]) {
        //           sh 'docker login -u otishan23 -p $DOCKER_REGISTRY_TOKEN'
        //       }
        //       // Push the Docker image to Docker registry
        //       sh 'docker push otishan23/ccp-ai'
        //   }
        // }
        
        stage('Deploy') {
          steps {
              // Remove any existing container named 'web'
              sh 'docker rm ccp-ai -f || true'
              // Run a new container named 'web' from the Docker image, exposing port 5010
              // sh 'docker run -d --name ccp-ai -p 5010:5010 phuhtn/ccp-ai'
              // sh 'docker run ccp-ai -d --name cpp-ai -p 5010:5010'
              sh 'docker run -p 5010:5010 -d --name ccp-ai ccp-ai:latest'
          }
        }
    }
}
