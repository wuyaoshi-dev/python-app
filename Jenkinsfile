pipeline {
    agent {
        kubernetes {
            cloud 'kubernetes'
            // 临时构建 Pod：python 容器跑测试，tools 容器负责 docker 和 kubectl
            yaml '''
apiVersion: v1
kind: Pod
spec:
  # 用 jenkins ServiceAccount，kubectl 才有第 2 步授予的部署权限
  serviceAccountName: jenkins
  containers:
  - name: python
    image: python:3.12-slim
    command: ["cat"]
    tty: true
  - name: tools
    image: docker:19.03
    command: ["cat"]
    tty: true
    env:
    - name: LANG
      value: C.UTF-8
    volumeMounts:
    - name: docker-sock
      mountPath: /var/run/docker.sock
    - name: kubectl-bin
      mountPath: /usr/local/bin/kubectl
      readOnly: true
  volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
  - name: kubectl-bin
    hostPath:
      path: /usr/bin/kubectl
'''
            defaultContainer 'tools'
        }
    }

    environment {
        HARBOR     = '192.168.100.128:1180'
        IMAGE_REPO = "${HARBOR}/tlias-dev/python-app"
    }

    stages {
        stage('1. 单元测试') {
            steps {
                container('python') {
                    sh '''
                        pip install -q --no-cache-dir -r requirements-dev.txt \
                            -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
                        python -m pytest -v --junitxml=test-results.xml
                    '''
                }
            }
            post {
                always {
                    // 测试报告会显示在 Jenkins 构建页面的 Test Result 里
                    junit 'test-results.xml'
                }
            }
        }

        stage('2. 构建镜像') {
            steps {
                script {
                    env.IMAGE_TAG = "${env.BUILD_NUMBER}-${env.GIT_COMMIT.take(7)}"
                }
                echo "分支: ${env.BRANCH_NAME}，镜像标签: ${env.IMAGE_TAG}"
                sh 'docker build -t ${IMAGE_REPO}:${IMAGE_TAG} .'
            }
        }

        stage('3. 推送到 Harbor') {
            when { branch 'master' }
            steps {
                withCredentials([usernamePassword(credentialsId: 'harbor-creds',
                        usernameVariable: 'HARBOR_USER', passwordVariable: 'HARBOR_PASS')]) {
                    sh '''
                        echo "$HARBOR_PASS" | docker login ${HARBOR} -u "$HARBOR_USER" --password-stdin
                        docker push ${IMAGE_REPO}:${IMAGE_TAG}
                        docker logout ${HARBOR}
                    '''
                }
            }
        }

        stage('4. 部署到 K8s') {
            when { branch 'master' }
            steps {
                sh '''
                    sed -e "s|IMAGE_PLACEHOLDER|${IMAGE_REPO}:${IMAGE_TAG}|" \
                        -e "s|VERSION_PLACEHOLDER|${IMAGE_TAG}|" \
                        deployment.yaml > deploy-rendered.yaml
                    kubectl apply -f deploy-rendered.yaml
                    kubectl rollout status deployment/python-app --timeout=180s
                '''
            }
        }
    }

    post {
        success {
            echo "成功。master 已上线：http://192.168.100.128:30082"
        }
        failure {
            echo "失败，请查看出错的 stage"
        }
    }
}
