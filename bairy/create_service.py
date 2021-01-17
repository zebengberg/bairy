"""Create bairy.service file for systemd scripts."""

import subprocess
import getpass


def get_bairy_path():
  """Get path of bairy installed by pip."""
  p = subprocess.Popen(['which', 'bairy'],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = p.communicate()

  assert len(err) == 0
  return out.decode().rstrip()


def create_service_file():
  """Create bairy.service to be put into systemd."""

  path = get_bairy_path()
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
