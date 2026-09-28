path = '/usr/local/lib/python3.10/site-packages/wyoming_satellite/__main__.py'
with open(path, 'r') as f:
    text = f.read()

target = '        if Describe.is_type(event.type):'
addition = '''        if event.type == "ping":
            await self.write_event(Event(type="pong", data=event.data))
            return True

'''

if 'if event.type == "ping":' in text:
    print('Already patched!')
elif target in text:
    text = text.replace(target, addition + target)
    with open(path, 'w') as f:
        f.write(text)
    print('Successfully patched __main__.py!')
else:
    print('Target not found in __main__.py!')
