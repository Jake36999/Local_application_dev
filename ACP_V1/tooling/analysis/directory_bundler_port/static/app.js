// API Configuration
const API_BASE_URL = window.location.origin === 'file://' ? 'http://localhost:8000' : window.location.origin;
let currentScanUid = null;
let pollInterval = null;
let lastScanConfig = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkServerStatus();
    refreshHistory();
    refreshModels();
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    document.getElementById('enableLMStudio').addEventListener('change', (e) => {
        document.getElementById('aiPersonaSection').style.display = 
            e.target.checked ? 'block' : 'none';
    });

    const lmstudioUrlInput = document.getElementById('lmstudioUrl');
    const lmBaseUrlInput = document.getElementById('lmBaseUrl');
    if (lmstudioUrlInput && lmBaseUrlInput) {
        lmstudioUrlInput.addEventListener('input', () => {
            lmBaseUrlInput.value = normalizeLmBaseUrl(lmstudioUrlInput.value);
        });
    }
}

// Normalize LM Studio base URL (strip API path)
function normalizeLmBaseUrl(url) {
    if (!url) return 'http://localhost:1234';
    return url.replace(/\s+/g, '').replace(/\/v1\/chat\/completions$/, '').replace(/\/$/, '') || 'http://localhost:1234';
}

// Get LM Studio base URL from input
function getLmBaseUrl() {
    const input = document.getElementById('lmBaseUrl');
    if (!input) return 'http://localhost:1234';
    const normalized = normalizeLmBaseUrl(input.value);
    input.value = normalized;
    return normalized;
}

// Refresh LM Studio models list
async function refreshModels() {
    const statusEl = document.getElementById('lmStatus');
    const listEl = document.getElementById('modelsList');
    if (!statusEl || !listEl) return;

    const baseUrl = getLmBaseUrl();
    statusEl.textContent = `Checking ${baseUrl}...`;
    listEl.innerHTML = '<p>Loading models...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/lmstudio/models?base_url=${encodeURIComponent(baseUrl)}`);
        if (!response.ok) {
            throw new Error('LM Studio unavailable');
        }
        const payload = await response.json();
        const models = payload.data || payload.models || [];
        const activeModel = payload.active_model || payload.activeModel || null;
        statusEl.textContent = `Connected to ${baseUrl}`;
        renderModels(models, activeModel);
    } catch (error) {
        console.error('Model refresh failed:', error);
        statusEl.textContent = 'LM Studio unavailable';
        listEl.innerHTML = '<div class="alert alert-danger">Cannot reach LM Studio. Check URL and server.</div>';
    }
}

// Render models list with load/unload controls
function renderModels(models, activeModel) {
    const listEl = document.getElementById('modelsList');
    if (!listEl) return;

    if (!Array.isArray(models) || models.length === 0) {
        listEl.innerHTML = '<div class="empty-state">No models returned by LM Studio.</div>';
        return;
    }

    let html = '';
    models.forEach(model => {
        const modelId = model.id || model.model || model.name || 'unknown-model';
        const isLoaded = model.loaded || model.isLoaded || model.status === 'loaded' || activeModel === modelId;
        const sizeLabel = model.size ? `${(model.size / (1024 * 1024)).toFixed(1)} MB` : (model.size_mb ? `${model.size_mb.toFixed(1)} MB` : '');

        html += `
            <div class="model-row">
                <div>
                    <div class="model-name">${modelId}</div>
                    <div class="model-meta">${sizeLabel || 'Size unknown'}${isLoaded ? ' • Loaded' : ''}</div>
                </div>
                <div class="model-actions">
                    <button class="btn btn-small" ${isLoaded ? 'disabled' : ''} onclick="handleModelAction('load', '${modelId}')">Load</button>
                    <button class="btn btn-small btn-secondary" ${!isLoaded ? 'disabled' : ''} onclick="handleModelAction('unload', '${modelId}')">Unload</button>
                </div>
            </div>
        `;
    });

    listEl.innerHTML = html;
}

