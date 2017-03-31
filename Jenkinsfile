node {

    try {
        stage ("Artifactory and Git configuration") {
            // Get Artifactory server instance, defined in the Artifactory Plugin administration page.
            def server = Artifactory.server "SERVER_ID"
            git url: 'http://zacharyc@stash.corp.alleninstitute.org/scm/aics/aicsimage.git'
        }
        stage ("Testing") {
            sh 'python setup.py test'
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