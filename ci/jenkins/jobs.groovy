pipelineJob('devops-monitor') {
    description('Build and check the DevOps course project from its development branch.')
    definition {
        cpsScm {
            scm {
                git {
                    remote { url('https://github.com/DrorAlpern/devops-final-exam.git') }
                    branch('*/dev')
                }
            }
            scriptPath('Jenkinsfile')
            lightweight(true)
        }
    }
}
