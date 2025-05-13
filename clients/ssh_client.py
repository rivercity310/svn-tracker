import paramiko


class SshClient:
    def __init__(self, ssh_info, project_name: str):
        self.project_name = project_name
        self.project_path = f"/app/webapps/{project_name}"
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.client.connect(
            hostname=ssh_info['host'],
            port=ssh_info['port'],
            username=ssh_info['username'],
            password=ssh_info['password']
        )
    
    def show_project_dir(self):
        """프로젝트 디렉토리 내 파일 목록"""
        self._exec(f"cd {self.project_path} && ls -al")


    def svn_update(self, commit_list):
        """특정 파일 목록만 SVN 업데이트"""
        files = " ".join(commit['path'] for commit in commit_list)
        cmd = f"cd {self.project_path} && svn update {files}"
        self._exec(cmd)


    def build_jar(self):
        """Maven 프로젝트 빌드"""
        print("[Build Jar.....]")
        cmd = (
            f"cd {self.project_path} && "
            f"rm -Rf /home/developer/.m2/repository/architecture && "
            f"/app/maven/bin/mvn clean && "
            f"/app/maven/bin/mvn package"
        )
        self._exec(cmd)


    def tboot(self):
        cmd = (
            f"cd {self.project_path} && "
            f"tboot {self.project_name}"
        )

        self._exec(cmd)


    def tdown(self):
        cmd = (
            f"cd {self.project_path} && "
            f"tdown {self.project_name}"
        )

        self._exec(cmd)


    def close(self):
        """SSH 연결 종료"""
        self.client.close()


    def _exec(self, command: str):
        """명령어 실행 및 출력"""
        print(f"Cmd: {command}")
        _, stdout, stderr = self.client.exec_command(command)
        out = stdout.read().decode()
        err = stderr.read().decode()
        print(out)
        print(err)
        return out, err
