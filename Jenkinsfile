// author: Zach Crabtree zacharyc@alleninstitute.org

node ("python2.7")
{

    // Set path for custom management tools on jenkins
    def is_release=(params.create_release)
    echo "BUILDTYPE: " + (is_release ? "Release" : "Integration")
    env.PATH = "${tool 'ant 1.9.7'}/bin:${env.PATH}"

    try {

        stage ("Git configuration") {
            git branch: 'master', url: 'ssh://git@stash.corp.alleninstitute.org:7999/aics/aicsimage.git'
        }

        stage ("Clean") {
            sh 'ant -f pipeline/build.xml clean'
        }

        stage ("Virtual Environment Setup") {
            createVirtualEnv()
        }

        stage ("Prepare Version") {
            sh 'manage_python_build.py prepare_release_version'
        }

        stage ("Build and Publish") {
            if (is_release) {
                sh 'ant -f pipeline/build.xml publish-release'
            }
            else {
                sh 'ant -f pipeline/build.xml publish-snapshot'
            }
        }

        stage ("Test Report") {
            junit 'nosetests.xml'
        }

        stage ("Tag and Push Version") {
            if (is_release) {
                sh 'manage_python_build.py tag_and_push_version'
            }
        }

        stage ("Virtual Environment Teardown") {
            deleteVirtualEnv()
        }

        currentBuild.result = "SUCCESS"
    }
    catch(e) {
        currentBuild.result = "FAILURE"
        throw e
    }
    finally {
        notifyBuildOnSlack(currentBuild.result, is_release)
        // Email
        step([$class: 'Mailer',
              notifyEveryUnstableBuild: true,
              recipients: '!AICS_DevOps@alleninstitute.org',
              sendToIndividuals: true])

    }
}

def createVirtualEnv() {
    sh 'ant -f pipeline/build.xml venv-setup'
}

def deleteVirtualEnv() {
    sh 'ant -f pipeline/build.xml venv-destroy'
}

def notifyBuildOnSlack(String buildStatus = 'STARTED', Boolean is_release) {
    // build status of null means successful
    buildStatus =  buildStatus ?: 'SUCCESS'
    buildType = is_release ? 'RELEASE' : 'SNAPSHOT'

    // Default values
    def colorCode = '#FF0000'
    def subject = "${buildStatus} ${buildType}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'"
    def summary = "${subject} (${env.BUILD_URL})"

    // Override default values based on build status
    if (buildStatus == 'SUCCESS') {
        colorCode = is_release ? '#008000' : '#00FF00'
    } else {
        colorCode = is_release ? '#800000' : '#FF0000'
    }

    // Send notifications
    slackSend (color: colorCode, message: summary)
}