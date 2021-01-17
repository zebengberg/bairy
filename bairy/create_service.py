"""Create bairy.service file for systemd scripts."""

import os
import subprocess
import getpass


def get_bairy_path():
  """Get path of bairy installed by pip."""
  p = subprocess.Popen(['which', 'bairy'],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
  out, err = p.communicate()

  assert len(err) == 0
  return out.decode().rstrip()


def create_service(as_hub: bool = False):
  """Create bairy.service to be put into systemd."""

  path = get_bairy_path()
  if as_hub:
    path += ' hub'
  user = getpass.getuser()
  content = f'''
  [Unit]
  Description=Run bairy at startup
  After=network-online.target time-sync.target
  User=pi

  [Service]
  Type=oneshot
  ExecStart={path}
  User={user}

  [Install]
  WantedBy=default.target
  '''

  with open('bairy.service', 'w') as f:
    f.write(content)
  move_service()


def move_service():
  """Move bairy.service to systemd directory."""
  path = '/etc/systemd/system'
  if os.path.exists(path):
    subprocess.run(['sudo', 'mv', 'bairy.service', path])
    subprocess.run(['sudo', 'systemctl', 'enable', 'bairy.service'])
    print('Successfully moved bairy.service to systemd directory.')
  else:
    print('No systemd directory found.')
    os.remove('bairy.service')
