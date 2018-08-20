import time, sys
import paramiko
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool

while True:
    username = raw_input('Enter username: ')
    password = raw_input('Enter password: ')
    hosts = raw_input('Enter the list of devices [host1, host2]: ')
    commands = raw_input('Enter the list of commands [command1, command2]: ')
    print '\n' + ('~' * 80)
    answer = raw_input('Are you sure you wish to continue? [Yes/no]: ')
    if answer.strip().upper() == 'NO':
        sys.exit(1)
    elif answer.strip().upper() == 'YES':
        break
    else:
        pass

hosts = [i.strip() for i in hosts.split(',')]
commands = [i.strip() for i in commands.split(',')]


def get_switch_info(args):
    host, commands = args

    ssh_client = {
        'hostname': host,
        'username': username,
        'password': password,
        'port': 22
    }

    conn = paramiko.SSHClient()
    conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        conn.connect(**ssh_client)
    except paramiko.AuthenticationException:
        print '** ERROR ** Authentication failure to host {}.'.format(host)
    except paramiko.BadHostKeyException:
        print '** ERROR ** The host Key is invalid for host {}.'.format(host)
    except EOFError:
        print '** ERROR ** End of file while attempting host {}.'.format(host)
    except paramiko.SSHException:
        print '** ERROR ** Unable to establish SSH connection to host {}!'.format(host)
    except Exception as unknown_error:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print '**ERROR: Unknown Error, Host: {}, Line: {}, Debug: {}.'.format(host, exc_tb.tb_lineno, unknown_error)
    else:
        print 'Connected to {}...'.format(host)
        with open('{}.txt'.format(host), 'w') as f:
            for command in commands:
                try:
                    stdin, stdout, stderr = conn.exec_command('{}\n'.format(command))
                    stdout.channel.recv_exit_status()
                    time.sleep(1)
                    output = stdout.read()
                    f.write('> {}\n'.format(command))
                    f.write(output)
                    f.write('\n{}\n'.format('~' * 80))
                except IOError:
                    print '** IOError ** Unable to execute command "{}" due to connection or device issues on host {}.'.format(command, host)
                except paramiko.SSHException:
                    print '** SSH Error ** Unable to connect to SSH on host{}!'.format(host)
                except Exception as unknown_error:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    print '** Unknown Error ** Host: {}, Line: {}, Debug: {}.'.format(host, exc_tb.tb_lineno, unknown_error)
        
        conn.close()
        print 'Disconnected from {}.'.format(host)

processes = []
for h in hosts:
    processes.append((h, commands))

pool = ThreadPool()
pool.map(get_switch_info, processes)
pool.close()
pool.join()
