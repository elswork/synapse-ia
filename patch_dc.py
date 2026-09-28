path = '/home/pirate/docker/linux-voice-assistant/docker-compose.yml'
with open(path, 'r', encoding='utf-8') as f:
    dc = f.read()

target = '      - sounds_custom:/app/sounds/custom'
replacement = '''      - sounds_custom:/app/sounds/custom
      - /home/pirate/docker/linux-voice-assistant/linux_voice_assistant:/app/linux_voice_assistant'''

if '/home/pirate/docker/linux-voice-assistant/linux_voice_assistant' not in dc:
    parts = dc.split(target)
    if len(parts) >= 3:
        new_dc = parts[0] + target + parts[1] + replacement + target.join(parts[2:])
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_dc)
        print('docker-compose.yml updated successfully')
    else:
        print('Could not find second target in docker-compose.yml')
else:
    print('Already present in docker-compose.yml')
