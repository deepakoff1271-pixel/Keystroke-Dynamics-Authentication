(() => {
  const passwordSelect = document.getElementById('passwordSelect');
  const sessionType = document.getElementById('sessionType');
  const participantId = document.getElementById('participantId');
  const startButton = document.getElementById('startButton');
  const typingField = document.getElementById('typingField');
  const targetPassword = document.getElementById('targetPassword');
  const eventLog = document.getElementById('eventLog');
  const statusBadge = document.getElementById('statusBadge');

  if (!passwordSelect || !typingField) {
    return;
  }

  let active = false;
  let rawEvents = [];
  let currentPassword = passwordSelect.value;

  const setStatus = (text, state) => {
    statusBadge.textContent = text;
    statusBadge.className = `status-badge ${state}`;
  };

  const logLine = (message) => {
    eventLog.textContent = `${message}\n${eventLog.textContent}`.trim();
  };

  const updateTarget = () => {
    currentPassword = passwordSelect.value;
    targetPassword.textContent = currentPassword;
  };

  const resetCapture = () => {
    rawEvents = [];
    typingField.value = '';
    eventLog.textContent = '';
    active = true;
    typingField.focus();
    setStatus('Capturing', 'active');
    logLine('Capture started. Type the password and press Enter.');
  };

  const buildMetrics = (events) => {
    const presses = events.filter((event) => event.type === 'keydown');
    const releases = events.filter((event) => event.type === 'keyup');
    if (!presses.length || presses.length !== releases.length) {
      return null;
    }

    const metrics = [];
    for (let index = 0; index < presses.length; index += 1) {
      const pressTime = presses[index].timestamp;
      const releaseTime = releases[index].timestamp;
      const holdTime = Math.max(releaseTime - pressTime, 0);
      const pressToPress = index === 0 ? 0 : Math.max(pressTime - presses[index - 1].timestamp, 0);
      const releaseToPress = index === 0 ? 0 : pressTime - releases[index - 1].timestamp;
      metrics.push(pressToPress, releaseToPress, holdTime);
    }
    metrics.push(metrics[metrics.length - 1] || 0);
    return metrics;
  };

  const submitCapture = async () => {
    const metrics = buildMetrics(rawEvents);
    if (!metrics) {
      logLine('Capture incomplete. Try again.');
      setStatus('Incomplete', 'idle');
      active = false;
      return;
    }

    setStatus('Saving', 'active');
    try {
      const response = await fetch('/api/save_keystrokes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          password: currentPassword,
          participant_id: participantId.value,
          session_type: sessionType.value,
          metrics: [metrics],
        }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || 'Failed to save keystrokes');
      }

      setStatus('Saved', 'saved');
      logLine(`Saved ${payload.entries_saved} attempt(s) for ${currentPassword}.`);
      active = false;
    } catch (error) {
      setStatus('Error', 'idle');
      logLine(error.message);
    }
  };

  const captureEvent = (type, event) => {
    if (!active) {
      return;
    }

    if (event.key === 'Enter' && type === 'keydown') {
      event.preventDefault();
      if (typingField.value === currentPassword) {
        logLine('Password matched. Finalizing capture...');
        submitCapture();
      } else {
        logLine('Password mismatch. Restart the capture.');
        setStatus('Mismatch', 'idle');
        active = false;
      }
      return;
    }

    if (event.key === 'Backspace') {
      logLine('Backspace detected. Capture reset.');
      resetCapture();
      return;
    }

    if (event.key.length !== 1 && event.key !== ' ') {
      return;
    }

    rawEvents.push({
      key: event.key,
      type,
      timestamp: performance.now(),
    });
  };

  passwordSelect.addEventListener('change', updateTarget);
  startButton.addEventListener('click', resetCapture);
  typingField.addEventListener('keydown', (event) => captureEvent('keydown', event));
  typingField.addEventListener('keyup', (event) => captureEvent('keyup', event));

  updateTarget();
  setStatus('Idle', 'idle');
  typingField.addEventListener('focus', () => {
    if (!active) {
      logLine('Press Start capture to begin a new attempt.');
    }
  });
})();
