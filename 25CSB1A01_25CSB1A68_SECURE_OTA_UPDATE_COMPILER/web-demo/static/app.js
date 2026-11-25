const sampleSelect = document.getElementById('sampleSelect');
const loadSampleBtn = document.getElementById('loadSampleBtn');
const policySelect = document.getElementById('policySelect');
const policyDesc = document.getElementById('policyDesc');
let availablePolicies = [];
const clearCodeBtn = document.getElementById('clearCodeBtn');
const compileBtn = document.getElementById('compileBtn');
const demoButtons = document.getElementById('demoButtons');
const codeInput = document.getElementById('codeInput');
const highlightLayer = document.getElementById('highlightLayer');
const highlightCode = document.getElementById('highlightCode');
const lineNumbers = document.getElementById('lineNumbers');
const filenameInput = document.getElementById('filenameInput');
const resultBadge = document.getElementById('resultBadge');
const messageBox = document.getElementById('messageBox');
const energyBox = document.getElementById('energyBox');
const energyPhases = document.getElementById('energyPhases');
const energyCard = document.getElementById('energyCard');
const energyToggle = document.getElementById('energyToggle');
const violationsList = document.getElementById('violationsList');
const hintsList = document.getElementById('hintsList');
const rawOutput = document.getElementById('rawOutput');
const historyList = document.getElementById('historyList');
const historyChart = document.getElementById('historyChart');
const historyChartWrap = document.getElementById('historyChartWrap');
const exportJsonBtn = document.getElementById('exportJsonBtn');
const exportMdBtn = document.getElementById('exportMdBtn');
const themeToggle = document.getElementById('themeToggle');
const themeGlyph = document.getElementById('themeGlyph');
const sidebarCollapseBtn = document.getElementById('sidebarCollapseBtn');
const sidebarExpandBtn = document.getElementById('sidebarExpandBtn');
const appShell = document.querySelector('.app-shell');
const stagePanel = document.querySelector('.stage-panel');

// File Dropbox & Tab elements
const fileDropZone = document.getElementById('fileDropZone');
const fileDropboxInput = document.getElementById('fileDropboxInput');
const editorTabsBar = document.getElementById('editorTabsBar');
const editorTabsList = document.getElementById('editorTabsList');
const newTabBtn = document.getElementById('newTabBtn');
const runAllBtn = document.getElementById('runAllBtn');
const closeAllBtn = document.getElementById('closeAllBtn');

// Tab Management State
let tabs = [];
let activeTabId = null;
let tabCounter = 0;

// AI Analysis elements
const runCopilotBtn = document.getElementById('runCopilotBtn');
const copilotPlaceholder = document.getElementById('copilotPlaceholder');
const copilotResults = document.getElementById('copilotResults');
const copilotVerdictBadge = document.getElementById('copilotVerdictBadge');
const copilotObservations = document.getElementById('copilotObservations');
const copilotDiagnosticsSection = document.getElementById('copilotDiagnosticsSection');
const copilotDiagnosticsBreakdown = document.getElementById('copilotDiagnosticsBreakdown');
const copilotNoOpBanner = document.getElementById('copilotNoOpBanner');
const copilotCodeSection = document.getElementById('copilotCodeSection');
const copilotCodeSnippet = document.getElementById('copilotCodeSnippet');
const replaceCodeBtn = document.getElementById('replaceCodeBtn');
const restoreCodeBtn = document.getElementById('restoreCodeBtn');
const copySnippetBtn = document.getElementById('copySnippetBtn');
const copyBtnText = document.getElementById('copyBtnText');
let lastCompileData = null;
let lastCompiledCode = null;
let lastCopilotData = null;
let isAuditing = false;
let editorBackupCode = null;

const runHistory = [];
let lastCompilePayload = null;
let currentActiveLine = 1;
const hintLines = new Map();
const THEME_KEY = 'ota-demo-theme';
const SIDEBAR_KEY = 'ota-sidebar-collapsed';
const ENERGY_KEY = 'ota-energy-telemetry-enabled';

const LANG_STORAGE_KEY = 'ota-target-language';
let currentLanguage = localStorage.getItem(LANG_STORAGE_KEY) || 'c';
const langBtnC = document.getElementById('langBtnC');
const langBtnPy = document.getElementById('langBtnPy');

const demoScenariosC = [
  { label: 'Secure Baseline', sample: 'secure.c', expected: 'pass' },
  { label: 'Signature Missing', sample: 'insecure_rule_signature_missing.c', expected: 'fail' },
  { label: 'Rollback Violation', sample: 'insecure_rule_rollback_missing.c', expected: 'fail' },
  { label: 'Weak Crypto', sample: 'insecure_rule_weak_md5.c', expected: 'fail' },
  { label: 'Logging Leak', sample: 'insecure_rule_logging_puts.c', expected: 'fail' },
  { label: 'Hardcoded Secret', sample: 'insecure_hardcoded_secret.c', expected: 'fail' },
];

const demoScenariosPython = [
  { label: 'Secure Baseline', sample: 'secure.py', expected: 'pass' },
  { label: 'Signature Missing', sample: 'insecure_rule_signature_missing.py', expected: 'fail' },
  { label: 'Source Missing', sample: 'insecure_rule_source_missing.py', expected: 'fail' },
  { label: 'Hash Missing', sample: 'insecure_rule_hash_missing.py', expected: 'fail' },
  { label: 'Rollback Missing', sample: 'insecure_rule_rollback_missing.py', expected: 'fail' },
  { label: 'Rollback Equal Replay', sample: 'insecure_rule_rollback_equal_allowed.py', expected: 'fail' },
  { label: 'Banned eval()', sample: 'insecure_banned_eval.py', expected: 'fail' },
  { label: 'Weak MD5 Hash', sample: 'insecure_rule_weak_md5.py', expected: 'fail' },
  { label: 'Hardcoded Secret', sample: 'insecure_hardcoded_secret.py', expected: 'fail' },
];

let demoScenarios = demoScenariosC;

function getActiveTab() {
  if (!tabs || tabs.length === 0) return null;
  return tabs.find((t) => t.id === activeTabId) || tabs[0];
}

function saveActiveTabState() {
  const activeTab = getActiveTab();
  if (!activeTab) return;
  if (codeInput) activeTab.code = codeInput.value;
  if (filenameInput && filenameInput.value.trim()) activeTab.filename = filenameInput.value.trim();
  activeTab.lastCompileData = lastCompileData;
  activeTab.lastCompiledCode = lastCompiledCode;
  activeTab.lastCopilotData = lastCopilotData;
  activeTab.editorBackupCode = editorBackupCode;
  if (resultBadge) {
    if (resultBadge.classList.contains('passed')) activeTab.badgeState = 'passed';
    else if (resultBadge.classList.contains('failed')) activeTab.badgeState = 'failed';
    else activeTab.badgeState = 'idle';
  }
  const pill = document.getElementById('eventPill');
  const msgText = document.getElementById('messageText');
  activeTab.messageText = msgText ? msgText.textContent : '';
  if (messageBox) {
    if (messageBox.classList.contains('good')) activeTab.messageMode = 'good';
    else if (messageBox.classList.contains('bad')) activeTab.messageMode = 'bad';
    else activeTab.messageMode = 'neutral';
  }
  activeTab.messagePill = pill ? pill.textContent : 'EVENT';
  activeTab.rawOutput = rawOutput ? rawOutput.textContent : '(no output)';
}