// Trigger LM Studio load/unload
async function handleModelAction(action, modelId) {
    const baseUrl = getLmBaseUrl();
    const statusEl = document.getElementById('lmStatus');
    if (statusEl) {
        statusEl.textContent = `${action === 'load' ? 'Loading' : 'Unloading'} ${modelId}...`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/lmstudio/model`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, model: modelId, base_url: baseUrl })
        });

        if (!response.ok) {
            throw new Error('LM Studio action failed');
        }

        await response.json().catch(() => ({}));
        if (statusEl) {
            statusEl.textContent = `${modelId} ${action === 'load' ? 'loaded' : 'unloaded'} via LM Studio`;
        }
        refreshModels();
    } catch (error) {
        console.error('Model action failed:', error);
        if (statusEl) {
            statusEl.textContent = 'LM Studio action failed';
        }
    }
}

// Check Server Status
async function checkServerStatus() {
    const statusIndicator = document.getElementById('serverStatus');
    const statusDot = statusIndicator.querySelector('.status-dot');
    const statusText = statusIndicator.querySelector('.status-text');
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/status?uid=test`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            statusDot.classList.remove('offline');
            statusText.textContent = 'Server Online';
        } else {
            throw new Error('Server not responding');
        }
    } catch (error) {
        statusDot.classList.add('offline');
        statusText.textContent = 'Server Offline';
        console.error('Server status check failed:', error);
    }
}

// Start Scan
async function startScan() {
    const targetPath = document.getElementById('targetPath').value.trim() || '.';
    
    // Validate LM Studio URL if enabled
    const enableLM = document.getElementById('enableLMStudio').checked;
    let lmstudioUrl = undefined;
    
    if (enableLM) {
        const urlInput = document.getElementById('lmstudioUrl')?.value.trim();
        if (!urlInput) {
            alert('Please enter LM Studio URL or disable AI analysis');
            return;
        }
        // Ensure URL has proper endpoint
        lmstudioUrl = urlInput.endsWith('/v1/chat/completions') 
            ? urlInput 
            : urlInput.replace(/\/$/, '') + '/v1/chat/completions';
    }
    
    const config = {
        target_path: targetPath,
        mode: document.getElementById('scanMode').value,
        max_file_size_mb: parseFloat(document.getElementById('maxFileSize').value) || 50,
        include_tests: document.getElementById('includeTests').checked,
        include_docs: document.getElementById('includeDocs').checked,
        include_config: document.getElementById('includeConfig').checked,
        lmstudio_enabled: enableLM,
        ai_persona: document.getElementById('aiPersona')?.value || 'default',
        lmstudio_url: lmstudioUrl,
        bypass_cache: document.getElementById('bypassCache')?.checked || false
    };
    
    // Store config for potential retry
    lastScanConfig = config;
    
    try {
        // Show progress panel
        const progressPanel = document.getElementById('progressPanel');
        progressPanel.style.display = 'block';
        updateProgress('Initializing scan...', 0);
        
        // Start scan
        const response = await fetch(`${API_BASE_URL}/api/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        currentScanUid = data.uid;
        
        updateProgress(`Scan started (UID: ${currentScanUid})`, 10);
        
        // Start polling for progress
        startProgressPolling(currentScanUid);
        
    } catch (error) {
        console.error('Scan failed:', error);
        const errorMsg = `Failed to start scan: ${error.message}`;
        alert(errorMsg);
        document.getElementById('progressPanel').style.display = 'none';
        updateProgress('Scan failed ✗', 0, errorMsg);
    }
}

// Retry Last Scan
function retryScan() {
    if (Object.keys(lastScanConfig).length === 0) {
        alert('No previous scan to retry');
        return;
    }
    // Restore form values and start scan
    document.getElementById('targetPath').value = lastScanConfig.target_path || '.';
    document.getElementById('scanMode').value = lastScanConfig.mode || 'full';
    document.getElementById('maxFileSize').value = lastScanConfig.max_file_size_mb || 50;
    document.getElementById('enableLMStudio').checked = lastScanConfig.lmstudio_enabled || false;
    if (lastScanConfig.lmstudio_url) {
        document.getElementById('lmstudioUrl').value = lastScanConfig.lmstudio_url;
    }
    document.getElementById('aiPersona').value = lastScanConfig.ai_persona || 'default';
    startScan();
}

// Update Progress Display
function updateProgress(status, percentage, details = '') {
    document.getElementById('progressStatus').textContent = status;
    const progressBar = document.getElementById('progressBar');
    progressBar.style.width = `${percentage}%`;
    progressBar.textContent = `${percentage}%`;
    document.getElementById('progressDetails').textContent = details;
}

// Start Progress Polling
function startProgressPolling(uid) {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    
    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/status?uid=${uid}`);
            const data = await response.json();
            
            if (data.status === 'processing') {
                const progress = data.progress || 50;
                updateProgress(
                    `Processing... (${data.current || 0}/${data.total || 0} files)`,
                    progress,
                    `Status: ${data.phase || 'analyzing'}`
                );
            } else if (data.status === 'completed') {
                clearInterval(pollInterval);
                updateProgress('Scan completed! ✓', 100, 'Loading results...');
                
                setTimeout(() => {
                    loadScanResults(uid);
                    refreshHistory();
                    document.getElementById('progressPanel').style.display = 'none';
                }, 1000);
            } else if (data.status === 'failed') {
                clearInterval(pollInterval);
                updateProgress('Scan failed ✗', 0, data.error || 'Unknown error');
                setTimeout(() => {
                    document.getElementById('progressPanel').style.display = 'none';
                }, 3000);
            }
        } catch (error) {
            console.error('Progress polling error:', error);
        }
    }, 1000); // Poll every second
}

