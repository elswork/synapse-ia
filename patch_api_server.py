import urllib.request, json, base64

patch_code = '''
path = '/host/home/pirate/docker/linux-voice-assistant/linux_voice_assistant/api_server.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """            # Read preamble, which should always 0x00
            if (preamble := self._read_varuint()) != 0x00:
                _LOGGER.error("Incorrect preamble: %s", preamble)
                return"""

replacement = """            # Read preamble, which should always 0x00
            if (preamble := self._read_varuint()) != 0x00:
                _LOGGER.error("Incorrect preamble: %s (clearing corrupted buffer)", preamble)
                self._buffer = b""
                self._buffer_len = 0
                return"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("api_server.py patched successfully")
else:
    print("target already patched or not found")
'''

b64 = base64.b64encode(patch_code.encode()).decode()

req = urllib.request.Request(
    'http://192.168.1.75:5051/system/run',
    data=json.dumps({'command': f'echo "{b64}" | base64 -d > /host/tmp/patch.py && chroot /host python3 /tmp/patch.py'}).encode(),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req) as resp:
    print(resp.read().decode())
