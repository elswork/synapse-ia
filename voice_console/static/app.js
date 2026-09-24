/**
 * ARQUÍMEDES // CONSOLA DE VOZ SOBERANA
 * Frontend Controller & Web Audio Visualizer
 */

(function () {
  'use strict';

  // --- DOM Elements ---
  const statusPill = document.getElementById('statusPill');
  const statusText = document.getElementById('statusText');
  const btnSettingsToggle = document.getElementById('btnSettingsToggle');
  const btnSettingsClose = document.getElementById('btnSettingsClose');
  const settingsDrawer = document.getElementById('settingsDrawer');
  const drawerOverlay = document.getElementById('drawerOverlay');

  const canvas = document.getElementById('waveformCanvas');
  const ctx = canvas.getContext('2d');
  const btnPushToTalk = document.getElementById('btnPushToTalk');
  const micHint = document.getElementById('micHint');
  const chkHandsFree = document.getElementById('chkHandsFree');

  const liveSpeechCard = document.getElementById('liveSpeechCard');
  const liveSpeakerTag = document.getElementById('liveSpeakerTag');
  const liveSpeechText = document.getElementById('liveSpeechText');
  const transcriptLog = document.getElementById('transcriptLog');
  const btnClearTranscript = document.getElementById('btnClearTranscript');

  const textPromptInput = document.getElementById('textPromptInput');
  const btnSendText = document.getElementById('btnSendText');

  // Settings Elements
  const inputApiKey = document.getElementById('inputApiKey');
  const btnToggleKeyVis = document.getElementById('btnToggleKeyVis');
  const selectVoice = document.getElementById('selectVoice');
  const selectModel = document.getElementById('selectModel');
  const rangeVolume = document.getElementById('rangeVolume');
  const lblVolume = document.getElementById('lblVolume');
  const rangeSpeechRate = document.getElementById('rangeSpeechRate');
  const lblRate = document.getElementById('lblRate');
  const btnSaveSettings = document.getElementById('btnSaveSettings');

  // --- Audio & State Variables ---
  let audioCtx = null;
  let analyser = null;
  let micStream = null;
  let micSourceNode = null;
  let currentAudioSource = null;
  let dataArray = null;

  let isListening = false;
  let isThinking = false;
  let isSpeaking = false;
  let recognition = null;
  let currentTranscript = '';
  let spaceKeyPressed = false;

  // Settings object
  const settings = {
    apiKey: localStorage.getItem('anticitera_gemini_key') || '',
    voice: localStorage.getItem('anticitera_voice') || 'Charon',
    model: (function() {
      const stored = localStorage.getItem('anticitera_model');
      if (!stored || stored.includes('2.') || stored.includes('1.5')) {
        localStorage.setItem('anticitera_model', 'gemini-3.8-flash');
        return 'gemini-3.8-flash';
      }
      return stored;
    })(),
    volume: parseFloat(localStorage.getItem('anticitera_volume') || '1.0'),
    speechRate: parseFloat(localStorage.getItem('anticitera_rate') || '1.0'),
    handsFree: localStorage.getItem('anticitera_handsfree') === 'true'
  };

  // --- Initialize Settings in UI ---
  inputApiKey.value = settings.apiKey;
  selectVoice.value = settings.voice;
  selectModel.value = settings.model;
  rangeVolume.value = settings.volume;
  lblVolume.textContent = Math.round(settings.volume * 100) + '%';
  rangeSpeechRate.value = settings.speechRate;
  lblRate.textContent = settings.speechRate.toFixed(1) + 'x';
  chkHandsFree.checked = settings.handsFree;

  // --- Setup Web Audio Context ---
  function initAudioContext() {
    if (!audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      audioCtx = new AudioContextClass();
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 128;
      analyser.smoothingTimeConstant = 0.8;
      const bufferLength = analyser.frequencyBinCount;
      dataArray = new Uint8Array(bufferLength);
    }
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
  }

  // --- Canvas Visualizer Loop ---
  let animId = null;
  function renderVisualizer() {
    animId = requestAnimationFrame(renderVisualizer);

    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;

    ctx.clearRect(0, 0, width, height);

    let avgFrequency = 0;
    if (analyser && dataArray) {
      analyser.getByteFrequencyData(dataArray);
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        sum += dataArray[i];
      }
      avgFrequency = sum / dataArray.length;
    }

    const scale = avgFrequency / 255; // 0.0 to 1.0

    // Dynamic Colors based on State
    let primaryGlow = 'rgba(0, 240, 255, ';
    let coreColor = '#00f0ff';
    if (isListening) {
      primaryGlow = 'rgba(255, 51, 102, ';
      coreColor = '#ff3366';
    } else if (isSpeaking) {
      primaryGlow = 'rgba(197, 160, 89, ';
      coreColor = '#c5a059';
    } else if (isThinking) {
      primaryGlow = 'rgba(255, 170, 0, ';
      coreColor = '#ffaa00';
    }

    // Outer Aura
    const baseRadius = 55 + scale * 45;
    const auraGradient = ctx.createRadialGradient(centerX, centerY, baseRadius * 0.4, centerX, centerY, baseRadius * 1.8);
    auraGradient.addColorStop(0, primaryGlow + '0.45)');
    auraGradient.addColorStop(0.5, primaryGlow + '0.15)');
    auraGradient.addColorStop(1, 'transparent');

    ctx.fillStyle = auraGradient;
    ctx.beginPath();
    ctx.arc(centerX, centerY, baseRadius * 1.8, 0, Math.PI * 2);
    ctx.fill();

    // Concentric Gear Frequency Waves
    const bars = 48;
    const step = (Math.PI * 2) / bars;

    ctx.save();
    ctx.translate(centerX, centerY);

    for (let i = 0; i < bars; i++) {
      const angle = i * step;
      let val = 0;
      if (dataArray) {
        val = dataArray[i % dataArray.length] / 255;
      }
      const barLen = 10 + val * 55;

      const x1 = Math.cos(angle) * baseRadius;
      const y1 = Math.sin(angle) * baseRadius;
      const x2 = Math.cos(angle) * (baseRadius + barLen);
      const y2 = Math.sin(angle) * (baseRadius + barLen);

      ctx.strokeStyle = primaryGlow + (0.3 + val * 0.7).toFixed(2) + ')';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }

    // Inner Glowing Core
    ctx.beginPath();
    ctx.arc(0, 0, baseRadius * 0.75, 0, Math.PI * 2);
    ctx.fillStyle = '#0a101d';
    ctx.fill();
    ctx.strokeStyle = coreColor;
    ctx.lineWidth = 2;
    ctx.stroke();

    // Antikythera Crosshair
    ctx.strokeStyle = primaryGlow + '0.5)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-15, 0); ctx.lineTo(15, 0);
    ctx.moveTo(0, -15); ctx.lineTo(0, 15);
    ctx.stroke();

    ctx.restore();
  }

  // --- Speech Recognition Setup ---
  function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      logMessage('Sistema', 'El navegador no tiene soporte nativo de Web Speech API. Puedes interactuar mediante el campo de texto inferior.', 'system');
      return;
    }

    recognition = new SpeechRecognition();
    recognition.lang = 'es-ES';
    recognition.continuous = settings.handsFree;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setInterfaceState('listening');
    };

    recognition.onresult = (event) => {
      let interim = '';
      let final = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript;
        } else {
          interim += transcript;
        }
      }

      currentTranscript = final || interim;
      liveSpeakerTag.innerHTML = '<span class="badge-agent">COO Eloy</span><span class="live-tag">CAPTANDO...</span>';
      liveSpeechText.textContent = `"${currentTranscript}"`;

      if (final && final.trim().length > 1) {
        handleUserSpeech(final.trim());
      }
    };

    recognition.onerror = (event) => {
      console.warn('SpeechRecognition error:', event.error);
      if (event.error !== 'no-speech') {
        setInterfaceState('ready');
      }
    };

    recognition.onend = () => {
      if (isListening) {
        if (settings.handsFree && !isThinking && !isSpeaking) {
          // Restart continuous listening
          try {
            recognition.start();
          } catch (e) {
            setInterfaceState('ready');
          }
        } else {
          setInterfaceState('ready');
        }
      }
    };
  }

  // --- State Controller ---
  function setInterfaceState(state) {
    statusPill.className = 'status-indicator';
    btnPushToTalk.classList.remove('active');

    if (state === 'ready') {
      isListening = false;
      isThinking = false;
      isSpeaking = false;
      statusText.textContent = 'ENLACE LISTO';
      micHint.textContent = settings.handsFree ? 'Modo Manos Libres Activo' : 'Mantén pulsado [ESPACIO] o pulsa para hablar';
    } else if (state === 'listening') {
      isListening = true;
      isThinking = false;
      isSpeaking = false;
      statusPill.classList.add('listening');
      btnPushToTalk.classList.add('active');
      statusText.textContent = 'ESCUCHANDO AL COO...';
      micHint.textContent = 'Suelto o para cuando termines de hablar';
    } else if (state === 'thinking') {
      isListening = false;
      isThinking = true;
      isSpeaking = false;
      statusText.textContent = 'ARQUÍMEDES DELIBERANDO...';
      liveSpeakerTag.innerHTML = '<span class="badge-agent" style="color:var(--accent-gold);">Arquímedes CEA</span><span class="live-tag" style="border-color:var(--accent-gold);color:var(--accent-gold);">PROCESANDO</span>';
      liveSpeechText.textContent = 'Consultando los engranajes de la red...';
    } else if (state === 'speaking') {
      isListening = false;
      isThinking = false;
      isSpeaking = true;
      statusPill.classList.add('speaking');
      statusText.textContent = 'TRANSMITIENDO VOZ...';
    }
  }

  // --- Start & Stop Microphone Stream ---
  async function startListening() {
    initAudioContext();
    if (isThinking || isSpeaking) return;

    try {
      if (!micStream) {
        micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        micSourceNode = audioCtx.createMediaStreamSource(micStream);
        micSourceNode.connect(analyser);
      }
    } catch (err) {
      console.warn('Mic access error for visualizer:', err);
    }

    if (recognition) {
      try {
        recognition.start();
      } catch (e) {
        // Already started
      }
    }
    setInterfaceState('listening');
  }

  function stopListening() {
    if (!isListening) return;
    if (recognition) {
      try {
        recognition.stop();
      } catch (e) {}
    }
    if (currentTranscript && currentTranscript.trim().length > 1) {
      handleUserSpeech(currentTranscript.trim());
      currentTranscript = '';
    } else {
      setInterfaceState('ready');
    }
  }

  // --- Dispatch User Speech to Backend ---
  async function handleUserSpeech(text) {
    if (!text || text.length < 1) return;
    setInterfaceState('thinking');
    logMessage('COO Eloy', text, 'user');

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-gemini-api-key': settings.apiKey
        },
        body: JSON.stringify({
          message: text,
          persona: settings.persona || 'arquimedes',
          api_key: settings.apiKey,
          voice: settings.voice,
          model: settings.model
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Error en la respuesta del servidor');
      }

      // Display response in bitácora
      const agentDisplayName = data.persona === 'athena' ? 'Athena (CAO)' : 'Arquímedes (CEA)';
      logMessage(agentDisplayName, data.text, 'agent');
      liveSpeakerTag.innerHTML = `<span class="badge-agent" style="color:${data.persona === 'athena' ? 'var(--accent-cyan)' : 'var(--accent-gold)'};">${agentDisplayName}</span><span class="live-tag">EMISIÓN</span>`;
      liveSpeechText.textContent = `"${data.text}"`;

      // Si es un error de API Key bloqueada, abrir los ajustes automáticamente
      if (data.is_api_key_error) {
        setTimeout(() => {
          settingsDrawer.classList.add('open');
          drawerOverlay.classList.add('active');
          inputApiKey.focus();
        }, 1200);
      }

      // Play Audio Response
      if (data.audio && !data.fallback_tts) {
        await playBase64Audio(data.audio, data.mime_type || 'audio/wav');
      } else {
        // Fallback to Browser Neural TTS
        speakWithBrowserTTS(data.text);
      }

    } catch (err) {
      console.error('Chat error:', err);
      logMessage('Error de Enlace', err.message, 'system');
      liveSpeechText.textContent = `Fallo de transmisión: ${err.message}`;
      setInterfaceState('ready');
    }
  }

  // --- Audio Output: Base64 Decoded Playback ---
  async function playBase64Audio(base64Data, mimeType) {
    initAudioContext();
    setInterfaceState('speaking');

    try {
      const binaryString = window.atob(base64Data);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      const audioBuffer = await audioCtx.decodeAudioData(bytes.buffer);
      
      if (currentAudioSource) {
        try { currentAudioSource.stop(); } catch (e) {}
      }

      currentAudioSource = audioCtx.createBufferSource();
      currentAudioSource.buffer = audioBuffer;

      // Gain Node for Volume Control
      const gainNode = audioCtx.createGain();
      gainNode.gain.value = settings.volume;

      // Connect: Buffer -> Gain -> Analyser -> Speakers
      currentAudioSource.connect(gainNode);
      gainNode.connect(analyser);
      analyser.connect(audioCtx.destination);

      currentAudioSource.onended = () => {
        setInterfaceState('ready');
        if (settings.handsFree) {
          setTimeout(startListening, 600);
        }
      };

      currentAudioSource.start(0);

    } catch (e) {
      console.warn('Error decodificando audio nativo de Gemini, usando TTS de navegador:', e);
      speakWithBrowserTTS(liveSpeechText.textContent);
    }
  }

  // --- Fallback TTS: Web SpeechSynthesis ---
  function speakWithBrowserTTS(text) {
    if (!('speechSynthesis' in window)) {
      setInterfaceState('ready');
      return;
    }

    window.speechSynthesis.cancel();
    setInterfaceState('speaking');

    const cleanText = text.replace(/[*#_~`]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = 'es-ES';
    utterance.rate = settings.speechRate;
    utterance.pitch = settings.voice === 'Aoede' ? 1.05 : 0.88; // Deep voice for Archimedes
    utterance.volume = settings.volume;

    // Pick best available Spanish voice
    const voices = window.speechSynthesis.getVoices();
    const esVoice = voices.find(v => v.lang.startsWith('es') && (v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Jorge') || v.name.includes('Pablo'))) ||
                    voices.find(v => v.lang.startsWith('es'));
    if (esVoice) {
      utterance.voice = esVoice;
    }

    utterance.onend = () => {
      setInterfaceState('ready');
      if (settings.handsFree) {
        setTimeout(startListening, 600);
      }
    };

    utterance.onerror = () => {
      setInterfaceState('ready');
    };

    window.speechSynthesis.speak(utterance);
  }

  // --- Transcript Logger ---
  function logMessage(author, message, type) {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}-entry`;

    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

    entry.innerHTML = `
      <div class="log-author">
        <span>${author}</span>
        <span class="log-timestamp">${timeStr}</span>
      </div>
      <div class="log-text">${escapeHtml(message)}</div>
    `;

    transcriptLog.appendChild(entry);
    transcriptLog.scrollTop = transcriptLog.scrollHeight;
  }

  function escapeHtml(str) {
    return str.replace(/[&<>'"]/g, 
      tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
  }

  // --- Event Listeners ---

  // Push-to-Talk Mouse / Touch
  btnPushToTalk.addEventListener('mousedown', (e) => {
    e.preventDefault();
    if (!settings.handsFree) {
      startListening();
    }
  });

  window.addEventListener('mouseup', () => {
    if (!settings.handsFree && isListening && !spaceKeyPressed) {
      stopListening();
    }
  });

  btnPushToTalk.addEventListener('touchstart', (e) => {
    e.preventDefault();
    if (!settings.handsFree) {
      startListening();
    }
  });

  btnPushToTalk.addEventListener('touchend', (e) => {
    e.preventDefault();
    if (!settings.handsFree && isListening) {
      stopListening();
    }
  });

  // Push-to-Talk via Keyboard (Spacebar)
  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && !spaceKeyPressed && document.activeElement !== textPromptInput && document.activeElement !== inputApiKey) {
      e.preventDefault();
      spaceKeyPressed = true;
      if (!settings.handsFree) {
        startListening();
      }
    }
  });

  window.addEventListener('keyup', (e) => {
    if (e.code === 'Space' && spaceKeyPressed) {
      e.preventDefault();
      spaceKeyPressed = false;
      if (!settings.handsFree) {
        stopListening();
      }
    }
  });

  // Hands Free Toggle
  chkHandsFree.addEventListener('change', () => {
    settings.handsFree = chkHandsFree.checked;
    localStorage.setItem('anticitera_handsfree', settings.handsFree);
    if (settings.handsFree) {
      startListening();
    } else {
      stopListening();
      setInterfaceState('ready');
    }
  });

  // Text Fallback Submit
  btnSendText.addEventListener('click', () => {
    const txt = textPromptInput.value.trim();
    if (txt) {
      handleUserSpeech(txt);
      textPromptInput.value = '';
    }
  });

  textPromptInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      const txt = textPromptInput.value.trim();
      if (txt) {
        handleUserSpeech(txt);
        textPromptInput.value = '';
      }
    }
  });

  // Clear Transcript
  btnClearTranscript.addEventListener('click', () => {
    transcriptLog.innerHTML = `
      <div class="log-entry system-entry">
        <span class="system-msg">Bitácora purgada. Canal de escucha listo.</span>
      </div>
    `;
  });

  // Drawer Toggles
  btnSettingsToggle.addEventListener('click', () => {
    settingsDrawer.classList.add('open');
    drawerOverlay.classList.add('active');
  });

  function closeDrawer() {
    settingsDrawer.classList.remove('open');
    drawerOverlay.classList.remove('active');
  }

  btnSettingsClose.addEventListener('click', closeDrawer);
  drawerOverlay.addEventListener('click', closeDrawer);

  btnToggleKeyVis.addEventListener('click', () => {
    inputApiKey.type = inputApiKey.type === 'password' ? 'text' : 'password';
  });

  // Save Settings
  btnSaveSettings.addEventListener('click', () => {
    settings.apiKey = inputApiKey.value.trim();
    settings.voice = selectVoice.value;
    settings.model = selectModel.value;
    settings.volume = parseFloat(rangeVolume.value);
    settings.speechRate = parseFloat(rangeSpeechRate.value);

    localStorage.setItem('anticitera_gemini_key', settings.apiKey);
    localStorage.setItem('anticitera_voice', settings.voice);
    localStorage.setItem('anticitera_model', settings.model);
    localStorage.setItem('anticitera_volume', settings.volume);
    localStorage.setItem('anticitera_rate', settings.speechRate);

    closeDrawer();
    logMessage('Sistema', 'Parámetros del Oráculo guardados satisfactoriamente.', 'system');
  });

  rangeVolume.addEventListener('input', () => {
    lblVolume.textContent = Math.round(rangeVolume.value * 100) + '%';
  });

  rangeSpeechRate.addEventListener('input', () => {
    lblRate.textContent = parseFloat(rangeSpeechRate.value).toFixed(1) + 'x';
  });

  // Pre-load voices for SpeechSynthesis
  if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => {
      window.speechSynthesis.getVoices();
    };
  }

  // --- Initial Start ---
  setupSpeechRecognition();
  renderVisualizer();

  // Check backend server status
  fetch('/api/status')
    .then(r => r.json())
    .then(data => {
      console.log('Status de consola:', data);
      if (!data.has_env_key && !settings.apiKey) {
        logMessage('Aviso de Configuración', 'No se ha detectado GEMINI_API_KEY en el servidor. Abre los ajustes (engranaje superior) para ingresar tu clave de AI Studio si es necesario.', 'system');
      }
    })
    .catch(err => {
      console.warn('Backend status check:', err);
    });

})();