// Load Scan Results
async function loadScanResults(uid) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/results?uid=${uid}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data, uid);
        
    } catch (error) {
        console.error('Failed to load results:', error);
        alert(`Failed to load results: ${error.message}`);
    }
}

// Display Results
function displayResults(data, uid) {
    // Show results panel
    document.getElementById('resultsPanel').style.display = 'block';
    
    // Display Summary
    displaySummary(data);
    
    // Load additional data
    loadFilesList(uid);
    loadTreeView(uid);
    loadDuplicates(uid);
    loadSecurityFindings(uid);
    
    // Scroll to results
    document.getElementById('resultsPanel').scrollIntoView({ behavior: 'smooth' });
}

// Display Summary
function displaySummary(data) {
    const summaryContent = document.getElementById('summaryContent');
    
    const html = `
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">${data.total_files || 0}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${(data.total_size_mb || 0).toFixed(2)} MB</div>
                <div class="stat-label">Total Size</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.total_chunks || 0}</div>
                <div class="stat-label">Chunks</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.duplicates_detected ? 'Yes' : 'No'}</div>
                <div class="stat-label">Duplicates</div>
            </div>
        </div>
        
        <h3>Scan Information</h3>
        <table style="width: 100%; margin-top: 15px;">
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid var(--border-color);"><strong>UID:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid var(--border-color);">${data.scan_uid}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid var(--border-color);"><strong>Timestamp:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid var(--border-color);">${formatTimestamp(data.timestamp)}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid var(--border-color);"><strong>Root Path:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid var(--border-color);">${data.root_path}</td>
            </tr>
            <tr>
                <td style="padding: 8px;"><strong>Mode:</strong></td>
                <td style="padding: 8px;">${data.config_used?.mode || 'N/A'}</td>
            </tr>
        </table>
    `;
    
    summaryContent.innerHTML = html;
}

