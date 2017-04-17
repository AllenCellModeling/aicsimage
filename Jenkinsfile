node ("python2.7")
{

    // Set path for custom management tools on jenkins
    env.PATH = "${env.PATH}:/local1/svchome/jenkins-scripts/bin"
    echo "${env.PATH}"
    def is_release=(params.create_release)
    echo "BUILDTYPE: " + (is_release ? "Release" : "Integration")

    try {

        stage ("Git configuration") {
            git branch: 'feature/jenkins-testing', url: 'http://zacharyc@stash.corp.alleninstitute.org/scm/aics/aicsimage.git'
        }

        stage ("Prepare Version") {
            sh 'manage_python_build.py prepare_release_version'
        }

        stage ("Build and Publish") {
            env.PATH = "${tool 'ant 1.9.7'}/bin:${env.PATH}"
            if (is_release) {
                sh 'ant -f pipeline/build.xml clean publish-release'
            }
            else {
                sh 'ant -f pipeline/build.xml clean publish-snapshot'
            }
        }

        stage ("Tag and Push Version") {
            sh 'manage_python_build.py tag_and_push_version'
        }
    }
    catch(e) {
        currentBuild.result = "FAILED"
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

def notifyBuildOnSlack(String buildStatus = 'STARTED', Boolean is_release) {
    // build status of null means successful
    buildStatus =  buildStatus ?: 'SUCCESSFUL'
    buildType = is_release ? 'RELEASE' : 'SNAPSHOT'

    // Default values
    def colorName = 'RED'
    def colorCode = '#FF0000'
    def subject = "${buildStatus} ${buildType}: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]'"
    def summary = "${subject} (${env.BUILD_URL})"

    // Override default values based on build status
    if (buildStatus == 'SUCCESSFUL') {
        color = 'GREEN'
        // colorCode = '#00FF00'
        colorCode = is_release ? '#008000' : '#00FF00'
    } else {
        color = 'RED'
        // colorCode = '#FF0000'
        colorCode = is_release ? '#800000' : '#FF0000'
    }

    // Send notifications
    slackSend (color: colorCode, message: summary)
}