function renderTabs() {
  if (!editorTabsList) return;
  editorTabsList.innerHTML = '';

  tabs.forEach((tab) => {
    const tabEl = document.createElement('div');
    const isActive = tab.id === activeTabId;
    tabEl.className = 'editor-tab' + (isActive ? ' active' : '');
    tabEl.setAttribute('role', 'tab');
    tabEl.setAttribute('aria-selected', isActive ? 'true' : 'false');
    tabEl.dataset.tabId = tab.id;

    // File icon
    const iconSpan = document.createElement('span');
    iconSpan.className = 'tab-icon';
    iconSpan.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>`;

    // Title
    const titleSpan = document.createElement('span');
    titleSpan.className = 'tab-title';
    titleSpan.textContent = tab.filename || 'untitled.c';
    titleSpan.title = tab.filename || 'untitled.c';

    // Status dot
    const statusDot = document.createElement('span');
    statusDot.className = 'tab-status-dot ' + (tab.badgeState || 'idle');
    if (tab.badgeState === 'passed') {
      statusDot.title = 'Verification passed';
    } else if (tab.badgeState === 'failed') {
      statusDot.title = 'Verification blocked';
    }

    // Close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'tab-close-btn';
    closeBtn.type = 'button';
    closeBtn.setAttribute('aria-label', `Close ${tab.filename}`);
    closeBtn.title = `Close ${tab.filename}`;
    closeBtn.innerHTML = '&times;';
    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeTab(tab.id);
    });

    tabEl.appendChild(iconSpan);
    tabEl.appendChild(titleSpan);
    tabEl.appendChild(statusDot);
    tabEl.appendChild(closeBtn);

    tabEl.addEventListener('click', () => {
      activateTab(tab.id);
    });

    editorTabsList.appendChild(tabEl);
  });

  const activeEl = editorTabsList.querySelector('.editor-tab.active');
  if (activeEl) {
    activeEl.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
  }
}

function activateTab(tabId, forceRefresh = false) {
  if (activeTabId === tabId && !forceRefresh) return;
  if (activeTabId !== tabId) {
    saveActiveTabState();
  }
  activeTabId = tabId;
  const tab = getActiveTab();
  if (!tab) return;

  // Restore editor values
  if (codeInput) codeInput.value = tab.code;
  if (filenameInput) filenameInput.value = tab.filename;
  lastCompileData = tab.lastCompileData;
  lastCompiledCode = tab.lastCompiledCode;
  lastCopilotData = tab.lastCopilotData;
  editorBackupCode = tab.editorBackupCode;

  // Restore badge & message
  setBadge(tab.badgeState || 'idle');
  setMessage(tab.messageText || 'Run compilation to see results.', tab.messageMode || 'neutral');
  if (tab.messagePill) {
    const pill = document.getElementById('eventPill');
    if (pill) pill.textContent = tab.messagePill;
  }

  // Restore violations & hints
  renderList(violationsList, tab.violations || [], (v) => v);
  hintLines.clear();
  if (Array.isArray(tab.hints)) {
    for (const h of tab.hints) {
      if (h.line) hintLines.set(h.line, h.kind || 'warning');
    }
  }
  renderHints(tab.hints || []);

  // Restore raw output
  if (rawOutput) rawOutput.textContent = tab.rawOutput || '(no output)';

  // Restore energy if enabled
  if (isEnergyEnabled()) {
    renderEnergy(tab.energy);
  }

  // Restore copilot UI
  if (tab.lastCopilotData) {
    renderCopilotData(tab.lastCopilotData);
  } else {
    if (copilotPlaceholder) copilotPlaceholder.style.display = 'block';
    if (copilotResults) copilotResults.style.display = 'none';
  }

  if (restoreCodeBtn) {
    restoreCodeBtn.style.display = tab.editorBackupCode !== null ? 'inline-block' : 'none';
  }

  updateLineNumbers();
  updateHighlighting();
  updateActiveDemoButton(tab.filename);
  renderTabs();
}

function createTab(filename, code = '', selectNow = true) {
  if (activeTabId) {
    saveActiveTabState();
  }
  const id = `tab-${++tabCounter}`;
  const defaultExt = currentLanguage === 'python' ? '.py' : '.c';
  const newTab = {
    id,
    filename: filename || `firmware_${tabCounter}${defaultExt}`,
    code: code || '',
    lastCompileData: null,
    lastCompiledCode: null,
    lastCopilotData: null,
    editorBackupCode: null,
    badgeState: 'idle',
    messageText: 'Ready to compile.',
    messageMode: 'neutral',
    messagePill: 'EVENT',
    violations: [],
    hints: [],
    rawOutput: '(no output)',
    energy: null
  };
  tabs.push(newTab);

  if (selectNow) {
    activeTabId = id;
    if (codeInput) codeInput.value = newTab.code;
    if (filenameInput) filenameInput.value = newTab.filename;
    lastCompileData = null;
    lastCompiledCode = null;
    lastCopilotData = null;
    editorBackupCode = null;
    setBadge('idle');
    setMessage('Ready to compile.', 'neutral');
    renderList(violationsList, [], (v) => v);
    renderHints([]);
    if (rawOutput) rawOutput.textContent = '(no output)';
    if (copilotPlaceholder) copilotPlaceholder.style.display = 'block';
    if (copilotResults) copilotResults.style.display = 'none';
    updateLineNumbers();
    updateHighlighting();
    updateActiveDemoButton(newTab.filename);
  }

  renderTabs();
  return newTab;
}

function closeTab(tabId) {
  if (tabs.length === 1) {
    const tab = tabs[0];
    tab.filename = 'firmware_demo.c';
    tab.code = '';
    tab.lastCompileData = null;
    tab.lastCompiledCode = null;
    tab.lastCopilotData = null;
    tab.editorBackupCode = null;
    tab.badgeState = 'idle';
    tab.messageText = 'Editor reset. Ready.';
    tab.messageMode = 'neutral';
    tab.messagePill = 'EVENT';
    tab.violations = [];
    tab.hints = [];
    tab.rawOutput = '(no output)';
    if (codeInput) codeInput.value = '';
    if (filenameInput) filenameInput.value = 'firmware_demo.c';
    lastCompileData = null;
    lastCompiledCode = null;
    lastCopilotData = null;
    editorBackupCode = null;
    setBadge('idle');
    setMessage('Editor reset. Ready.', 'neutral');
    renderList(violationsList, [], (v) => v);
    renderHints([]);
    if (rawOutput) rawOutput.textContent = '(no output)';
    if (copilotPlaceholder) copilotPlaceholder.style.display = 'block';
    if (copilotResults) copilotResults.style.display = 'none';
    updateLineNumbers();
    updateHighlighting();
    renderTabs();
    return;
  }

  const idx = tabs.findIndex((t) => t.id === tabId);
  if (idx === -1) return;

  const wasActive = activeTabId === tabId;
  tabs.splice(idx, 1);

  if (wasActive) {
    const nextIdx = idx > 0 ? idx - 1 : 0;
    activeTabId = tabs[nextIdx].id;
    const tab = tabs[nextIdx];
    if (codeInput) codeInput.value = tab.code;
    if (filenameInput) filenameInput.value = tab.filename;
    lastCompileData = tab.lastCompileData;
    lastCompiledCode = tab.lastCompiledCode;
    lastCopilotData = tab.lastCopilotData;
    editorBackupCode = tab.editorBackupCode;
    setBadge(tab.badgeState || 'idle');
    setMessage(tab.messageText || 'Ready.', tab.messageMode || 'neutral');
    renderList(violationsList, tab.violations || [], (v) => v);
    hintLines.clear();
    if (Array.isArray(tab.hints)) {
      for (const h of tab.hints) {
        if (h.line) hintLines.set(h.line, h.kind || 'warning');
      }
    }
    renderHints(tab.hints || []);
    if (rawOutput) rawOutput.textContent = tab.rawOutput || '(no output)';
    if (tab.lastCopilotData) {
      renderCopilotData(tab.lastCopilotData);
    } else {
      if (copilotPlaceholder) copilotPlaceholder.style.display = 'block';
      if (copilotResults) copilotResults.style.display = 'none';
    }
    updateLineNumbers();
    updateHighlighting();
    updateActiveDemoButton(tab.filename);
  }

  renderTabs();
}

function closeAllTabs() {
  tabCounter = 1;
  const initialTab = {
    id: 'tab-1',
    filename: 'firmware_demo.c',
    code: '',
    lastCompileData: null,
    lastCompiledCode: null,
    lastCopilotData: null,
    editorBackupCode: null,
    badgeState: 'idle',
    messageText: 'All tabs closed. Editor reset.',
    messageMode: 'neutral',
    messagePill: 'EVENT',
    violations: [],
    hints: [],
    rawOutput: '(no output)',
    energy: null
  };
  tabs = [initialTab];
  activeTabId = 'tab-1';

  if (codeInput) codeInput.value = '';
  if (filenameInput) filenameInput.value = currentLanguage === 'python' ? 'firmware_demo.py' : 'firmware_demo.c';
  lastCompileData = null;
  lastCompiledCode = null;
  lastCopilotData = null;
  editorBackupCode = null;

  setBadge('idle');
  setMessage('All tabs closed. Editor reset.', 'neutral');
  renderList(violationsList, [], (v) => v);
  hintLines.clear();
  renderHints([]);
  if (rawOutput) rawOutput.textContent = '(no output)';
  if (copilotPlaceholder) copilotPlaceholder.style.display = 'block';
  if (copilotResults) copilotResults.style.display = 'none';
  if (restoreCodeBtn) restoreCodeBtn.style.display = 'none';

  updateLineNumbers();
  updateHighlighting();
  updateActiveDemoButton(null);
  renderTabs();
}

function setActionButtonsState(isRunning) {
  const rBtn = document.getElementById('runAllBtn');
  const cBtn = document.getElementById('closeAllBtn');

  if (rBtn) {
    rBtn.disabled = isRunning;
    rBtn.innerHTML = isRunning
      ? '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="spin-icon"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>'
      : '<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="6 3 20 12 6 21 6 3"></polygon></svg>';
  }

  if (cBtn) {
    cBtn.disabled = isRunning;
  }

  if (compileBtn) compileBtn.disabled = isRunning;
}

function wireActionButtons() {
  const rBtn = document.getElementById('runAllBtn');
  const cBtn = document.getElementById('closeAllBtn');
  const addBtn = document.getElementById('newTabBtn');

  if (rBtn) rBtn.onclick = runAll;
  if (cBtn) cBtn.onclick = closeAllTabs;
  if (addBtn) {
    addBtn.onclick = () => {
      const ext = currentLanguage === 'python' ? '.py' : '.c';
      createTab(`firmware_${tabCounter + 1}${ext}`, '', true);
    };
  }
}

function ensureActionButtons() {
  // 1. Ensure Header Actions have Run All & Close All icon buttons (no text, same line)
  const headerActions = document.querySelector('.editor-header-actions');
  const compileBtnEl = document.getElementById('compileBtn');
  if (headerActions && compileBtnEl) {
    let rBtn = document.getElementById('runAllBtn');
    if (!rBtn) {
      rBtn = document.createElement('button');
      rBtn.id = 'runAllBtn';
      rBtn.className = 'btn secondary editor-icon-btn run-all';
      rBtn.type = 'button';
      rBtn.title = 'Run All';
      rBtn.setAttribute('aria-label', 'Run All');
      rBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="6 3 20 12 6 21 6 3"></polygon></svg>';
      headerActions.insertBefore(rBtn, compileBtnEl);
    } else {
      rBtn.className = 'btn secondary editor-icon-btn run-all';
      rBtn.title = 'Run All';
      rBtn.setAttribute('aria-label', 'Run All');
      rBtn.innerHTML = '<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="none"><polygon points="6 3 20 12 6 21 6 3"></polygon></svg>';
    }

    let cBtn = document.getElementById('closeAllBtn');
    if (!cBtn) {
      cBtn = document.createElement('button');
      cBtn.id = 'closeAllBtn';
      cBtn.className = 'btn secondary editor-icon-btn close-all';
      cBtn.type = 'button';
      cBtn.title = 'Close All';
      cBtn.setAttribute('aria-label', 'Close All');
      cBtn.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
      headerActions.insertBefore(cBtn, compileBtnEl);
    } else {
      cBtn.className = 'btn secondary editor-icon-btn close-all';
      cBtn.title = 'Close All';
      cBtn.setAttribute('aria-label', 'Close All');
      cBtn.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
    }
  }

  // 2. Remove any extra buttons that were previously added to the tab bar
  const tabsBarEl = document.getElementById('editorTabsBar');
  const controlsEl = document.getElementById('editorTabsControls');
  if (tabsBarEl && controlsEl) {
    let addBtn = document.getElementById('newTabBtn');
    if (addBtn) {
      addBtn.className = 'tab-add-btn';
      tabsBarEl.appendChild(addBtn);
    }
    controlsEl.remove();
  }

  wireActionButtons();
}

async function runAll() {
  if (!tabs || tabs.length === 0) return;

  setActionButtonsState(true);

  saveActiveTabState();

  const energyEnabled = isEnergyEnabled();
  let passedCount = 0;
  let blockedCount = 0;

  for (let i = 0; i < tabs.length; i++) {
    const tab = tabs[i];
    const code = (tab.code || '').trim();
    if (!code) {
      tab.badgeState = 'idle';
      tab.messageText = 'Firmware source is empty in this tab.';
      tab.messageMode = 'bad';
      tab.messagePill = 'EVENT';
      tab.violations = [];
      tab.hints = [];
      tab.rawOutput = '(no code in tab)';
      renderTabs();
      continue;
    }

    try {
      const res = await fetch('/api/compile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: tab.filename || (currentLanguage === 'python' ? `firmware_${i + 1}.py` : `firmware_${i + 1}.c`),
          code: tab.code,
          language: currentLanguage,
          policy: policySelect ? policySelect.value : 'original_protocol.json',
          energy: energyEnabled,
        }),
      });

      const data = await res.json();
      tab.lastCompileData = data;
      tab.lastCompiledCode = tab.code;
      tab.badgeState = data.ok ? 'passed' : 'failed';
      tab.violations = data.violations || [];
      tab.hints = data.hints || [];
      tab.rawOutput = data.rawOutput || '(no output)';
      tab.energy = data.energy || null;
      tab.messageText = data.message;
      tab.messageMode = data.ok ? 'good' : 'bad';
      tab.messagePill = data.ok ? 'PASSED' : 'BLOCKED';

      if (data.ok) passedCount++;
      else blockedCount++;

      const totalEnergy = (energyEnabled && data.energy?.total?.energy_kwh) || 0;
      const totalEmissions = (energyEnabled && data.energy?.total?.emissions_kg) || 0;
      addHistoryEntry({
        timestamp: Date.now(),
        filename: tab.filename,
        status: data.ok ? 'pass' : 'fail',
        violations: (data.violations || []).length,
        energyKwh: Number(totalEnergy),
        emissionsKg: Number(totalEmissions),
      });

    } catch (err) {
      tab.badgeState = 'failed';
      tab.messageText = `Compile error: ${err.message}`;
      tab.messageMode = 'bad';
      tab.messagePill = 'BLOCKED';
      blockedCount++;
    }

    renderTabs();

    if (tab.id === activeTabId) {
      activateTab(tab.id, true);
    }
  }

  const currentActive = getActiveTab();
  if (currentActive) {
    activateTab(currentActive.id, true);
    setMessage(
      `Run All finished: ${passedCount} passed, ${blockedCount} blocked across ${tabs.length} tabs. Results shown for open tab "${currentActive.filename}".`,
      currentActive.badgeState === 'passed' ? 'good' : (currentActive.badgeState === 'failed' ? 'bad' : 'neutral')
    );
  }

  setActionButtonsState(false);
}

function initTabs() {
  ensureActionButtons();
  tabCounter = 1;
  const defaultInitial = currentLanguage === 'python' ? 'firmware_demo.py' : 'firmware_demo.c';
  const initialName = filenameInput ? filenameInput.value.trim() || defaultInitial : defaultInitial;
  const initialCode = codeInput ? codeInput.value : '';
  const initialTab = {
    id: 'tab-1',
    filename: initialName,
    code: initialCode,
    lastCompileData: null,
    lastCompiledCode: null,
    lastCopilotData: null,
    editorBackupCode: null,
    badgeState: 'idle',
    messageText: 'Run compilation to see results.',
    messageMode: 'neutral',
    messagePill: 'EVENT',
    violations: [],
    hints: [],
    rawOutput: '(no output)',
    energy: null
  };
  tabs = [initialTab];
  activeTabId = 'tab-1';
  renderTabs();

  wireActionButtons();

  if (filenameInput) {
    filenameInput.addEventListener('input', () => {
      const activeTab = getActiveTab();
      if (activeTab) {
        activeTab.filename = filenameInput.value.trim() || 'firmware_demo.c';
        renderTabs();
      }
    });
  }
}

function parseMultiCodeContent(text, defaultFilename) {
  if (!text || !text.trim()) {
    return [{ filename: defaultFilename || 'firmware_demo.c', code: '' }];
  }

  // 1. Markdown code fences
  const mdRegex = /(?:(?:^|\n)(?:#{1,6}|\/\/|\/\*)\s*([a-zA-Z0-9_\-.]+(?:\.[a-zA-Z0-9]+)?)[^\n]*\n)?```(?:c|cpp|h)?\r?\n([\s\S]*?)\r?\n```/gi;
  const mdMatches = [];
  let match;
  while ((match = mdRegex.exec(text)) !== null) {
    let fname = match[1] ? match[1].trim() : '';
    if (fname && !fname.includes('.')) {
      fname += '.c';
    }
    mdMatches.push({
      filename: fname,
      code: match[2].trim()
    });
  }

  if (mdMatches.length >= 2) {
    return mdMatches.map((item, idx) => ({
      filename: item.filename || `snippet_${idx + 1}.c`,
      code: item.code
    }));
  }

  // 2. Delimiter pattern
  const delimRegex = /(?:^|\r?\n)[ \t]*(?:(?:\/\/|\/\*+|#|--+|==+)[ \t]*(?:File:|Filename:|Code:|Case:|Scenario:|Section:|===+|---+)?\s*\[?([a-zA-Z0-9_\-.]+\.(?:c|h|txt|cpp))\]?\s*(?:===+|---+)?\s*(?:\*\/)?|###+[ \t]+([a-zA-Z0-9_\-.]+\.(?:c|h|txt|cpp))|(?:\/\/|\/\*+)[ \t]*(?:Code|Case|File|Scenario)\s*(\d+)[ \t]*(?:\*\/)?)[ \t]*(?:\r?\n|$)/gi;

  const matches = [];
  while ((match = delimRegex.exec(text)) !== null) {
    let fname = match[1] || match[2];
    if (!fname && match[3]) {
      fname = `case_${match[3]}.c`;
    }
    matches.push({
      filename: fname,
      start: match.index,
      end: match.index + match[0].length
    });
  }

  if (matches.length >= 2) {
    const segments = [];
    for (let i = 0; i < matches.length; i++) {
      const cur = matches[i];
      const startIdx = cur.end;
      const endIdx = (i + 1 < matches.length) ? matches[i + 1].start : text.length;
      let snippet = text.slice(startIdx, endIdx).trim();
      snippet = snippet.replace(/^```(?:c|cpp)?\r?\n/i, '').replace(/\r?\n```$/i, '').trim();
      segments.push({
        filename: cur.filename || `part_${i + 1}.c`,
        code: snippet
      });
    }
    return segments;
  }

  if (matches.length === 1 && matches[0].start < 30) {
    const cur = matches[0];
    let snippet = text.slice(cur.end).trim();
    snippet = snippet.replace(/^```(?:c|cpp)?\r?\n/i, '').replace(/\r?\n```$/i, '').trim();
    let fname = cur.filename || defaultFilename || 'firmware_demo.c';
    if (fname.toLowerCase().endsWith('.txt')) {
      fname = fname.slice(0, -4) + '.c';
    }
    return [{
      filename: fname,
      code: snippet
    }];
  }

  let fallbackName = defaultFilename || 'firmware_demo.c';
  if (fallbackName.toLowerCase().endsWith('.txt')) {
    fallbackName = fallbackName.slice(0, -4) + '.c';
  }

  return [{
    filename: fallbackName,
    code: text
  }];
}

function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(reader.error);
    reader.readAsText(file);
  });
}

async function handleFiles(files) {
  if (!files || files.length === 0) return;

  const parsedSegments = [];

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    try {
      const text = await readFileAsText(file);
      const segments = parseMultiCodeContent(text, file.name);
      for (const seg of segments) {
        parsedSegments.push(seg);
      }
    } catch (err) {
      console.error(`Failed to read file ${file.name}:`, err);
    }
  }

  if (parsedSegments.length === 0) return;

  const currentTab = getActiveTab();
  const isDefaultEmpty = tabs.length === 1 && (!currentTab.code || !currentTab.code.trim()) && currentTab.filename === 'firmware_demo.c';

  let targetActiveId = null;

  parsedSegments.forEach((seg, idx) => {
    if (idx === 0 && isDefaultEmpty) {
      currentTab.filename = seg.filename;
      currentTab.code = seg.code;
      currentTab.lastCompileData = null;
      currentTab.lastCompiledCode = null;
      currentTab.lastCopilotData = null;
      currentTab.editorBackupCode = null;
      currentTab.badgeState = 'idle';
      currentTab.violations = [];
      currentTab.hints = [];
      currentTab.rawOutput = '(no output)';
      currentTab.messageText = `Loaded ${seg.filename}.`;
      currentTab.messageMode = 'neutral';
      currentTab.messagePill = 'EVENT';
      targetActiveId = currentTab.id;
    } else {
      const newTab = createTab(seg.filename, seg.code, false);
      if (!targetActiveId) {
        targetActiveId = newTab.id;
      }
    }
  });

  if (targetActiveId) {
    activateTab(targetActiveId);
  }

  renderTabs();
  setMessage(`Loaded ${parsedSegments.length} code file(s) into editor tabs.`, 'good');
}

function initDropzone() {
  if (!fileDropZone || !fileDropboxInput) return;

  fileDropZone.addEventListener('click', () => {
    fileDropboxInput.click();
  });

  fileDropZone.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      fileDropboxInput.click();
    }
  });

  fileDropboxInput.addEventListener('change', () => {
    if (fileDropboxInput.files && fileDropboxInput.files.length > 0) {
      handleFiles(fileDropboxInput.files);
      fileDropboxInput.value = '';
    }
  });

  ['dragenter', 'dragover'].forEach((eventName) => {
    fileDropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      fileDropZone.classList.add('dragover');
    });
  });

  ['dragleave', 'dragend'].forEach((eventName) => {
    fileDropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      fileDropZone.classList.remove('dragover');
    });
  });

  fileDropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    fileDropZone.classList.remove('dragover');
    if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  });

  if (stagePanel) {
    stagePanel.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.stopPropagation();
    });

    stagePanel.addEventListener('drop', (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
      }
    });
  }
}

function updateActiveDemoButton(sampleName) {
  if (!demoButtons) return;
  const buttons = demoButtons.querySelectorAll('.demo-btn');
  buttons.forEach((btn) => {
    const isMatch = Boolean(sampleName && btn.dataset.sample === sampleName.trim());
    if (isMatch) {
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
    } else {
      btn.classList.remove('active');
      btn.setAttribute('aria-pressed', 'false');
    }
  });
}

function renderDemoButtons() {
  if (!demoButtons) return;
  demoButtons.innerHTML = '';
  const scenarios = currentLanguage === 'python' ? demoScenariosPython : demoScenariosC;
  for (const s of scenarios) {
    const btn = document.createElement('button');
    btn.className = 'demo-btn';
    btn.type = 'button';
    btn.dataset.sample = s.sample;
    btn.innerHTML = `<span class="demo-btn-title">${s.label}</span><em>${s.expected.toUpperCase()}</em>`;
    btn.addEventListener('click', async () => {
      sampleSelect.value = s.sample;
      await loadSample();
    });
    demoButtons.appendChild(btn);
  }
}

async function fetchSamples(lang = currentLanguage) {
  if (!sampleSelect) return;
  const res = await fetch(`/api/samples?lang=${encodeURIComponent(lang)}`);
  const data = await res.json();
  sampleSelect.innerHTML = '';

  for (const name of data.samples) {
    const opt = document.createElement('option');
    opt.value = name;
    opt.textContent = name;
    sampleSelect.appendChild(opt);
  }

  const defaultSample = lang === 'python' ? 'secure.py' : 'secure.c';
  if (data.samples.includes(defaultSample)) {
    sampleSelect.value = defaultSample;
  } else if (data.samples.length > 0) {
    sampleSelect.value = data.samples[0];
  }
}

async function fetchPolicies() {
  if (!policySelect) return;
  try {
    const res = await fetch('/api/policies');
    const data = await res.json();
    availablePolicies = data.policies || [];
    policySelect.innerHTML = '';

    for (const p of availablePolicies) {
      const opt = document.createElement('option');
      opt.value = p.filename;
      opt.textContent = p.name;
      policySelect.appendChild(opt);
    }

    if (availablePolicies.length > 0) {
      policySelect.value = availablePolicies[0].filename;
      updatePolicyDetails();
    }

    policySelect.addEventListener('change', updatePolicyDetails);
  } catch (err) {
    console.error('Failed to load policies:', err);
  }
}

function updatePolicyDetails() {
  if (!policyDesc || !policySelect) return;
  const p = availablePolicies.find((item) => item.filename === policySelect.value);
  if (!p) {
    policyDesc.innerHTML = '';
    return;
  }

  const rules = p.rules || {};
  const ruleTags = [
    { key: 'signature_verification', label: 'Signature Check' },
    { key: 'source_trust', label: 'Source Trust' },
    { key: 'rollback_guard', label: 'Anti-Rollback' },
    { key: 'banned_logging', label: 'Ban Logging' },
    { key: 'weak_crypto', label: 'Ban Weak Crypto' },
  ];

  const badgesHtml = ruleTags
    .map((r) => {
      const active = Boolean(rules[r.key]);
      const cls = active ? 'active' : 'inactive';
      const icon = active ? '✓ ' : '✗ ';
      return `<span class="policy-rule-tag ${cls}">${icon}${r.label}</span>`;
    })
    .join('');

  policyDesc.innerHTML = `
    <div>${p.description || ''}</div>
    <div class="policy-badge-list">${badgesHtml}</div>
  `;
}

function getActiveLineNumber() {
  if (!codeInput.value) return 1;
  const cursor = codeInput.selectionStart || 0;
  const textBeforeCursor = codeInput.value.slice(0, cursor);
  return textBeforeCursor.split('\n').length;
}

function updateActiveLine() {
  if (!lineNumbers) return;
  const activeLine = getActiveLineNumber();
  if (activeLine === currentActiveLine) return;

  const prevEl = lineNumbers.querySelector(`.line-number[data-line="${currentActiveLine}"]`);
  if (prevEl) prevEl.classList.remove('active');

  currentActiveLine = activeLine;
  const nextEl = lineNumbers.querySelector(`.line-number[data-line="${currentActiveLine}"]`);
  if (nextEl) nextEl.classList.add('active');
}

function updateLineNumbers() {
  if (!lineNumbers) return;
  const text = codeInput.value;
  const count = text ? text.split('\n').length : (codeInput.placeholder ? codeInput.placeholder.split('\n').length : 1);
  currentActiveLine = getActiveLineNumber();

  const frag = document.createDocumentFragment();
  for (let i = 1; i <= count; i++) {
    const div = document.createElement('div');
    let cls = 'line-number';
    if (i === currentActiveLine) cls += ' active';
    if (hintLines.has(i)) {
      cls += hintLines.get(i) === 'error' ? ' has-error' : ' has-hint';
    }
    div.className = cls;
    div.dataset.line = String(i);
    div.textContent = String(i);
    div.title = `Line ${i}`;
    frag.appendChild(div);
  }
  lineNumbers.innerHTML = '';
  lineNumbers.appendChild(frag);
  lineNumbers.scrollTop = codeInput.scrollTop;
}

function goToLine(lineNum) {
  const text = codeInput.value;
  if (!text) {
    codeInput.focus();
    return;
  }
  const lines = text.split('\n');
  if (lineNum < 1 || lineNum > lines.length) return;

  let start = 0;
  for (let i = 0; i < lineNum - 1; i++) {
    start += lines[i].length + 1;
  }
  const end = start + lines[lineNum - 1].length;

  codeInput.focus();
  codeInput.setSelectionRange(start, end);

  const lineHeight = 22;
  const targetScrollTop = (lineNum - 1) * lineHeight;
  const editorHeight = codeInput.clientHeight;
  if (targetScrollTop < codeInput.scrollTop || targetScrollTop > codeInput.scrollTop + editorHeight - lineHeight) {
    codeInput.scrollTop = Math.max(0, targetScrollTop - Math.floor(editorHeight / 3));
  }
  if (lineNumbers) {
    lineNumbers.scrollTop = codeInput.scrollTop;
  }
  updateActiveLine();
}

function renderHints(hints) {
  hintsList.innerHTML = '';
  if (!hints || hints.length === 0) {
    const li = document.createElement('li');
    li.textContent = 'None';
    hintsList.appendChild(li);
    return;
  }

  for (const h of hints) {
    const li = document.createElement('li');
    li.className = 'hint-item';
    const col = h.column ? `:${h.column}` : '';
    li.textContent = `L${h.line}${col} ${h.label}`;
    li.title = `Jump to line ${h.line}`;
    li.addEventListener('click', () => {
      goToLine(h.line);
    });
    hintsList.appendChild(li);
  }
}

function highlightC(code) {
  if (!code) return '';

  const tokenRegex = /(\/\*[\s\S]*?\*\/|\/\/[^\n]*)|("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(^#[a-zA-Z_]\w*(?:[^\n\\]|\\.)*)|(\b(?:updateFirmware|verifySignature|verify_signature|checkSignature|sourceTrusted|isSourceTrusted|validateSource|install|installFirmware|applyUpdate)\b)|(\b(?:printf|puts|fprintf|perror|syslog|vsyslog|snprintf|MD5|MD5_Init|MD5_Update|MD5_Final|SHA1|SHA1_Init|SHA1_Update|SHA1_Final|rand|srand)\b)|(\b(?:int|char|void|float|double|short|long|unsigned|signed|struct|union|enum|typedef|static|const|volatile|extern|inline|return|if|else|while|for|do|switch|case|break|continue|default|goto|sizeof|bool|true|false|NULL|size_t|uint8_t|uint16_t|uint32_t|uint64_t|int8_t|int16_t|int32_t|int64_t)\b)|(\b0x[0-9a-fA-F]+\b|\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?[fFlLuU]*\b)|(\b[A-Z][a-zA-Z0-9_]*\b)|([a-zA-Z_]\w*(?=\s*\())/gm;

  let lastIndex = 0;
  let html = '';
  let match;

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  while ((match = tokenRegex.exec(code)) !== null) {
    if (match.index > lastIndex) {
      html += escapeHtml(code.slice(lastIndex, match.index));
    }

    const [full, comment, string, directive, otaGood, otaBad, keyword, number, customType, funcCall] = match;

    if (comment) {
      html += `<span class="hl-comment">${escapeHtml(comment)}</span>`;
    } else if (string) {
      html += `<span class="hl-string">${escapeHtml(string)}</span>`;
    } else if (directive) {
      html += `<span class="hl-directive">${escapeHtml(directive)}</span>`;
    } else if (otaGood) {
      html += `<span class="hl-ota-good">${escapeHtml(otaGood)}</span>`;
    } else if (otaBad) {
      html += `<span class="hl-ota-bad">${escapeHtml(otaBad)}</span>`;
    } else if (keyword) {
      html += `<span class="hl-keyword">${escapeHtml(keyword)}</span>`;
    } else if (number) {
      html += `<span class="hl-number">${escapeHtml(number)}</span>`;
    } else if (customType) {
      html += `<span class="hl-type">${escapeHtml(customType)}</span>`;
    } else if (funcCall) {
      html += `<span class="hl-func">${escapeHtml(funcCall)}</span>`;
    } else {
      html += escapeHtml(full);
    }

    lastIndex = match.index + full.length;
  }

  if (lastIndex < code.length) {
    html += escapeHtml(code.slice(lastIndex));
  }

  if (code.endsWith('\n')) {
    html += ' ';
  }

  return html;
}

function highlightPython(code) {
  if (!code) return '';

  const tokenRegex = /(#[^\n]*)|("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(@[a-zA-Z_]\w*)|(\b(?:update_firmware|updateFirmware|verify_signature|verify_cryptographic_signature|verifySignature|source_trusted|sourceTrusted|is_source_trusted|verify_image_hash|verifyImageHash|decrypt_payload_aes_gcm|install)\b)|(\b(?:eval|exec|compile|os\.system|os\.popen|pickle\.loads|pickle\.load|MD5|SHA1|md5|sha1)\b)|(\b(?:def|class|return|if|elif|else|while|for|in|try|except|finally|raise|import|from|as|with|pass|break|continue|yield|lambda|assert|global|nonlocal|async|await|and|or|not|is|True|False|None)\b)|(\b0x[0-9a-fA-F]+\b|\b\d+(?:\.\d+)?\b)|(\b[A-Z][a-zA-Z0-9_]*\b)|([a-zA-Z_]\w*(?=\s*\())/gm;

  let lastIndex = 0;
  let html = '';
  let match;

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  while ((match = tokenRegex.exec(code)) !== null) {
    if (match.index > lastIndex) {
      html += escapeHtml(code.slice(lastIndex, match.index));
    }

    const [full, comment, string, decorator, otaGood, otaBad, keyword, number, customType, funcCall] = match;

    if (comment) {
      html += `<span class="hl-comment">${escapeHtml(comment)}</span>`;
    } else if (string) {
      html += `<span class="hl-string">${escapeHtml(string)}</span>`;
    } else if (decorator) {
      html += `<span class="hl-directive">${escapeHtml(decorator)}</span>`;
    } else if (otaGood) {
      html += `<span class="hl-ota-good">${escapeHtml(otaGood)}</span>`;
    } else if (otaBad) {
      html += `<span class="hl-ota-bad">${escapeHtml(otaBad)}</span>`;
    } else if (keyword) {
      html += `<span class="hl-keyword">${escapeHtml(keyword)}</span>`;
    } else if (number) {
      html += `<span class="hl-number">${escapeHtml(number)}</span>`;
    } else if (customType) {
      html += `<span class="hl-type">${escapeHtml(customType)}</span>`;
    } else if (funcCall) {
      html += `<span class="hl-func">${escapeHtml(funcCall)}</span>`;
    } else {
      html += escapeHtml(full);
    }

    lastIndex = match.index + full.length;
  }

  if (lastIndex < code.length) {
    html += escapeHtml(code.slice(lastIndex));
  }

  if (code.endsWith('\n')) {
    html += ' ';
  }

  return html;
}

function syncEditorScroll() {
  if (highlightLayer) {
    highlightLayer.scrollTop = codeInput.scrollTop;
    highlightLayer.scrollLeft = codeInput.scrollLeft;
  }
  if (lineNumbers) {
    lineNumbers.scrollTop = codeInput.scrollTop;
  }
}

function updateHighlighting() {
  if (!highlightCode) return;
  const val = codeInput.value;
  if (!val) {
    codeInput.classList.add('is-empty');
    highlightCode.innerHTML = '';
  } else {
    codeInput.classList.remove('is-empty');
    const activeTab = getActiveTab();
    const isPy = (activeTab && activeTab.filename && activeTab.filename.endsWith('.py')) || currentLanguage === 'python';
    highlightCode.innerHTML = isPy ? highlightPython(val) : highlightC(val);
  }
  syncEditorScroll();
}

function initEditorEvents() {
  codeInput.addEventListener('scroll', syncEditorScroll);

  if (lineNumbers) {
    lineNumbers.addEventListener('wheel', (e) => {
      codeInput.scrollTop += e.deltaY;
      syncEditorScroll();
      e.preventDefault();
    }, { passive: false });

    lineNumbers.addEventListener('click', (e) => {
      const lineEl = e.target.closest('.line-number');
      if (!lineEl) return;
      const lineNum = parseInt(lineEl.dataset.line, 10);
      if (!lineNum) return;
      goToLine(lineNum);
    });
  }

  codeInput.addEventListener('input', () => {
    lastCompiledCode = null;
    const activeTab = getActiveTab();
    if (activeTab) {
      activeTab.code = codeInput.value;
      activeTab.lastCompiledCode = null;
    }
    if (hintLines.size > 0) {
      hintLines.clear();
      renderHints([]);
    }
    updateLineNumbers();
    updateHighlighting();
    if (!codeInput.value.trim()) {
      updateActiveDemoButton(null);
    }
  });

  codeInput.addEventListener('click', updateActiveLine);
  codeInput.addEventListener('keyup', updateActiveLine);
  codeInput.addEventListener('select', updateActiveLine);

  codeInput.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = codeInput.selectionStart;
      const end = codeInput.selectionEnd;
      const val = codeInput.value;
      codeInput.value = val.substring(0, start) + '    ' + val.substring(end);
      codeInput.selectionStart = codeInput.selectionEnd = start + 4;
      lastCompiledCode = null;
      const activeTab = getActiveTab();
      if (activeTab) {
        activeTab.code = codeInput.value;
        activeTab.lastCompiledCode = null;
      }
      updateLineNumbers();
      updateHighlighting();
    }
  });
}

async function loadSample(options = {}) {
  if (!sampleSelect.value) return;
  const res = await fetch(`/api/samples/${encodeURIComponent(sampleSelect.value)}`);
  const data = await res.json();
  if (data.error) {
    setMessage(data.error, 'bad');
    return;
  }

  saveActiveTabState();

  const currentTab = getActiveTab();
  const isDefaultEmpty = tabs.length === 1 && (!currentTab.code || !currentTab.code.trim()) && currentTab.filename === 'firmware_demo.c';

  if (isDefaultEmpty) {
    currentTab.filename = data.name;
    currentTab.code = data.code;
    currentTab.lastCompiledCode = null;
    currentTab.lastCompileData = null;
    currentTab.lastCopilotData = null;
    currentTab.editorBackupCode = null;
    currentTab.badgeState = 'idle';
    currentTab.violations = [];
    currentTab.hints = [];
    currentTab.rawOutput = '(no output)';
    currentTab.messageText = `Loaded ${data.name}. Click "Run secure-clang" to compile or "Run Advisory Audit" for AI analysis.`;
    currentTab.messageMode = 'neutral';
    currentTab.messagePill = 'EVENT';
    if (codeInput) codeInput.value = data.code;
    if (filenameInput) filenameInput.value = data.name;
    renderTabs();
    activateTab(currentTab.id, true);
    return;
  }

  // If a tab with this exact filename is already open and unmodified, switch to it
  const existingTab = tabs.find((t) => t.filename === data.name);
  if (existingTab && existingTab.code === data.code && !options.forceNewTab) {
    activateTab(existingTab.id);
    setMessage(`Switched to open sample "${data.name}". Click "Run secure-clang" to compile or "Run Advisory Audit" for AI analysis.`, 'neutral');
    return;
  }

  // Open a new tab for this sample
  let targetName = data.name;
  let counter = 1;
  while (tabs.some((t) => t.filename === targetName)) {
    const dot = data.name.lastIndexOf('.');
    const base = dot !== -1 ? data.name.slice(0, dot) : data.name;
    const ext = dot !== -1 ? data.name.slice(dot) : '.c';
    targetName = `${base}_${++counter}${ext}`;
  }

  const newTab = createTab(targetName, data.code, true);
  newTab.messageText = `Loaded ${targetName} into new tab. Click "Run secure-clang" to compile or "Run Advisory Audit" for AI analysis.`;
  setMessage(newTab.messageText, 'neutral');
  updateActiveDemoButton(data.name);
}

function setBadge(state) {
  resultBadge.className = 'badge';
  if (state === 'passed') {
    resultBadge.classList.add('passed');
    resultBadge.textContent = 'Passed';
  } else if (state === 'failed') {
    resultBadge.classList.add('failed');
    resultBadge.textContent = 'Blocked';
  } else {
    resultBadge.classList.add('idle');
    resultBadge.textContent = 'Idle';
  }
}

function setMessage(text, mode) {
  if (!messageBox) return;
  messageBox.className = `message ${mode}`;
  const pill = document.getElementById('eventPill');
  const msgText = document.getElementById('messageText');
  if (pill) {
    if (mode === 'good') {
      pill.textContent = 'PASSED';
    } else if (mode === 'bad') {
      pill.textContent = 'BLOCKED';
    } else {
      pill.textContent = 'EVENT';
    }
  }
  if (msgText) {
    msgText.textContent = text;
  } else {
    messageBox.textContent = text;
  }
}

function getInitialTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored === 'dark' || stored === 'light') {
    return stored;
  }
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    return 'light';
  }
  return 'dark';
}

function applyTheme(theme) {
  document.body.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);
  if (themeToggle) {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    themeToggle.setAttribute('aria-label', `Switch to ${nextTheme} mode`);
    themeToggle.setAttribute('title', `Switch to ${nextTheme} mode`);
  }
  if (themeGlyph) {
    themeGlyph.className = `theme-glyph ${theme === 'dark' ? 'sun' : 'moon'}`;
  }
  drawHistoryChart();
}

function toggleTheme() {
  const current = document.body.getAttribute('data-theme') || 'dark';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

function isEnergyEnabled() {
  return Boolean(energyToggle && energyToggle.checked);
}

function updateEnergyVisibility() {
  const enabled = isEnergyEnabled();
  if (energyCard) {
    if (enabled) {
      energyCard.classList.remove('energy-ui-hidden');
    } else {
      energyCard.classList.add('energy-ui-hidden');
    }
  }
  if (historyChartWrap) {
    if (enabled) {
      historyChartWrap.classList.remove('energy-ui-hidden');
      drawHistoryChart();
    } else {
      historyChartWrap.classList.add('energy-ui-hidden');
    }
  }
  renderHistory();
}

function initEnergyToggle() {
  if (!energyToggle) return;
  // Default to false (disabled) for ~0.1s fast compilation
  const stored = localStorage.getItem(ENERGY_KEY);
  energyToggle.checked = stored === 'true';
  updateEnergyVisibility();

  energyToggle.addEventListener('change', () => {
    localStorage.setItem(ENERGY_KEY, energyToggle.checked ? 'true' : 'false');
    updateEnergyVisibility();
  });
}

function renderEnergy(energy) {
  if (!energy || !energy.available) {
    energyBox.className = 'message neutral';
    energyBox.textContent = 'CodeCarbon metrics unavailable. Ensure codecarbon is installed in the active Python environment.';
    renderList(energyPhases, [], (x) => x);
    return;
  }

  const total = energy.total || { energy_kwh: 0, emissions_kg: 0 };
  energyBox.className = 'message good';
  energyBox.textContent = `Total energy: ${Number(total.energy_kwh).toFixed(8)} kWh | Total emissions: ${Number(total.emissions_kg).toFixed(8)} kgCO2eq`;

  renderList(energyPhases, energy.phases, (p) =>
    `${p.phase} -> ${Number(p.energy_kwh).toFixed(8)} kWh, ${Number(p.emissions_kg).toFixed(8)} kgCO2eq`
  );
}

function renderList(listEl, items, formatItem) {
  listEl.innerHTML = '';
  if (!items || items.length === 0) {
    const li = document.createElement('li');
    li.textContent = 'None';
    listEl.appendChild(li);
    return;
  }

  for (const item of items) {
    const li = document.createElement('li');
    li.textContent = formatItem(item);
    listEl.appendChild(li);
  }
}

function formatTimestamp(ts) {
  const d = new Date(ts);
  return d.toLocaleString();
}

function addHistoryEntry(entry) {
  runHistory.unshift(entry);
  if (runHistory.length > 20) {
    runHistory.pop();
  }
  renderHistory();
}

function renderHistory() {
  const showEnergy = isEnergyEnabled();
  renderList(historyList, runHistory, (r) => {
    const base = `${formatTimestamp(r.timestamp)} | ${r.filename} | ${r.status.toUpperCase()} | violations=${r.violations}`;
    if (showEnergy && r.energyKwh > 0) {
      return `${base} | energy=${r.energyKwh.toFixed(8)} kWh`;
    }
    return base;
  });
  if (showEnergy) {
    drawHistoryChart();
  }
}

function drawHistoryChart() {
  if (!isEnergyEnabled()) return;
  const canvas = historyChart;
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const width = canvas.width;
  const height = canvas.height;
  const styles = getComputedStyle(document.body);
  const axisColor = styles.getPropertyValue('--line').trim() || '#314139';
  const labelColor = styles.getPropertyValue('--muted').trim() || '#95a79a';
  const barColor = styles.getPropertyValue('--accent').trim() || '#f4b860';
  ctx.clearRect(0, 0, width, height);

  ctx.strokeStyle = axisColor;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(30, 12);
  ctx.lineTo(30, height - 24);
  ctx.lineTo(width - 8, height - 24);
  ctx.stroke();

  if (runHistory.length === 0) {
    ctx.fillStyle = labelColor;
    ctx.font = '12px IBM Plex Mono';
    ctx.fillText('No runs yet', 40, 30);
    return;
  }

  const values = runHistory.slice(0, 10).map((r) => r.energyKwh);
  const max = Math.max(...values, 0.000001);
  const chartW = width - 46;
  const chartH = height - 42;
  const barW = chartW / values.length;

  values.forEach((v, i) => {
    const x = 32 + i * barW + 3;
    const h = (v / max) * (chartH - 8);
    const y = height - 24 - h;
    ctx.fillStyle = barColor;
    ctx.fillRect(x, y, Math.max(4, barW - 6), h);
  });

  ctx.fillStyle = labelColor;
  ctx.font = '11px IBM Plex Mono';
  ctx.fillText(`max ${max.toExponential(2)} kWh`, 36, 24);
}

function downloadBlob(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function exportJsonReport() {
  const payload = {
    generatedAt: new Date().toISOString(),
    lastRun: lastCompilePayload,
    history: runHistory,
  };
  downloadBlob(JSON.stringify(payload, null, 2), 'secure-compiler-report.json', 'application/json');
}

function exportMarkdownReport() {
  const lines = [];
  const showEnergy = isEnergyEnabled();
  lines.push('# Secure OTA Compiler Run Report');
  lines.push('');
  lines.push(`Generated: ${new Date().toISOString()}`);
  lines.push('');

  if (lastCompilePayload) {
    lines.push('## Latest Run');
    lines.push('');
    lines.push(`- Status: ${lastCompilePayload.status}`);
    lines.push(`- File: ${lastCompilePayload.filename}`);
    lines.push(`- Violations: ${lastCompilePayload.violations}`);
    if (showEnergy) {
      lines.push(`- Energy (kWh): ${lastCompilePayload.energyKwh.toFixed(8)}`);
      lines.push(`- Emissions (kgCO2eq): ${lastCompilePayload.emissionsKg.toFixed(8)}`);
    }
    lines.push('');
  }

  lines.push('## Run History');
  lines.push('');
  if (showEnergy) {
    lines.push('| Time | File | Status | Violations | Energy (kWh) |');
    lines.push('|---|---|---|---:|---:|');
    for (const r of runHistory) {
      lines.push(`| ${formatTimestamp(r.timestamp)} | ${r.filename} | ${r.status.toUpperCase()} | ${r.violations} | ${r.energyKwh.toFixed(8)} |`);
    }
  } else {
    lines.push('| Time | File | Status | Violations |');
    lines.push('|---|---|---|---:|');
    for (const r of runHistory) {
      lines.push(`| ${formatTimestamp(r.timestamp)} | ${r.filename} | ${r.status.toUpperCase()} | ${r.violations} |`);
    }
  }

  downloadBlob(lines.join('\n'), 'secure-compiler-report.md', 'text/markdown');
}

async function runCompile() {
  const code = codeInput.value.trim();
  if (!code) {
    setBadge('idle');
    setMessage('Firmware source is empty. Please enter code or load a sample first.', 'bad');
    return;
  }

  compileBtn.disabled = true;
  compileBtn.textContent = 'Compiling...';

  const energyEnabled = isEnergyEnabled();
  const activeTab = getActiveTab();
  if (activeTab) {
    activeTab.code = codeInput.value;
    activeTab.filename = (filenameInput && filenameInput.value.trim()) ? filenameInput.value.trim() : activeTab.filename;
  }

  const currentFilename = (activeTab && activeTab.filename) || (filenameInput ? filenameInput.value.trim() : 'firmware_demo.c') || 'firmware_demo.c';

  try {
    const res = await fetch('/api/compile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename: currentFilename,
        code: codeInput.value,
        language: (currentFilename && currentFilename.endsWith('.py')) ? 'python' : currentLanguage,
        policy: policySelect ? policySelect.value : 'original_protocol.json',
        energy: energyEnabled,
      }),
    });

    const data = await res.json();
    lastCompileData = data;
    lastCompiledCode = codeInput.value;

    if (activeTab) {
      activeTab.lastCompileData = data;
      activeTab.lastCompiledCode = codeInput.value;
      activeTab.badgeState = data.ok ? 'passed' : 'failed';
      activeTab.violations = data.violations || [];
      activeTab.hints = data.hints || [];
      activeTab.rawOutput = data.rawOutput || '(no output)';
      activeTab.energy = data.energy || null;
      activeTab.messageText = data.message;
      activeTab.messageMode = data.ok ? 'good' : 'bad';
      activeTab.messagePill = data.ok ? 'PASSED' : 'BLOCKED';
    }

    if (!res.ok) {
      setBadge('failed');
      setMessage(data.error || 'Compile request failed.', 'bad');
      renderTabs();
      return;
    }

    if (data.ok) {
      setBadge('passed');
      setMessage(data.message, 'good');
    } else {
      setBadge('failed');
      setMessage(data.message, 'bad');
    }

    renderList(violationsList, data.violations, (v) => v);
    hintLines.clear();
    if (Array.isArray(data.hints)) {
      for (const h of data.hints) {
        if (h.line) {
          hintLines.set(h.line, h.kind || 'warning');
        }
      }
    }
    renderHints(data.hints);
    updateLineNumbers();
    if (energyEnabled) {
      renderEnergy(data.energy);
    }
    rawOutput.textContent = data.rawOutput || '(no output)';

    // Auto-trigger advisory copilot analysis on new compile results
    await runAdvisoryAudit({
      fromCompile: true,
      rawOutput: data.rawOutput,
      violations: data.violations,
      hints: data.hints
    });

    const totalEnergy = (energyEnabled && data.energy?.total?.energy_kwh) || 0;
    const totalEmissions = (energyEnabled && data.energy?.total?.emissions_kg) || 0;
    const historyEntry = {
      timestamp: Date.now(),
      filename: currentFilename,
      status: data.ok ? 'pass' : 'fail',
      violations: (data.violations || []).length,
      energyKwh: Number(totalEnergy),
      emissionsKg: Number(totalEmissions),
    };
    lastCompilePayload = historyEntry;
    addHistoryEntry(historyEntry);

    renderTabs();
  } catch (err) {
    setBadge('failed');
    setMessage(`Unexpected error: ${err.message}`, 'bad');
    if (activeTab) {
      activeTab.badgeState = 'failed';
      renderTabs();
    }
  } finally {
    compileBtn.disabled = false;
    compileBtn.textContent = currentLanguage === 'python' ? 'Run secure-python' : 'Run secure-clang';
  }
}

loadSampleBtn.addEventListener('click', () => loadSample({ forceNewTab: true }));
if (clearCodeBtn) {
  clearCodeBtn.addEventListener('click', () => {
    codeInput.value = '';
    hintLines.clear();
    updateLineNumbers();
    updateHighlighting();
    updateActiveDemoButton(null);
    setBadge('idle');
    setMessage('Editor cleared. Codeholder is idle.', 'neutral');
    renderList(violationsList, [], (v) => v);
    renderHints([]);
    rawOutput.textContent = '(no output)';
    const activeTab = getActiveTab();
    if (activeTab) {
      activeTab.code = '';
      activeTab.lastCompiledCode = null;
      activeTab.lastCompileData = null;
      activeTab.lastCopilotData = null;
      activeTab.editorBackupCode = null;
      activeTab.badgeState = 'idle';
      activeTab.violations = [];
      activeTab.hints = [];
      activeTab.rawOutput = '(no output)';
      activeTab.messageText = 'Editor cleared. Codeholder is idle.';
      activeTab.messageMode = 'neutral';
      activeTab.messagePill = 'EVENT';
      renderTabs();
    }
  });
}
compileBtn.addEventListener('click', runCompile);
exportJsonBtn.addEventListener('click', exportJsonReport);
exportMdBtn.addEventListener('click', exportMarkdownReport);
if (themeToggle) {
  themeToggle.addEventListener('click', toggleTheme);
}

function setSidebarCollapsed(collapsed) {
  if (!appShell) return;
  if (collapsed) {
    appShell.classList.add('sidebar-collapsed');
    localStorage.setItem(SIDEBAR_KEY, 'true');
  } else {
    appShell.classList.remove('sidebar-collapsed');
    localStorage.setItem(SIDEBAR_KEY, 'false');
  }
  setTimeout(() => {
    if (isEnergyEnabled()) {
      drawHistoryChart();
    }
  }, 240);
}

function formatMarkdownLite(text) {
  if (!text) return '';
  // Step 1: Neutralize XSS vectors by escaping raw HTML tags and entities
  const safeText = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  // Step 2: Apply safe subset of markdown rendering
  return safeText
    .replace(/^#### (.*$)/gim, '<h5 style="margin: 8px 0 4px; font-size: 0.88rem; font-weight: 700;">$1</h5>')
    .replace(/^### (.*$)/gim, '<h4 style="margin: 10px 0 6px; font-size: 0.93rem; font-weight: 700;">$1</h4>')
    .replace(/^## (.*$)/gim, '<h3 style="margin: 12px 0 8px; font-size: 1rem; font-weight: 700;">$1</h3>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code style="background: var(--chip); padding: 2px 6px; border-radius: 2px; font-family: \'IBM Plex Mono\', monospace; font-size: 0.82em;">$1</code>')
    .replace(/^\s*[-•]\s+(.*$)/gim, '<li style="margin-left: 18px; margin-bottom: 4px; list-style-type: disc;">$1</li>')
    .replace(/\n\n/g, '<br><br>');
}

function replaceUpdateFirmwareInCode(fullCode, newFunc) {
  if (newFunc.includes('#include') || newFunc.includes('typedef struct') || !fullCode.trim()) {
    return newFunc;
  }
  const match = fullCode.match(/(?:int|void|UpdateStatus|OtaStatus)\s+updateFirmware\s*\([^)]*\)\s*\{/);
  if (!match) {
    return newFunc;
  }
  const startIndex = match.index;
  const braceStart = fullCode.indexOf('{', startIndex);
  let depth = 1;
  let i = braceStart + 1;
  while (i < fullCode.length && depth > 0) {
    if (fullCode[i] === '{') depth++;
    else if (fullCode[i] === '}') depth--;
    i++;
  }
  if (depth === 0) {
    return fullCode.slice(0, startIndex) + newFunc + fullCode.slice(i);
  }
  return newFunc;
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function renderDiagnosticBreakdown(breakdown, noImprovementNeeded) {
  if (!copilotDiagnosticsBreakdown) return;
  copilotDiagnosticsBreakdown.innerHTML = '';

  if (!breakdown || breakdown.length === 0) {
    if (noImprovementNeeded) {
      copilotDiagnosticsBreakdown.innerHTML = `
        <div class="diagnostic-item pass">
          <div class="diagnostic-header-row">
            <div class="diagnostic-meta-left">
              <span class="diagnostic-badge pass">VERIFIED</span>
              <span class="diagnostic-loc">Full Translation Unit</span>
            </div>
            <span class="diagnostic-status-pill pass">PASS</span>
          </div>
          <div class="diagnostic-content-row">
            <div class="diagnostic-issue">All 4 CFG dominance invariants and self-contained rules satisfied.</div>
            <div class="diagnostic-arrow">✓</div>
            <div class="diagnostic-correction">No syntax or security corrections needed.</div>
          </div>
        </div>`;
    } else {
      copilotDiagnosticsBreakdown.innerHTML = '<div style="color: var(--muted); font-size: 0.83rem; padding: 6px;">No diagnostic items available.</div>';
    }
    return;
  }

  for (const item of breakdown) {
    const el = document.createElement('div');
    const isPass = item.status === 'PASS';
    const isPurged = item.status === 'PURGED' || (item.category && item.category.toLowerCase().includes('injection'));
    const itemClass = isPass ? 'pass' : (isPurged ? 'purged' : 'fixed');
    el.className = `diagnostic-item ${itemClass}`;

    let badgeClass = 'violation';
    if (isPass) badgeClass = 'pass';
    else if (isPurged) badgeClass = 'attack';
    else if (item.category && item.category.toLowerCase().includes('external')) badgeClass = 'external';
    else if (item.category && (item.category.toLowerCase().includes('syntax') || item.category.toLowerCase().includes('compiler'))) badgeClass = 'syntax';

    const locText = item.line ? `Line ${item.line}` : (item.location || 'Global / Function');
    const statusText = item.status || (isPass ? 'PASS' : 'FIXED');

    el.innerHTML = `
      <div class="diagnostic-header-row">
        <div class="diagnostic-meta-left">
          <span class="diagnostic-badge ${badgeClass}">${escapeHtml(item.category || 'Diagnostic')}</span>
          <span class="diagnostic-loc">${escapeHtml(locText)}</span>
        </div>
        <span class="diagnostic-status-pill ${itemClass}">${escapeHtml(statusText)}</span>
      </div>
      <div class="diagnostic-content-row">
        <div class="diagnostic-issue">${escapeHtml(item.issue || '')}</div>
        <div class="diagnostic-arrow">${isPass ? '✓' : '➔'}</div>
        <div class="diagnostic-correction">${escapeHtml(item.correction || '')}</div>
      </div>
    `;
    copilotDiagnosticsBreakdown.appendChild(el);
  }
}

function renderCopilotData(data) {
  if (!data) {
    if (copilotPlaceholder) copilotPlaceholder.style.display = 'block';
    if (copilotResults) copilotResults.style.display = 'none';
    return;
  }

  // Hide placeholder, display results
  if (copilotPlaceholder) copilotPlaceholder.style.display = 'none';
  if (copilotResults) copilotResults.style.display = 'grid';

  // 1. Audit Verdict
  if (copilotVerdictBadge) {
    const v = (data.verdict || 'WARNING').toUpperCase().replace(/\s+/g, '_');
    copilotVerdictBadge.textContent = v;
    if (v === 'SAFE') {
      copilotVerdictBadge.className = 'badge passed';
    } else if (v === 'CRITICAL') {
      copilotVerdictBadge.className = 'badge failed';
    } else if (v === 'SYNTAX_ERROR') {
      copilotVerdictBadge.className = 'badge syntax-error';
    } else {
      copilotVerdictBadge.className = 'badge idle';
    }
  }

  // 2. Judge Observations
  if (copilotObservations) {
    copilotObservations.innerHTML = formatMarkdownLite(data.observations);
  }

  // 3. Diagnostic Breakdown & Applied Corrections Box
  const isNoOp = data.status === 'NO_IMPROVEMENT_NEEDED' || data.no_improvement_needed === true;
  renderDiagnosticBreakdown(data.diagnostic_breakdown, isNoOp);

  // 4. Conditional Code Generation & No-Op Suppression
  const codeTitle = copilotCodeSection ? copilotCodeSection.querySelector('.copilot-section-title') : null;
  if (isNoOp) {
    if (copilotNoOpBanner) copilotNoOpBanner.style.display = 'flex';
    if (copilotCodeSection) copilotCodeSection.style.display = 'grid';
    if (codeTitle) codeTitle.textContent = 'Verified Compliant Code';
    if (replaceCodeBtn) replaceCodeBtn.style.display = 'none';
    if (copilotCodeSnippet) {
      copilotCodeSnippet.textContent = data.full_code || data.code_snippet || (codeInput ? codeInput.value : '');
    }
  } else {
    if (copilotNoOpBanner) copilotNoOpBanner.style.display = 'none';
    if (copilotCodeSection) copilotCodeSection.style.display = 'grid';
    if (codeTitle) codeTitle.textContent = 'Improved Code View';
    if (replaceCodeBtn) replaceCodeBtn.style.display = 'inline-block';
    if (copilotCodeSnippet) {
      copilotCodeSnippet.textContent = data.code_snippet || '// No improved code required.';
    }
  }
}

async function runAdvisoryAudit(options = {}) {
  const code = codeInput ? codeInput.value : '';
  if (!code.trim()) {
    setMessage('Firmware source is empty. Please enter code first.', 'bad');
    return;
  }

  // If code in editor has not been compiled yet or was changed, compile first so results are accurate!
  if (!options.fromCompile && lastCompiledCode !== code) {
    await runCompile();
    return;
  }

  if (isAuditing) return;
  isAuditing = true;

  if (runCopilotBtn) {
    runCopilotBtn.disabled = true;
    runCopilotBtn.innerHTML = '<span class="copilot-btn-icon">⏳</span> Auditing...';
  }

  const activeTab = getActiveTab();
  const currentFilename = (activeTab && activeTab.filename) || (filenameInput ? filenameInput.value.trim() : 'firmware_demo.c') || 'firmware_demo.c';

  try {
    const violations = options.violations || lastCompileData?.violations || [];
    const hints = options.hints || lastCompileData?.hints || [];
    const rawOutputText = options.rawOutput !== undefined ? options.rawOutput : (lastCompileData?.rawOutput || (rawOutput ? rawOutput.textContent : ''));

    const payload = {
      code,
      violations,
      hints,
      policy: policySelect ? policySelect.value : 'original_protocol.json',
      filename: currentFilename,
      language: (currentFilename && currentFilename.endsWith('.py')) ? 'python' : currentLanguage,
      rawOutput: rawOutputText,
    };

    const res = await fetch('/api/advisory-copilot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok || !data.ok) {
      if (copilotObservations) {
        copilotObservations.innerHTML = `<span style="color: var(--bad);">Analysis failed: ${data.error || 'Unknown error'}</span>`;
      }
      return;
    }

    lastCopilotData = data;
    if (activeTab) {
      activeTab.lastCopilotData = data;
    }

    renderCopilotData(data);

    // Reset restore button on fresh analysis if code matches original backup
    if (editorBackupCode === null && restoreCodeBtn) {
      restoreCodeBtn.style.display = 'none';
    }

  } catch (err) {
    if (copilotObservations) {
      copilotObservations.textContent = `Error running AI analysis: ${err.message}`;
    }
  } finally {
    isAuditing = false;
    if (runCopilotBtn) {
      runCopilotBtn.disabled = false;
      runCopilotBtn.innerHTML = '<span class="copilot-btn-icon">⚡</span> Run Advisory Audit';
    }
  }
}

function initCopilotEvents() {
  if (runCopilotBtn) {
    runCopilotBtn.addEventListener('click', () => runAdvisoryAudit());
  }

  // Replace code in editor
  if (replaceCodeBtn && copilotCodeSnippet) {
    replaceCodeBtn.addEventListener('click', () => {
      const improvedCode = copilotCodeSnippet.textContent.trim();
      if (!codeInput) return;
      editorBackupCode = codeInput.value;
      if (lastCopilotData && lastCopilotData.full_code) {
        codeInput.value = lastCopilotData.full_code;
      } else if (improvedCode) {
        codeInput.value = replaceUpdateFirmwareInCode(codeInput.value, improvedCode);
      } else {
        return;
      }
      lastCompiledCode = null; // Mark code as modified so next audit/compile knows
      const activeTab = getActiveTab();
      if (activeTab) {
        activeTab.code = codeInput.value;
        activeTab.editorBackupCode = editorBackupCode;
        activeTab.lastCompiledCode = null;
      }
      updateLineNumbers();
      updateHighlighting();
      if (restoreCodeBtn) {
        restoreCodeBtn.style.display = 'inline-block';
      }
      setMessage('Replaced code in editor with improved version. Click "Restore Code" to revert or "Run secure-clang" to compile.', 'good');
    });
  }

  // Restore original code in editor
  if (restoreCodeBtn) {
    restoreCodeBtn.addEventListener('click', () => {
      if (editorBackupCode !== null && codeInput) {
        codeInput.value = editorBackupCode;
        const activeTab = getActiveTab();
        if (activeTab) {
          activeTab.code = editorBackupCode;
          activeTab.editorBackupCode = null;
          activeTab.lastCompiledCode = null;
        }
        editorBackupCode = null;
        lastCompiledCode = null; // Mark code as modified
        updateLineNumbers();
        updateHighlighting();
        restoreCodeBtn.style.display = 'none';
        setMessage('Original editor code restored.', 'good');
      }
    });
  }

  // Copy code snippet to clipboard
  if (copySnippetBtn && copilotCodeSnippet) {
    copySnippetBtn.addEventListener('click', async () => {
      const code = copilotCodeSnippet.textContent;
      if (!code) return;
      try {
        await navigator.clipboard.writeText(code);
        if (copyBtnText) {
          const original = copyBtnText.textContent;
          copyBtnText.textContent = '✓ Copied!';
          setTimeout(() => { copyBtnText.textContent = original; }, 2000);
        }
      } catch (err) {
        const ta = document.createElement('textarea');
        ta.value = code;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        if (copyBtnText) {
          copyBtnText.textContent = '✓ Copied!';
          setTimeout(() => { copyBtnText.textContent = 'Copy'; }, 2000);
        }
      }
    });
  }
}

function initSidebar() {
  if (sidebarCollapseBtn) {
    sidebarCollapseBtn.addEventListener('click', () => setSidebarCollapsed(true));
  }
  if (sidebarExpandBtn) {
    sidebarExpandBtn.addEventListener('click', () => setSidebarCollapsed(false));
  }
  const isCollapsed = localStorage.getItem(SIDEBAR_KEY) === 'true';
  if (isCollapsed) {
    setSidebarCollapsed(true);
  }
}

const WORKSPACE_SPLIT_KEY = 'ota-workspace-split';

function initWorkspaceResizer() {
  const resizer = document.getElementById('workspaceResizer');
  const grid = document.getElementById('workspaceGrid');
  const stagePanel = document.getElementById('stagePanel');
  const outputPanel = document.getElementById('outputPanel');
  if (!resizer || !grid || !stagePanel || !outputPanel) return;

  let isDragging = false;
  const resizerWidth = 10;
  const minPanelWidth = 260;

  const restoreSplit = () => {
    if (window.innerWidth > 1100) {
      try {
        const saved = parseFloat(localStorage.getItem(WORKSPACE_SPLIT_KEY));
        if (saved && saved >= 20 && saved <= 80) {
          grid.style.gridTemplateColumns = `${saved}% ${resizerWidth}px ${(100 - saved).toFixed(2)}%`;
          return;
        }
      } catch (_) {}
      grid.style.gridTemplateColumns = `1fr ${resizerWidth}px 1fr`;
    } else {
      grid.style.gridTemplateColumns = '';
    }
  };

  restoreSplit();
  window.addEventListener('resize', restoreSplit);

  resizer.addEventListener('mousedown', (e) => {
    if (window.innerWidth <= 1100) return;
    isDragging = true;
    resizer.classList.add('dragging');
    document.body.classList.add('resizing-col');
    e.preventDefault();
  });

  window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const gridRect = grid.getBoundingClientRect();
    const availableWidth = gridRect.width - resizerWidth;
    if (availableWidth <= minPanelWidth * 2) return;

    let leftPx = e.clientX - gridRect.left;
    if (leftPx < minPanelWidth) leftPx = minPanelWidth;
    if (leftPx > availableWidth - minPanelWidth) leftPx = availableWidth - minPanelWidth;

    const leftPct = (leftPx / availableWidth) * 100;
    const rightPct = 100 - leftPct;

    grid.style.gridTemplateColumns = `${leftPct.toFixed(2)}% ${resizerWidth}px ${rightPct.toFixed(2)}%`;
    try {
      localStorage.setItem(WORKSPACE_SPLIT_KEY, leftPct.toFixed(2));
    } catch (_) {}
  });

  const stopDragging = () => {
    if (isDragging) {
      isDragging = false;
      resizer.classList.remove('dragging');
      document.body.classList.remove('resizing-col');
    }
  };

  window.addEventListener('mouseup', stopDragging);
  window.addEventListener('mouseleave', stopDragging);

  resizer.addEventListener('dblclick', () => {
    grid.style.gridTemplateColumns = `1fr ${resizerWidth}px 1fr`;
    try {
      localStorage.removeItem(WORKSPACE_SPLIT_KEY);
    } catch (_) {}
  });

  resizer.addEventListener('keydown', (e) => {
    if (window.innerWidth <= 1100) return;
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      const gridRect = grid.getBoundingClientRect();
      const availableWidth = gridRect.width - resizerWidth;
      const currentLeft = stagePanel.getBoundingClientRect().width;
      const delta = e.key === 'ArrowLeft' ? -30 : 30;
      let newLeft = Math.max(minPanelWidth, Math.min(availableWidth - minPanelWidth, currentLeft + delta));
      const leftPct = (newLeft / availableWidth) * 100;
      grid.style.gridTemplateColumns = `${leftPct.toFixed(2)}% ${resizerWidth}px ${(100 - leftPct).toFixed(2)}%`;
      try {
        localStorage.setItem(WORKSPACE_SPLIT_KEY, leftPct.toFixed(2));
      } catch (_) {}
      e.preventDefault();
    }
  });
}

async function setTargetLanguage(lang, switchSample = false) {
  currentLanguage = (lang === 'python') ? 'python' : 'c';
  localStorage.setItem(LANG_STORAGE_KEY, currentLanguage);

  if (langBtnC && langBtnPy) {
    if (currentLanguage === 'python') {
      langBtnPy.classList.add('active');
      langBtnC.classList.remove('active');
      langBtnPy.setAttribute('aria-pressed', 'true');
      langBtnC.setAttribute('aria-pressed', 'false');
    } else {
      langBtnC.classList.add('active');
      langBtnPy.classList.remove('active');
      langBtnC.setAttribute('aria-pressed', 'true');
      langBtnPy.setAttribute('aria-pressed', 'false');
    }
  }

  if (compileBtn) {
    compileBtn.textContent = currentLanguage === 'python' ? 'Run secure-python' : 'Run secure-clang';
  }

  const dropExts = document.getElementById('dropzoneFileExts');
  if (dropExts) {
    dropExts.textContent = currentLanguage === 'python'
      ? 'or click to browse (.py, .txt)'
      : 'or click to browse (.c, .h, .txt)';
  }

  renderDemoButtons();
  await fetchSamples(currentLanguage);

  if (switchSample) {
    const activeTab = getActiveTab();
    const isPy = currentLanguage === 'python';
    const targetDefault = isPy ? 'secure.py' : 'secure.c';
    if (activeTab && (!activeTab.code.trim() || activeTab.filename.endsWith(isPy ? '.c' : '.py'))) {
      sampleSelect.value = targetDefault;
      await loadSample();
    }
  }

  updateHighlighting();
}

function initLanguageToggle() {
  if (langBtnC) {
    langBtnC.addEventListener('click', () => {
      if (currentLanguage !== 'c') {
        setTargetLanguage('c', true);
      }
    });
  }
  if (langBtnPy) {
    langBtnPy.addEventListener('click', () => {
      if (currentLanguage !== 'python') {
        setTargetLanguage('python', true);
      }
    });
  }
}

// Ensure action buttons exist as early as possible
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', ensureActionButtons);
} else {
  ensureActionButtons();
}

(async function init() {
  applyTheme(getInitialTheme());
  initSidebar();
  initWorkspaceResizer();
  initEnergyToggle();
  initEditorEvents();
  initDropzone();
  initTabs();
  ensureActionButtons();
  initLanguageToggle();
  await setTargetLanguage(currentLanguage, false);
  updateLineNumbers();
  updateHighlighting();
  await fetchPolicies();
  renderHistory();
  initCopilotEvents();
})();