// Load Files List
async function loadFilesList(uid) {
    const filesContent = document.getElementById('filesContent');
    filesContent.innerHTML = '<p>Loading files...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/files?uid=${uid}`);
        const files = await response.json();

        if (!Array.isArray(files) || files.length === 0) {
            filesContent.innerHTML = '<p>No files found for this scan.</p>';
            return;
        }

        let html = '<div class="file-list">';
        html += '<div class="file-list-header">';
        html += '<span>File</span><span>Type</span><span>Size (MB)</span><span>Action</span>';
        html += '</div>';

        files.forEach(file => {
            html += `
                <div class="file-item">
                    <span class="file-path">${file.path || file.name || ''}</span>
                    <span class="file-type">${file.file_type || 'unknown'}</span>
                    <span class="file-size">${(file.size_mb || 0).toFixed(4)}</span>
                    <button class="btn btn-small" onclick="showFileDetails('${uid}', '${file.file_id}')">View</button>
                </div>
            `;
        });

        html += '</div>';
        html += '<div id="fileDetails" class="file-details"></div>';
        filesContent.innerHTML = html;
        
    } catch (error) {
        filesContent.innerHTML = '<p class="alert alert-danger">Failed to load files list</p>';
    }
}

// Show File Details
async function showFileDetails(uid, fileId) {
    const detailsContainer = document.getElementById('fileDetails');
    if (!detailsContainer) return;
    detailsContainer.innerHTML = '<p>Loading file details...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/file?uid=${uid}&file_id=${fileId}`);
        if (!response.ok) {
            throw new Error('Failed to load file details');
        }
        const fileData = await response.json();

        const analysis = fileData.analysis || {};
        const securityFindings = analysis.security_findings || [];
        const dangerousCalls = analysis.dangerous_calls || [];

        let html = `
            <h3>File Details</h3>
            <table style="width: 100%; margin-top: 10px;">
                <tr><td><strong>Path:</strong></td><td>${fileData.path || ''}</td></tr>
                <tr><td><strong>Size:</strong></td><td>${(fileData.size_mb || 0).toFixed(4)} MB</td></tr>
                <tr><td><strong>Type:</strong></td><td>${fileData.file_type || 'unknown'}</td></tr>
                <tr><td><strong>Extension:</strong></td><td>${fileData.extension || ''}</td></tr>
            </table>
        `;

        if (securityFindings.length || dangerousCalls.length) {
            html += '<h4>Security Findings</h4>';
            html += '<ul>';
            securityFindings.forEach(item => {
                html += `<li>${item}</li>`;
            });
            dangerousCalls.forEach(call => {
                html += `<li>Dangerous call: ${call.function || ''} (line ${call.line || 'unknown'})</li>`;
            });
            html += '</ul>';
        }

        detailsContainer.innerHTML = html;
    } catch (error) {
        detailsContainer.innerHTML = '<p class="alert alert-danger">Failed to load file details</p>';
    }
}

// Load Tree View
async function loadTreeView(uid) {
    const treeContent = document.getElementById('treeContent');
    treeContent.innerHTML = '<p>Loading tree...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/tree?uid=${uid}`);
        if (!response.ok) {
            throw new Error('Failed to load tree');
        }
        const treeData = await response.json();
        treeContent.innerHTML = renderTree(treeData);
        
    } catch (error) {
        treeContent.innerHTML = '<p class="alert alert-danger">Failed to load tree view</p>';
    }
}

function renderTree(nodes) {
    if (!Array.isArray(nodes) || nodes.length === 0) {
        return '<p>No tree data available.</p>';
    }

    const buildList = (items) => {
        let html = '<ul class="tree-list">';
        items.forEach(item => {
            const icon = item.type === 'directory' ? '📁' : '📄';
            html += `<li>${icon} ${item.name}`;
            if (item.children) {
                html += buildList(item.children);
            }
            html += '</li>';
        });
        html += '</ul>';
        return html;
    };

    return buildList(nodes);
}

