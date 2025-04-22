from ftplib import FTP

class FtpClient:
    def __init__(self, host, username='', password='', passive=False):
        self.ftp = FTP(host)
        self.ftp.login(user=username, passwd=password)
        self.ftp.set_pasv(passive)

    # 현재 경로나 주어진 경로의 파일 리스트 출력
    def list_files(self, path='.'):
        print(self.ftp.nlst(path))
    
    # 파일 업로드 (같은 이름이면 덮어쓰기)
    def upload_file(self, local_path, remote_path):
        with open(local_path, "rb") as f:
            self.ftp.storbinary(f"STOR {remote_path}", f)

    # 파일 다운로드
    def download_file(self, local_path, remote_path):
        with open(local_path, "wb") as f:
            self.ftp.retrbinary(f"RETR {remote_path}", f.write)

    # 파일 삭제
    def delete_file(self, remote_path):
        self.ftp.delete(remote_path)

    # 연결 종료
    def close(self):
        self.ftp.quit()