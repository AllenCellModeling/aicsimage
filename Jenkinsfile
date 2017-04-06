node {
    try {
        env.PATH = "${tool 'ant 1.9.7'}/bin:${env.PATH}"
        stage ("Artifactory and Git configuration") {
            git branch: 'feature/jenkins-testing', url: 'http://zacharyc@stash.corp.alleninstitute.org/scm/aics/aicsimage.git'
        }
        stage ("Cleaning") {
            sh 'ant -f build.xml clean'
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