// Load Duplicates
async function loadDuplicates(uid) {
    const duplicatesContent = document.getElementById('duplicatesContent');
    duplicatesContent.innerHTML = '<p>Loading duplicates...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/labels?uid=${uid}`);
        if (!response.ok) {
            throw new Error('Failed to load labels');
        }
        const labels = await response.json();
        const duplicates = labels.duplicates || {};
        const duplicateGroups = Object.values(duplicates).filter(group => Array.isArray(group) && group.length > 1);

        if (duplicateGroups.length === 0) {
            duplicatesContent.innerHTML = '<p>No duplicates detected.</p>';
            return;
        }

        let html = `<p>Duplicate groups: ${duplicateGroups.length}</p>`;
        duplicateGroups.forEach((group, index) => {
            html += `<div class="duplicate-group"><strong>Group ${index + 1}:</strong> ${group.join(', ')}</div>`;
        });
        duplicatesContent.innerHTML = html;
        
    } catch (error) {
        duplicatesContent.innerHTML = '<p class="alert alert-danger">Failed to load duplicates</p>';
    }
}

// Load Security Findings
async function loadSecurityFindings(uid) {
    const securityContent = document.getElementById('securityContent');
    securityContent.innerHTML = '<p>Loading security analysis...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/files?uid=${uid}&include_analysis=1`);
        if (!response.ok) {
            throw new Error('Failed to load security findings');
        }
        const files = await response.json();

        let findingsCount = 0;
        let dangerousCount = 0;

        files.forEach(file => {
            const analysis = file.analysis || {};
            const findings = analysis.security_findings || [];
            const dangerous = analysis.dangerous_calls || [];
            findingsCount += findings.length;
            dangerousCount += dangerous.length;
        });

        securityContent.innerHTML = `
            <div class="alert alert-info">
                <strong>Security Summary</strong>
                <p>Total security findings: ${findingsCount}</p>
                <p>Total dangerous calls: ${dangerousCount}</p>
            </div>
            <p>Check the Files tab and select a file for detailed findings.</p>
        `;
        
    } catch (error) {
        securityContent.innerHTML = '<p class="alert alert-danger">Failed to load security findings</p>';
    }
}

// Refresh History
async function refreshHistory() {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = '<p>Loading history...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/history`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch history');
        }
        
        const history = await response.json();
        
        if (!history || history.length === 0) {
            historyList.innerHTML = '<div class="empty-state">No scans yet. Start your first scan above!</div>';
            return;
        }
        
        let html = '';
        history.reverse().forEach(item => {
            html += `
                <div class="history-item" onclick="loadScanResults('${item.uid}')">
                    <div class="history-item-header">
                        <span class="history-item-uid">📦 ${item.uid}</span>
                        <span class="history-item-time">${formatTimestamp(item.timestamp)}</span>
                    </div>
                    <div class="history-item-details">
                        ${item.path} | ${item.file_count || 0} files | Mode: ${item.mode}
                    </div>
                </div>
            `;
        });
        
        historyList.innerHTML = html;
        
    } catch (error) {
        console.error('Failed to load history:', error);
        historyList.innerHTML = '<div class="empty-state">Failed to load history</div>';
    }
}

// Switch Tabs
function switchTab(tabName) {
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + 'Tab').classList.add('active');
    
    // Set button active
    const activeButton = document.querySelector(`.tab-btn[data-tab="${tabName}"]`);
    if (activeButton) {
        activeButton.classList.add('active');
    }
}

// Close Results
function closeResults() {
    document.getElementById('resultsPanel').style.display = 'none';
}

// Clear Form
function clearForm() {
    document.getElementById('targetPath').value = '.';
    document.getElementById('scanMode').value = 'quick';
    document.getElementById('maxFileSize').value = '50';
    document.getElementById('includeTests').checked = true;
    document.getElementById('includeDocs').checked = true;
    document.getElementById('includeConfig').checked = true;
    document.getElementById('enableLMStudio').checked = false;
    document.getElementById('aiPersonaSection').style.display = 'none';
}

// Browse Directory (placeholder - would need electron or file API)
function browseDirectory() {
    alert('Directory browsing requires a file dialog.\n\nFor now, please manually enter the full path in the input field.\n\nExample: C:\\Users\\YourName\\Documents\\MyProject');
}

// Format Timestamp
function formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString();
}

// Auto-refresh history every 30 seconds
setInterval(() => {
    if (!pollInterval) { // Only refresh when not actively scanning
        refreshHistory();
    }
}, 30000);
