import os

# 1. Patch api_server.py
api_server_path = '/home/pirate/docker/linux-voice-assistant/linux_voice_assistant/api_server.py'
with open(api_server_path, 'r', encoding='utf-8') as f:
    api_server = f.read()

t1 = """            # Read preamble, which should always 0x00
            if (preamble := self._read_varuint()) != 0x00:
                _LOGGER.error("Incorrect preamble: %s", preamble)
                return"""
r1 = """            # Read preamble, which should always 0x00
            if (preamble := self._read_varuint()) != 0x00:
                _LOGGER.error("Incorrect preamble: %s (clearing corrupted buffer)", preamble)
                self._buffer = b""
                self._buffer_len = 0
                return"""

t2 = """            if (length := self._read_varuint()) == -1:
                _LOGGER.error("Incorrect length: %s", length)
                return"""
r2 = """            if (length := self._read_varuint()) == -1:
                _LOGGER.error("Incorrect length: %s (clearing corrupted buffer)", length)
                self._buffer = b""
                self._buffer_len = 0
                return"""

t3 = """            if (msg_type := self._read_varuint()) == -1:
                _LOGGER.error("Incorrect message type: %s", msg_type)
                return"""
r3 = """            if (msg_type := self._read_varuint()) == -1:
                _LOGGER.error("Incorrect message type: %s (clearing corrupted buffer)", msg_type)
                self._buffer = b""
                self._buffer_len = 0
                return"""

if t1 in api_server:
    api_server = api_server.replace(t1, r1, 1).replace(t2, r2, 1).replace(t3, r3, 1)
    with open(api_server_path, 'w', encoding='utf-8') as f:
        f.write(api_server)
    print("api_server.py patched successfully")
else:
    print("api_server.py already patched or target not found")

# 2. Patch wake_word.py
wake_word_path = '/home/pirate/docker/linux-voice-assistant/linux_voice_assistant/wake_word.py'
with open(wake_word_path, 'r', encoding='utf-8') as f:
    ww = f.read()

t_ww = """    for wake_word_dir in wake_word_dirs:"""
r_ww = """    custom_ww_dir = Path("/app/wakewords/custom")
    if custom_ww_dir.exists() and custom_ww_dir not in wake_word_dirs:
        wake_word_dirs.append(custom_ww_dir)

    for wake_word_dir in wake_word_dirs:"""

if t_ww in ww and "custom_ww_dir = Path" not in ww:
    ww = ww.replace(t_ww, r_ww, 1)
    with open(wake_word_path, 'w', encoding='utf-8') as f:
        f.write(ww)
    print("wake_word.py patched successfully")
else:
    print("wake_word.py already patched or target not found")

# 3. Patch __main__.py
main_path = '/home/pirate/docker/linux-voice-assistant/linux_voice_assistant/__main__.py'
with open(main_path, 'r', encoding='utf-8') as f:
    main_code = f.read()

t_oww_append = """    oww_dir = _WAKEWORDS_DIR / "openWakeWord"
    if oww_dir not in wake_word_dirs:
        wake_word_dirs.append(oww_dir)"""

r_oww_append = """    oww_dir = _WAKEWORDS_DIR / "openWakeWord"
    if oww_dir not in wake_word_dirs:
        wake_word_dirs.append(oww_dir)

    custom_dir = _WAKEWORDS_DIR / "custom"
    if custom_dir not in wake_word_dirs:
        wake_word_dirs.append(custom_dir)"""

if t_oww_append in main_code and "custom_dir = _WAKEWORDS_DIR" not in main_code:
    main_code = main_code.replace(t_oww_append, r_oww_append, 1)

t_ww_loop = """                        if isinstance(wake_word, MicroWakeWord):
                            # No debugging when no detection
                            wake_word.debug_probabilities = False

                            # set microWakeWord cutoff
                            wake_word.probability_cutoff = threshold

                            for micro_input in micro_inputs:
                                if wake_word.process_streaming(micro_input):
                                    wake_word.debug_probabilities = True
                                    activated = True
                        elif isinstance(wake_word, OpenWakeWord):
                            for oww_input in oww_inputs:
                                for prob in wake_word.process_streaming(oww_input):
                                    if prob > threshold:
                                        _LOGGER.debug("Wake word '%s' activated (probability %.3f exceeded threshold %.3f)", wake_word.wake_word, prob, threshold)  # type: ignore[attr-defined]
                                        activated = True"""

r_ww_loop = """                        if isinstance(wake_word, MicroWakeWord):
                            wake_word.probability_cutoff = threshold
                            for micro_input in micro_inputs:
                                prob = wake_word.process_streaming_prob(micro_input)
                                if prob > 0.2:
                                    _LOGGER.debug("Wake word '%s' probability: %.3f (threshold: %.3f)", wake_word.wake_word, prob, threshold)
                                if prob > threshold:
                                    _LOGGER.info("Wake word '%s' activated! (probability %.3f exceeded threshold %.3f)", wake_word.wake_word, prob, threshold)
                                    activated = True
                        elif isinstance(wake_word, OpenWakeWord):
                            for oww_input in oww_inputs:
                                for prob in wake_word.process_streaming(oww_input):
                                    if prob > 0.2:
                                        _LOGGER.debug("Wake word '%s' probability: %.3f (threshold: %.3f)", wake_word.wake_word, prob, threshold)
                                    if prob > threshold:
                                        _LOGGER.info("Wake word '%s' activated! (probability %.3f exceeded threshold %.3f)", wake_word.wake_word, prob, threshold)
                                        activated = True"""

if t_ww_loop in main_code:
    main_code = main_code.replace(t_ww_loop, r_ww_loop, 1)

with open(main_path, 'w', encoding='utf-8') as f:
    f.write(main_code)
print("__main__.py patched successfully")
