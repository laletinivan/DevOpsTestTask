import paramiko
import psycopg2


def install_postgresql(ssh, passw):
    print('Installing Postgresql...')
    stdin, stdout, stderr = ssh.exec_command('sudo apt-get update', get_pty=True)
    stdin.write(passw + '\n')
    #stdin.flush()
    #print(stderr.read())
    if stderr.read() == b'':
        print("sudo apt-get update successful")

    stdin, stdout, stderr = ssh.exec_command('sudo apt-get install -y postgresql postgresql-contrib',get_pty=True)
    stdin.write(passw + '\n')
    #stdin.flush()
    if stderr.read() == b'':
        print('PostgreSQL installed')


def configure_postgresql(ssh, passw):
    # nujno uznat version of postgresql
    stdin, stdout, stderr = ssh.exec_command("find /etc/postgresql -name 'postgresql.conf'", get_pty=True)
    path = stdout.read()
    # from bytes to str
    path = path.decode()
    if path == '' or "No such file" in path:
        print("Can't find postgresql.conf")
        exit()
    path = path.replace('\r\n', '')
    #/etc/postgresql/12/main/postgresql.conf
    stdin, stdout, stderr = ssh.exec_command("sudo sed -i \"s/#listen_addresses = \'localhost\'/listen_addresses = '*'/\" " + path, get_pty=True)
    stdin.write(passw + '\n')
    if stderr.read() == b'':
        print("postgresql.conf configured succesfully")
    stdin, stdout, stderr = ssh.exec_command("find /etc/postgresql -name 'pg_hba.conf'", get_pty=True)
    path = stdout.read()
    # from bytes to str
    path = path.decode()
    if path == '' or "No such file" in path:
        print("Can't find pg_hba.conf")
        exit()
    path = path.replace('\r\n', '')
    stdin, stdout, stderr = ssh.exec_command("sudo sed -i \"s/127.0.0.1\/32            md5/0.0.0.0\/0            trust/\" " + path, get_pty=True)
    stdin.write(passw + '\n')
    if stderr.read() == b'':
        print("pg_hba.conf configured succesfully")
    stdin, stdout, stderr = ssh.exec_command("sudo systemctl restart postgresql", get_pty=True)
    stdin.write(passw + '\n')
    if stderr.read() == b'':
        print("PostgreSQL restarted succesfully")


def test_connection(host, username, password):
    conn = psycopg2.connect(
        host=host,
        user=username,
        #password=password,
        dbname='postgres'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()
    return result[0] == 1


host = input("Host IP: ")
user = input("Username: ")
password = input("Password: ")
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=user, password=password)
except:
    print("Unable to connect to the host")
    exit()
try:
    install_postgresql(ssh, passw=password)
except:
    print("Failed to install PostgreSQL")
    exit()
try:
    configure_postgresql(ssh, passw=password)
except:
    print("Failed to configure PostgreSQL")
    exit()
try:
    test_connection(host=host, username='postgres', password=password)
    print('PostgreSQL is ready for external connections')
except:
    print('Failed to connect to PostgreSQL')
    exit()
ssh.close()
