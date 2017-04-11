node ("python2.7") {
    try {
        // Set path for custom management tools on jenkins
        env.PATH = "${env.PATH}:/local1/svchome/jenkins-version-control/bin"
        env.PATH = "${tool 'ant 1.9.7'}/bin:${env.PATH}"
        def is_release=params.create_release
        stage ("Artifactory and Git configuration") {
            git branch: 'feature/jenkins-testing', url: 'http://zacharyc@stash.corp.alleninstitute.org/scm/aics/aicsimage.git'
        }
        stage ("Build and Publish") {
            if (is_release) {
                sh 'ant -f pipeline/build.xml clean publish-release'
            }
            else {
                sh 'ant -f pipeline/build.xml clean publish-snapshot'
            }
        }
    }
    catch(e) {
        currentBuild.result = "FAILED"
        throw e
    }
    finally {
        println currentBuild.result
    }
}