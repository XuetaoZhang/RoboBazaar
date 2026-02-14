document.addEventListener('DOMContentLoaded', () => {
  // Elements
  // const statusPill = document.getElementById('system-status'); // Removed
  // const statusText = document.getElementById('status-text'); // Removed
  const bannerStatusText = document.getElementById('banner-status-text');
  const bannerRisk = document.getElementById('banner-risk');
  const bannerError = document.getElementById('banner-error');
  const bannerTime = document.getElementById('banner-time');
  const bannerDot = document.getElementById('banner-dot');
  const statusBanner = document.getElementById('status-banner');
  
  const fleetDot01 = document.getElementById('fleet-dot-01');
  const fleetStatus01 = document.getElementById('fleet-status-01');

  const riskScore = document.getElementById('risk-score'); // Keep for legacy refs if any
  const alertModal = document.getElementById('alert-modal');
  const paymentModal = document.getElementById('payment-modal');
  const successModal = document.getElementById('success-modal');
  const btnHelp = document.getElementById('btn-help');
  const btnSign = document.getElementById('btn-sign');
  const btnCloseSuccess = document.getElementById('btn-close-success');
  const btnReset = document.getElementById('btn-reset');
  const btnTriggerError = document.getElementById('btn-trigger-error');
  const logFeed = document.getElementById('log-feed');

  // State
  let isStuck = false;
  let isPaid = false;

  // Helpers
  function log(msg, type = 'info') {
    const entry = document.createElement('div');
    entry.className = `log-line`;
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    
    // Convert old classes to new log-msg classes
    const msgClass = type === 'error' ? 'error' : (type === 'success' ? 'success' : 'info');
    
    entry.innerHTML = `<span class="log-ts">${time}</span><span class="log-msg ${msgClass}">${msg}</span>`;
    logFeed.prepend(entry);
  }

  function setStatus(status) {
    const now = new Date().toLocaleTimeString('en-US', { hour12: false });
    bannerTime.innerText = now;

    if (status === 'active') {
      // Banner Updates
      statusBanner.className = 'card status-banner';
      bannerStatusText.innerHTML = '<div class="dot green" id="banner-dot"></div> ACTIVE';
      bannerStatusText.style.color = '#10b981';
      bannerRisk.innerText = '0.02';
      bannerRisk.style.color = '#10b981';
      bannerError.innerText = 'NONE';
      bannerError.style.color = 'var(--color-text-muted)';
      
      // Fleet Updates
      fleetDot01.className = 'dot green';
      fleetStatus01.innerText = 'Operational';
      
      alertModal.classList.remove('visible');
      paymentModal.classList.remove('visible');
      successModal.classList.remove('visible');
      isStuck = false;
    } else if (status === 'stuck') {
      // Banner Updates
      statusBanner.className = 'card status-banner alert';
      bannerStatusText.innerHTML = '<div class="dot red" id="banner-dot"></div> WAITING FOR HELP';
      bannerStatusText.style.color = '#ef4444';
      bannerRisk.innerText = '0.82';
      bannerRisk.style.color = '#ef4444';
      bannerError.innerText = 'GRASP_FAILURE';
      bannerError.style.color = '#ef4444';

      // Fleet Updates
      fleetDot01.className = 'dot red';
      fleetStatus01.innerText = 'Intervention Req.';

      alertModal.classList.add('visible');
      isStuck = true;
      log('CRITICAL: Axis-Z Collision Detected. Risk: 0.82', 'error');
    }
  }

  function unlockControls() {
    btnReset.disabled = false;
    btnReset.classList.remove('btn-ghost');
    btnReset.classList.add('btn-primary'); // Highlight reset button
    log('X402 Payment Verified. Control Authority: UNLOCKED', 'success');
  }

  function lockControls() {
    btnReset.disabled = true;
    btnReset.classList.remove('btn-primary');
    btnReset.classList.add('btn-ghost');
  }

  // Event Listeners
  btnTriggerError.addEventListener('click', () => {
    setStatus('stuck');
  });

  btnHelp.addEventListener('click', () => {
    alertModal.classList.remove('visible');
    paymentModal.classList.add('visible');
    log('Handshake initiated. Requesting signature...', 'info');
  });

  btnSign.addEventListener('click', () => {
    // Simulate wallet interaction delay
    btnSign.innerText = 'Verifying Signature...';
    setTimeout(() => {
      paymentModal.classList.remove('visible');
      successModal.classList.add('visible');
      btnSign.innerText = 'Sign & Pay 0.50 USDC';
      isPaid = true;
      log('Signature Valid. Tx Broadcast: 0x82...1a', 'success');
    }, 1500);
  });

  btnCloseSuccess.addEventListener('click', () => {
    successModal.classList.remove('visible');
    unlockControls();
  });

  btnReset.addEventListener('click', () => {
    log('Sending RESET command to Robot #01...');
    setTimeout(() => {
      setStatus('active');
      lockControls();
      log('Robot #01 recovered successfully.');
    }, 1000);
  });

  // Init
  log('System ready. Waiting for telemetry...');
  
  // Auto-trigger error for demo purposes after 3 seconds
  setTimeout(() => {
    setStatus('stuck');
  }, 3000);

});