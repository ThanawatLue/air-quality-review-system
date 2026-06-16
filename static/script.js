let allRooms = [];
let roomsByArea = {};
let selectedRooms = new Set();
let currentArea = null;
let isSyncing = false;
let currentSourceMode = 'phase1';
let lastAnalysisPlotResult = null;
let currentJobId = null;

function setPlotBtnEnabled(enabled) {
    const btn = document.getElementById('plotBtn');
    if (!btn) return;
    btn.disabled = !enabled;
    btn.style.opacity = enabled ? '' : '0.4';
    btn.style.cursor  = enabled ? '' : 'not-allowed';
    btn.style.filter  = enabled ? '' : 'grayscale(1)';
    btn.style.pointerEvents = enabled ? '' : 'none';
}

function setSourceMode(mode) {
    currentSourceMode = mode;
    const p1 = document.getElementById('modePhase1Btn');
    const p2 = document.getElementById('modePhase2Btn');
    if (p1 && p2) {
        p1.style.background = mode === 'phase1' ? 'var(--accent)' : '';
        p1.style.color       = mode === 'phase1' ? '#fff' : '';
        p2.style.background  = mode === 'phase2' ? 'var(--accent)' : '';
        p2.style.color        = mode === 'phase2' ? '#fff' : '';
    }
    // Reset state when switching mode
    document.getElementById('sidebarDateTime').style.display = 'none';
    document.getElementById('roomSelectionSection').style.display = 'none';
    document.getElementById('folderPath').value = '';
    lastAnalysisPlotResult = null;
    currentJobId = null;
    setPlotBtnEnabled(false);
}

function showLoading(show = true) {
    const el = document.getElementById('loadingOverlay');
    if (el) {
        if (show) el.classList.add('active');
        else el.classList.remove('active');
    }
}

// Sidebar Toggle & Graph Resize Logic
document.getElementById('sidebarToggle').addEventListener('click', () => {
    document.body.classList.toggle('sidebar-collapsed');
    setTimeout(() => {
        const plotIds = ['violationTimelineChart', 'summaryViolationChart', 'plotTemp', 'plotHum', 'plotPress', 'violationHeatmap'];
        plotIds.forEach(id => {
            const el = document.getElementById(id);
            if (el && el.data) Plotly.Plots.resize(el);
        });
        window.dispatchEvent(new Event('resize'));
    }, 450); 
});

// Dark Mode Toggle
document.getElementById('darkModeToggle').addEventListener('click', () => {
    const isDark = document.body.getAttribute('data-theme') === 'dark';
    document.body.setAttribute('data-theme', isDark ? 'light' : 'dark');
    document.getElementById('darkModeToggle').innerHTML = isDark ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
    
    // Update Plotly Templates
    const newTemplate = isDark ? 'plotly_white' : 'plotly_dark';
    const plotIds = ['violationTimelineChart', 'summaryViolationChart', 'plotTemp', 'plotHum', 'plotPress', 'violationHeatmap'];
    plotIds.forEach(id => {
        const el = document.getElementById(id);
        if (el && el.data) {
            Plotly.relayout(id, { template: newTemplate });
        }
    });
});

function updateAiMsg(step, msg) {
    const el = document.getElementById(`aiHelper${step}`);
    if (el) el.innerText = msg;
}

async function browseFolder() {
    const res = await fetch('/browse-folder');
    const data = await res.json();
    if (data.path) {
        document.getElementById('folderPath').value = data.path;
        updateAiMsg(1, "AQR Program: Analysis path confirmed. Scanning metadata...");
        checkReadyForScan();
    }
}

async function browseFile() {
    const res = await fetch('/browse-file');
    const data = await res.json();
    if (data.path) {
        document.getElementById('setpointPath').value = data.path;
        updateAiMsg(1, "AQR Program: Limit file linked. System ready for temporal definition.");
        checkReadyForScan();
    }
}

async function checkReadyForScan() {
    const folder = document.getElementById('folderPath').value;
    if (folder) {
        showLoading(true);
        try {
            const res = await fetch('/get-file-info', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ folder_path: folder, source_mode: currentSourceMode })
            });
            const data = await res.json();
            if (data.error) {
                if (data.error.includes('ERR-001')) {
                    showErrorModal('Header Missing Error', 'ERR-001', data.error);
                } else if (data.error.includes('ERR-003')) {
                    showErrorModal('Invalid Configuration Error', 'ERR-003', data.error);
                } else if (data.error.includes('ERR-005')) {
                    showErrorModal('Invalid File Format', 'ERR-005', data.error);
                } else if (data.error.includes('ERR-006')) {
                    showErrorModal('Logical Constraint Error', 'ERR-006', data.error);
                } else if (data.error.includes('ERR-010')) {
                    showErrorModal('No Matching Files Found', 'ERR-010', data.error);
                } else {
                    showErrorModal('Error', 'ERR-UNKNOWN', data.error);
                }
                return;
            }
            document.getElementById('sidebarDateTime').style.display = 'block';
            const start = new Date(data.default_start_end);
            start.setHours(0, 0, 0, 0);
            const end = new Date(data.default_start_end);
            end.setHours(23, 55, 0, 0);
            document.getElementById('startDate').value = formatDateTimeLocal(start);
            document.getElementById('endDate').value = formatDateTimeLocal(end);
            updateAiMsg(2, "AQR Program: Metadata scan complete. Define period to load rooms.");
        } finally { showLoading(false); }
    }
}

function formatDateTimeLocal(date) {
    const pad = (num) => String(num).padStart(2, '0');
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

document.getElementById('availableSearch').addEventListener('input', renderAvailableRooms);
document.getElementById('selectedSearch').addEventListener('input', renderSelectedRooms);
document.getElementById('areaSearch').addEventListener('input', () => {
    const search = document.getElementById('areaSearch').value.toLowerCase();
    Array.from(document.getElementById('areaList').children).forEach(li => {
        li.style.display = li.innerText.toLowerCase().includes(search) ? '' : 'none';
    });
});

document.getElementById('loadRoomsBtn').addEventListener('click', async () => {
    const folder = document.getElementById('folderPath').value;
    const setpoint = document.getElementById('setpointPath').value;
    const start = document.getElementById('startDate').value;
    const end = document.getElementById('endDate').value;
    if (!setpoint) return showErrorModal('Missing Limit File', 'ERR-002', 'AQR Program: Please select a limit file (.xlsx) first.');
    lastAnalysisPlotResult = null;
    currentJobId = null;
    setPlotBtnEnabled(false);
    showLoading(true);
    try {
        const res = await fetch('/get-rooms', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ folder_path: folder, setpoint_path: setpoint, start_date: start, end_date: end, source_mode: currentSourceMode })
        });
        const data = await res.json();
        if (data.error) {
            if (data.error.includes('ERR-002')) {
                showErrorModal('Limit File Error', 'ERR-002', data.error);
            } else if (data.error.includes('ERR-009')) {
                showErrorModal('Invalid Limit File', 'ERR-009', data.error);
            } else if (data.error.includes('ERR-006')) {
                showErrorModal('Logical Constraint Error', 'ERR-006', data.error);
            } else {
                showErrorModal('Error', 'ERR-UNKNOWN', data.error);
            }
            return;
        }
        allRooms = data.all_rooms;
        roomsByArea = data.rooms_by_area;
        selectedRooms.clear();
        renderAreas(); renderAvailableRooms(); renderSelectedRooms();
        document.getElementById('roomSelectionSection').style.display = 'block';
        updateAiMsg(3, `AQR Program: Found ${allRooms.length} rooms. Select targets for multi-vector analysis.`);
    } finally { showLoading(false); }
});

function renderAreas() {
    const list = document.getElementById('areaList');
    list.innerHTML = '';
    Object.keys(roomsByArea).sort().forEach(area => {
        const li = document.createElement('li');
        li.innerText = area;
        if (area === currentArea) li.classList.add('active-area');
        li.onclick = () => {
            currentArea = (currentArea === area) ? null : area;
            renderAreas(); renderAvailableRooms();
        };
        list.appendChild(li);
    });
}

function renderAvailableRooms() {
    const list = document.getElementById('availableRoomList');
    list.innerHTML = '';
    const search = document.getElementById('availableSearch').value.toLowerCase();
    let roomsToShow = currentArea ? roomsByArea[currentArea] : allRooms;
    roomsToShow.filter(r => !selectedRooms.has(r.id))
               .filter(r => r.id.toLowerCase().includes(search) || r.name.toLowerCase().includes(search))
               .sort((a,b) => a.id.localeCompare(b.id))
               .forEach(room => {
                    const li = document.createElement('li');
                    li.innerText = `${room.id} - ${room.name}`;
                    li.onclick = () => { selectedRooms.add(room.id); renderAvailableRooms(); renderSelectedRooms(); };
                    list.appendChild(li);
               });
}

function renderSelectedRooms() {
    const list = document.getElementById('selectedRoomList');
    list.innerHTML = '';
    const search = document.getElementById('selectedSearch').value.toLowerCase();
    const filtered = allRooms.filter(r => selectedRooms.has(r.id))
            .filter(r => r.id.toLowerCase().includes(search) || r.name.toLowerCase().includes(search))
            .sort((a,b) => a.id.localeCompare(b.id));
    
    filtered.forEach(room => {
        const li = document.createElement('li');
        li.innerText = `${room.id} - ${room.name}`;
        li.classList.add('selected-item');
        li.onclick = () => { selectedRooms.delete(room.id); renderAvailableRooms(); renderSelectedRooms(); };
        list.appendChild(li);
    });

    document.getElementById('selectionBadge').innerText = selectedRooms.size;
}

// Action Buttons
document.getElementById('areaSelectAllBtn').onclick = () => {
    Object.values(roomsByArea).flat().forEach(r => selectedRooms.add(r.id));
    renderAvailableRooms(); renderSelectedRooms();
};
document.getElementById('areaDeselectAllBtn').onclick = () => {
    Object.values(roomsByArea).flat().forEach(r => selectedRooms.delete(r.id));
    renderAvailableRooms(); renderSelectedRooms();
};
document.getElementById('availSelectAllBtn').onclick = () => {
    let roomsToShow = currentArea ? roomsByArea[currentArea] : allRooms;
    roomsToShow.forEach(r => selectedRooms.add(r.id));
    renderAvailableRooms(); renderSelectedRooms();
};
document.getElementById('selectedDeselectAllBtn').onclick = () => {
    selectedRooms.clear();
    renderAvailableRooms(); renderSelectedRooms();
};

document.getElementById('analyzeBtn').onclick = async () => {
    if (selectedRooms.size === 0) return showErrorModal('No Rooms Selected', 'ERR-UNKNOWN', 'AQR Program: Select rooms first.');

    // Reset previous run state
    lastAnalysisPlotResult = null;
    currentJobId = null;
    setPlotBtnEnabled(false);
    document.getElementById('graphResults').style.display = 'none';
    document.getElementById('logSection').style.display = 'none';
    document.getElementById('analysisStatsBar').style.display = 'none';
    document.getElementById('analysisStatsBar').innerHTML = '';

    showLoading(true);

    // --- Step 1: start background job, get job_id ---
    let jobId;
    try {
        const res = await fetch('/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                folder_path:    document.getElementById('folderPath').value,
                setpoint_path:  document.getElementById('setpointPath').value,
                selected_rooms: Array.from(selectedRooms),
                start_date:     document.getElementById('startDate').value,
                end_date:       document.getElementById('endDate').value,
                source_mode:    currentSourceMode
            })
        });
        const initData = await res.json();
        if (initData.error) {
            showLoading(false);
            showErrorModal('Analysis Error', 'ERR-UNKNOWN', initData.error);
            return;
        }
        jobId = initData.job_id;
    } catch (e) {
        showLoading(false);
        showErrorModal('Network Error', 'ERR-UNKNOWN', 'Failed to start analysis. Is the server running?');
        return;
    }

    // Hide overlay now — log terminal streams in real-time, no need to block the UI
    showLoading(false);

    // --- Step 2: open SSE stream and pipe log lines into the terminal ---
    document.getElementById('statusSection').style.display = 'block';
    document.getElementById('logSection').style.display = 'block';
    const msg  = document.getElementById('statusMessage');
    const logs = document.getElementById('logOutput');
    msg.innerText = 'AQR Program: Processing...';
    msg.style.color = '';
    document.getElementById('statusIcon').style.background = '#3b82f6';
    logs.textContent = '';
    document.getElementById('resultLinks').innerHTML = '';
    document.getElementById('statusSection').scrollIntoView({ behavior: 'smooth' });

    // --- Efficient log rendering ---
    // Buffer incoming SSE lines and flush to DOM via requestAnimationFrame.
    // This batches all lines that arrive within a single frame into one DOM write,
    // preventing the O(n²) cost of innerText += on every event.
    let _logBuf = [];
    let _logActive = true;
    let _logLineCount = 0;
    const LOG_MAX_DISPLAY = 5000; // rolling window: keep last N lines visible

    function _flushLog() {
        if (_logBuf.length > 0) {
            const chunk = _logBuf.splice(0).join('\n') + '\n';
            _logLineCount += (chunk.match(/\n/g) || []).length;
            logs.appendChild(document.createTextNode(chunk));

            // Rolling trim: once DOM grows too large, compact it
            if (_logLineCount > LOG_MAX_DISPLAY + 500) {
                const lines = logs.textContent.split('\n');
                logs.textContent = '… (earlier output truncated) …\n' + lines.slice(-LOG_MAX_DISPLAY).join('\n');
                _logLineCount = LOG_MAX_DISPLAY;
            }
            logs.scrollTop = logs.scrollHeight;
        }
        if (_logActive) requestAnimationFrame(_flushLog);
    }
    requestAnimationFrame(_flushLog);

    function _stopLog() {
        _logActive = false;
        if (_logBuf.length > 0) {
            logs.appendChild(document.createTextNode(_logBuf.splice(0).join('\n') + '\n'));
            logs.scrollTop = logs.scrollHeight;
        }
    }

    const pollInterval = setInterval(async () => {
        try {
            const res = await fetch(`/job-status/${jobId}`);
            const data = await res.json();

            if (data.error) {
                clearInterval(pollInterval);
                _stopLog();
                showErrorModal('Analysis Error', 'ERR-UNKNOWN', data.error);
                return;
            }

            // GAMP 5: Feed incoming logs to real-time UI terminal buffer
            if (data.logs && data.logs.length > 0) {
                data.logs.forEach(line => _logBuf.push(line));
            }

            if (data.done) {
                clearInterval(pollInterval);
                _stopLog();

                if (data.error_msg) {
                    msg.innerHTML = `<span style="color:#ef4444">AQR Program: Analysis Failed</span>`;
                    document.getElementById('statusIcon').style.background = '#ef4444';
                    const errMsg = data.error_msg;
                    if (errMsg.includes('ERR-001'))      showErrorModal('Header Missing Error',         'ERR-001', errMsg);
                    else if (errMsg.includes('ERR-002')) showErrorModal('Limit File Error',              'ERR-002', errMsg);
                    else if (errMsg.includes('ERR-003')) showErrorModal('Invalid Configuration Error',   'ERR-003', errMsg);
                    else if (errMsg.includes('ERR-005')) showErrorModal('Invalid File Format',           'ERR-005', errMsg);
                    else if (errMsg.includes('ERR-006')) showErrorModal('Logical Constraint Error',      'ERR-006', errMsg);
                    else if (errMsg.includes('ERR-007')) showErrorModal('Report Generation Failed',      'ERR-007', errMsg);
                    else if (errMsg.includes('ERR-009')) showErrorModal('Invalid Limit File',           'ERR-009', errMsg);
                    else                                 showErrorModal('Analysis Error',                'ERR-UNKNOWN', errMsg);
                } else {
                    const result = data.response || {};
                    if (result.warning) {
                        msg.innerText = result.warning.length > 80 ? result.warning.slice(0, 80) + '...' : result.warning;
                        msg.style.color = '#f59e0b';
                        document.getElementById('statusIcon').style.background = '#f59e0b';
                        
                        // Check if warning contains room-level errors (ERR-001, ERR-003, ERR-005, ERR-006, ERR-011)
                        const codesFound = [];
                        ['ERR-001', 'ERR-003', 'ERR-005', 'ERR-006', 'ERR-011'].forEach(code => {
                            if (result.warning.includes(code)) {
                                codesFound.push(code);
                            }
                        });
                        if (codesFound.length > 0) {
                            showErrorModal('Room Analysis Warnings', codesFound.join(', '), result.warning);
                        } else {
                            // GAMP 5 compliance: Trigger Warning Modal Alert to ensure reviewer notices duplicate timestamps resolution
                            showErrorModal('Duplicate Timestamps Warning', 'ERR-008', result.warning);
                        }
                    } else {
                        msg.innerText = 'AQR Program: Analysis Successful!';
                        msg.style.color = '';
                        document.getElementById('statusIcon').style.background = '#10b981';
                    }
                    document.getElementById('resultLinks').innerHTML =
                        `<a href="/download/${result.filename}" class="btn-glow-primary" style="text-decoration:none;">Download AQR Program Report</a>`;
                    currentJobId = jobId;
                    setPlotBtnEnabled(true);

                    // Show stats bar
                    const statsBar = document.getElementById('analysisStatsBar');
                    const stats = result.stats || {};
                    if (stats.total !== undefined) {
                        statsBar.innerHTML =
                            `<div class="stat-item total"><div class="stat-value">${stats.total}</div><div class="stat-label">Total Rooms</div></div>` +
                            `<div class="stat-item passed"><div class="stat-value">${stats.passed}</div><div class="stat-label">Passed</div></div>` +
                            `<div class="stat-item violation"><div class="stat-value">${stats.violations}</div><div class="stat-label">Out of Spec</div></div>` +
                            `<div class="stat-item error"><div class="stat-value">${stats.errors}</div><div class="stat-label">Errors</div></div>`;
                        statsBar.style.display = 'flex';
                    }
                }
            }
        } catch (e) {
            clearInterval(pollInterval);
            _stopLog();
            showErrorModal('Connection Error', 'ERR-UNKNOWN', 'Lost connection to server during analysis.');
        }
    }, 500);
};

const commonRangeButtons = [
    {count: 1, label: '1H', step: 'hour', stepmode: 'backward'},
    {count: 1, label: '1D', step: 'day', stepmode: 'backward'},
    {count: 7, label: '7D', step: 'day', stepmode: 'backward'},
    {count: 30, label: '30D', step: 'day', stepmode: 'backward'},
    {step: 'all', label: 'ALL'}
];

document.getElementById('plotBtn').onclick = async () => {
    if (!currentJobId) return;

    // If we already fetched this job's plot data, re-render from cache
    if (lastAnalysisPlotResult && lastAnalysisPlotResult._jobId === currentJobId) {
        const data = lastAnalysisPlotResult;
        const limits = {
            temp_high:  parseFloat(document.getElementById('limitTempHigh').value)  || 0,
            hum_high:   parseFloat(document.getElementById('limitHumHigh').value)   || 0,
            hum_low:    parseFloat(document.getElementById('limitHumLow').value)    || 0,
            press_high: parseFloat(document.getElementById('limitPressHigh').value) || 0,
            press_low:  parseFloat(document.getElementById('limitPressLow').value)  || 0
        };
        updateAiMsg(3, "AQR Program: Visual engine engaged. All monitors synchronized.");
        document.getElementById('graphResults').style.display = 'block';
        renderTimelineChart(data.violation_intervals);
        const summaryH = renderSummaryChart(data.summary);
        renderSummaryTable(data.summary, summaryH);
        renderPlots(data.plot_data, limits);
        renderHeatmap(data.violation_intervals);
        setTimeout(() => document.getElementById('graphResults').scrollIntoView({ behavior: 'smooth' }), 100);
        return;
    }

    // First time: fetch plot data lazily from server
    showLoading(true);
    try {
        const res = await fetch(`/plot/${currentJobId}`);
        const data = await res.json();
        if (data.error) {
            showErrorModal('Plot Error', 'ERR-UNKNOWN', data.error);
            return;
        }
        data._jobId = currentJobId;  // tag for cache check above
        lastAnalysisPlotResult = data;

        const limits = {
            temp_high:  parseFloat(document.getElementById('limitTempHigh').value)  || 0,
            hum_high:   parseFloat(document.getElementById('limitHumHigh').value)   || 0,
            hum_low:    parseFloat(document.getElementById('limitHumLow').value)    || 0,
            press_high: parseFloat(document.getElementById('limitPressHigh').value) || 0,
            press_low:  parseFloat(document.getElementById('limitPressLow').value)  || 0
        };
        updateAiMsg(3, "AQR Program: Visual engine engaged. All monitors synchronized.");
        document.getElementById('graphResults').style.display = 'block';
        renderTimelineChart(data.violation_intervals);
        const summaryH = renderSummaryChart(data.summary);
        renderSummaryTable(data.summary, summaryH);
        renderPlots(data.plot_data, limits);
        renderHeatmap(data.violation_intervals);
        setTimeout(() => document.getElementById('graphResults').scrollIntoView({ behavior: 'smooth' }), 100);
    } finally {
        showLoading(false);
    }
};

function renderHeatmap(intervals) {
    if (!intervals || intervals.length === 0) {
        document.getElementById('violationHeatmap').innerHTML = '<div style="display:flex; height:100%; align-items:center; justify-content:center; color:#94a3b8; font-weight:600;">AQR Program: Insufficient violation data for heatmap</div>';
        return;
    }

    // Process intervals to count by Hour and Day (local timezone)
    const pad = n => String(n).padStart(2, '0');
    const toLocalDate = d => `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
    const counts = {}; // "YYYY-MM-DD|HH" -> count
    intervals.forEach(inv => {
        const start = new Date(inv.start);
        const end = new Date(inv.end);
        let curr = new Date(start.getTime());
        curr.setMinutes(0, 0, 0);

        while (curr <= end) {
            const dayKey = toLocalDate(curr);
            const hourKey = curr.getHours();
            const key = `${dayKey}|${hourKey}`;
            counts[key] = (counts[key] || 0) + 1;
            curr.setHours(curr.getHours() + 1);
        }
    });

    const days = [...new Set(Object.keys(counts).map(k => k.split('|')[0]))].sort();
    const hours = Array.from({length: 24}, (_, i) => i);
    const zData = days.map(d => hours.map(h => counts[`${d}|${h}`] || 0));

    const trace = {
        z: zData, x: hours.map(h => `${h}:00`), y: days,
        type: 'heatmap', colorscale: 'YlOrRd', reversescale: true, showscale: true,
        hoverongaps: false,
        hovertemplate: 'Day: %{y}<br>Hour: %{x}<br>Violations: %{z}<extra></extra>'
    };

    const layout = {
        template: document.body.getAttribute('data-theme') === 'dark' ? 'plotly_dark' : 'plotly_white',
        margin: { t: 30, b: 50, l: 100, r: 30 },
        xaxis: { title: 'Hour of Day', tickmode: 'linear' },
        yaxis: { title: 'Date', type: 'category', automargin: true }
    };

    Plotly.newPlot('violationHeatmap', [trace], layout, { responsive: true, displaylogo: false });
}

function renderTimelineChart(intervals) {
    const chartDiv = document.getElementById('violationTimelineChart');
    if (!intervals || intervals.length === 0) {
        chartDiv.innerHTML = '<div style="display:flex; height:100%; align-items:center; justify-content:center; color:#94a3b8; font-weight:600;">AQR Program: No major violations detected (> 20 mins)</div>';
        return;
    }

    // Extract unique rooms to maintain 1 room = 1 row space
    const violationRooms = [...new Set(intervals.map(inv => inv.room_id))];
    const N_TL = violationRooms.length;
    const ROW_H = 34; // Slightly taller rows to give offset lines breathing room
    const P = N_TL * ROW_H + 30; // Plotting area
    const dynamicHeight = P + 80 + 65; // Plotting area + top margin + bottom margin
    chartDiv.style.height = dynamicHeight + 'px';
    const sliderThickness = 30 / P;

    // Map room IDs to numeric indices
    const roomIndices = {};
    violationRooms.forEach((room, idx) => {
        roomIndices[room] = idx;
    });

    // Y-offsets within a single room row to show all 3 parameters in parallel lanes (no overlaps!)
    const yOffsets = {
        'Temperature': 0.22,  // Shifted up
        'Humidity': 0.0,       // Centered
        'Pressure': -0.22      // Shifted down
    };
    const typeColors = {
        'Temperature': '#fbbf24', // Yellow
        'Humidity': '#3b82f6',    // Blue
        'Pressure': '#ef4444'      // Red
    };

    const traces = intervals.map(inv => {
        const roomIdx = roomIndices[inv.room_id];
        const yVal = roomIdx + (yOffsets[inv.type] || 0.0);
        return {
            x: [inv.start, inv.end], y: [yVal, yVal], name: inv.type,
            mode: 'lines', line: { color: typeColors[inv.type] || '#6366f1', width: 8 }, // Increased from 6 to 8 for a slightly bolder, clearer appearance
            customdata: [inv], hoverinfo: 'text',
            hovertext: `<b>Room: ${inv.room_id}</b><br>Type: ${inv.type} (${inv.status})<br>Start: ${inv.start}<br>End: ${inv.end}<br>Duration: ${inv.duration} mins`,
            showlegend: false
        };
    });

    ['Temperature', 'Humidity', 'Pressure'].forEach(type => {
        traces.push({ x: [null], y: [0], name: type, mode: 'lines', line: { color: typeColors[type], width: 8 }, showlegend: true });
    });

    const layout = {
        height: dynamicHeight,
        template: document.body.getAttribute('data-theme') === 'dark' ? 'plotly_dark' : 'plotly_white',
        margin: { t: 80, b: 65, l: 85, r: 90 },
        font: { family: 'Inter, sans-serif', color: document.body.getAttribute('data-theme') === 'dark' ? '#f1f5f9' : '#1e293b' },
        xaxis: {
            type: 'date', title: { text: 'Time', font: { size: 12, weight: 700 }, standoff: 20 }, automargin: true,
            tickfont: { family: 'JetBrains Mono, monospace', size: 10, color: '#64748b' },
            rangeselector: { buttons: commonRangeButtons, x: 0, y: 1 + (35 / P), yanchor: 'bottom', bgcolor: '#f8fafc' },
            rangeslider: { visible: true, bordercolor: '#e2e8f0', borderwidth: 1, thickness: sliderThickness }
        },
        yaxis: {
            range: [N_TL - 0.5, -0.5], // Keep first room at the top
            tickvals: violationRooms.map((_, idx) => idx),
            ticktext: violationRooms.map(room => room + '    '), // Append trailing spaces for robust label-to-graph spacing
            automargin: true,
            tickfont: { family: 'JetBrains Mono, monospace', size: 10, color: '#64748b' },
            zeroline: false, // Completely removes the black zero line from the numeric Y-axis!
            tickpad: 15 // Pushes the Room ID labels left of the axis line
        },
        hovermode: 'closest',
        legend: { orientation: 'v', x: 1.02, y: 1, xanchor: 'left', font: { size: 11, weight: 600 } }
    };

    Plotly.newPlot('violationTimelineChart', traces, layout, { responsive: false, displaylogo: false });
    
    // Manual resize listener to keep width responsive without Plotly corrupting the height
    window.addEventListener('resize', () => {
        Plotly.relayout('violationTimelineChart', { width: chartDiv.parentElement.clientWidth });
    });

    chartDiv.on('plotly_restyle', function(data) {
        if (window.isSyncingTimeline) return;
        const update = data[0];
        const indices = data[1];
        if (update.visible === undefined) return;
        window.isSyncingTimeline = true;
        try {
            const toggledIndex = indices[0];
            const toggledTrace = chartDiv.data[toggledIndex];
            if (!toggledTrace) return;
            const type = toggledTrace.name; 
            const targetVisible = update.visible[0];
            const matchingIndices = [];
            chartDiv.data.forEach((trace, i) => {
                if (i !== toggledIndex && trace.customdata && trace.customdata[0] && trace.customdata[0].type === type) matchingIndices.push(i);
            });
            if (matchingIndices.length > 0) Plotly.restyle(chartDiv, { visible: targetVisible }, matchingIndices);
        } finally { setTimeout(() => { window.isSyncingTimeline = false; }, 50); }
    });

    chartDiv.on('plotly_click', function(data){
        if(!data.points || data.points.length === 0) return;
        const inv = data.points[0].fullData.customdata ? data.points[0].fullData.customdata[0] : null;
        if (inv) {
            const startBuf = new Date(new Date(inv.start).getTime() - 30*60*1000).toISOString();
            const endBuf = new Date(new Date(inv.end).getTime() + 30*60*1000).toISOString();
            isolateRoomInDetailPlots(inv.room_id, [startBuf, endBuf]);
        }
    });
}

function renderSummaryChart(summary) {
    const chartDiv = document.getElementById('summaryViolationChart');

    // Filter to rooms with at least one violation, sorted descending by total
    const withViolations = summary
        .filter(s => s.temp_v + s.hum_v + s.press_v > 0)
        .sort((a, b) => (b.temp_v + b.hum_v + b.press_v) - (a.temp_v + a.hum_v + a.press_v));

    if (withViolations.length === 0) {
        chartDiv.innerHTML = '<div style="display:flex; height:100%; align-items:center; justify-content:center; color:#94a3b8; font-weight:600;">AQR Program: No violations detected.</div>';
        return;
    }

    const N_SUM = withViolations.length;
    const ROW_H = 26;
    const P = N_SUM * ROW_H; // Plotting area (bars only)
    const dynamicHeight = P + 80 + 50; // Plotting area + margins (t:80, b:50)
    chartDiv.style.height = dynamicHeight + 'px';

    const roomIds = withViolations.map(s => '\u200B' + s.room_id);
    const traceTemp  = { y: roomIds, x: withViolations.map(s => s.temp_v),  name: 'Temperature', type: 'bar', orientation: 'h', marker: { color: '#fbbf24' } };
    const traceHum   = { y: roomIds, x: withViolations.map(s => s.hum_v),   name: 'Humidity',    type: 'bar', orientation: 'h', marker: { color: '#3b82f6' } };
    const tracePress = { y: roomIds, x: withViolations.map(s => s.press_v), name: 'Pressure',    type: 'bar', orientation: 'h', marker: { color: '#ef4444' } };

    const layout = {
        height: dynamicHeight,
        barmode: 'stack',
        // bargap: 0.5 → each bar ≈ 50% of ROW_H = 13px, matching timeline line width
        bargap: 0.5,
        template: document.body.getAttribute('data-theme') === 'dark' ? 'plotly_dark' : 'plotly_white',
        margin: { t: 80, b: 50, l: 120, r: 20 },
        font: { family: 'Inter, sans-serif', color: document.body.getAttribute('data-theme') === 'dark' ? '#f1f5f9' : '#1e293b' },
        yaxis: {
            range: [N_SUM - 0.5, -0.5],
            type: 'category',
            categoryorder: 'array',
            categoryarray: roomIds,
            dtick: 1,
            title: { text: 'Room ID', font: { size: 12, weight: 700 } }, automargin: true
        },
        xaxis: { title: { text: 'Violation Event Count', font: { size: 12, weight: 700 } }, gridcolor: '#f1f5f9', zeroline: false, showline: false },
        legend: { orientation: 'h', y: 1.0, yanchor: 'bottom', x: 0.5, xanchor: 'center', font: { size: 11, weight: 600 } },
        hovermode: 'closest'
    };

    Plotly.newPlot('summaryViolationChart', [traceTemp, traceHum, tracePress], layout, { responsive: false, displaylogo: false });

    // Manual resize listener to keep width responsive without Plotly corrupting the height
    window.addEventListener('resize', () => {
        Plotly.relayout('summaryViolationChart', { width: chartDiv.parentElement.clientWidth });
    });

    chartDiv.on('plotly_click', function(data) {
        if (!data.points || data.points.length === 0) return;
        let clickedY = data.points[0].y;
        if (typeof clickedY === 'string') clickedY = clickedY.replace('\u200B', '');
        isolateRoomInDetailPlots(clickedY);
    });

    return dynamicHeight;
}

function isolateRoomInDetailPlots(roomId, timeRange = null) {
    const plotDivs = ['plotTemp', 'plotHum', 'plotPress', 'violationTimelineChart'];
    plotDivs.forEach(pid => {
        const gd = document.getElementById(pid);
        if (!gd || !gd.data) return;
        if (pid !== 'violationTimelineChart') {
            const update = {
                visible: gd.data.map(trace => {
                    if (trace.name === 'H-Limit' || trace.name === 'L-Limit') return true;
                    return trace.name === roomId ? true : 'legendonly';
                })
            };
            Plotly.restyle(pid, update);
        }
        if (timeRange) Plotly.relayout(pid, { 'xaxis.range': timeRange });
    });
    document.getElementById('plotTemp').scrollIntoView({ behavior: 'smooth' });
}

function renderSummaryTable(summary, maxH) {
    if (maxH) {
        const container = document.querySelector('.table-container-modern');
        if (container) {
            const visibleH = Math.min(maxH, 500);
            container.style.height = visibleH + 'px';
            container.style.maxHeight = visibleH + 'px';
        }
    }
    const tbody = document.getElementById('summaryTableBody');
    tbody.innerHTML = '';
    summary.forEach(row => {
        const tr = document.createElement('tr');
        tr.className = 'clickable-row';
        tr.innerHTML = `<td>${row.room_id}</td><td>${row.room_name}</td><td>${row.temp_v}</td><td>${row.hum_v}</td><td>${row.press_v}</td>`;
        tr.onclick = () => isolateRoomInDetailPlots(row.room_id);
        tbody.appendChild(tr);
    });
}

function renderPlots(plotData) {
    const rooms = Object.keys(plotData);
    const isManyRooms = rooms.length > 5;
    const plotConfigs = [
        { id: 'plotTemp', title: 'Temperature Monitor', unit: '°C', param: 'temp', limits: [ {id: 'limitTempHigh', label: 'H-Limit'} ] },
        { id: 'plotHum', title: 'Humidity Monitor', unit: '%RH', param: 'hum', limits: [ {id: 'limitHumHigh', label: 'H-Limit'}, {id: 'limitHumLow', label: 'L-Limit'} ] },
        { id: 'plotPress', title: 'Pressure Monitor', unit: 'Pa', param: 'press', limits: [ {id: 'limitPressHigh', label: 'H-Limit'}, {id: 'limitPressLow', label: 'L-Limit'} ] }
    ];

    plotConfigs.forEach((config) => {
        const traces = rooms.map(rid => ({
            x: plotData[rid].times, y: plotData[rid][config.param], name: rid, 
            type: 'scattergl', mode: 'lines', line: { width: 2 },
            visible: isManyRooms ? 'legendonly' : true,
            hoverlabel: { namelength: -1 }
        }));

        const buildShapes = () => config.limits.map(l => {
            const val = parseFloat(document.getElementById(l.id).value);
            return {
                type: 'line', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: val, y1: val,
                line: { color: 'red', width: 2, dash: 'dash' }, name: l.id
            };
        });

        const layout = {
            template: document.body.getAttribute('data-theme') === 'dark' ? 'plotly_dark' : 'plotly_white',
            margin: { t: 40, b: 100, l: 60, r: 170 },
            font: { family: 'Inter, sans-serif' },
            hovermode: 'closest',
            xaxis: { 
                type: 'date', title: { text: 'Time of Day', font: { size: 12, weight: 700 } }, automargin: true,
                rangeselector: { buttons: commonRangeButtons, x: 0, y: 1.15 }
            },
            yaxis: { title: { text: `${config.title} (${config.unit})`, font: { size: 12, weight: 700 } }, automargin: true, autorange: true, fixedrange: false },
            autosize: true,
            legend: { orientation: 'v', x: 1.01, y: 1, xanchor: 'left', font: { size: 10, weight: 600 } },
            shapes: buildShapes()
        };

        const pConfig = { responsive: true, displaylogo: false, editable: true, edits: { shapePosition: true } };
        Plotly.newPlot(config.id, traces, layout, pConfig);

        const gd = document.getElementById(config.id);
        gd.on('plotly_restyle', function(data) {
            if (window.isSyncingMultiLegend) return;
            if (data[0].visible === undefined) return;
            window.isSyncingMultiLegend = true;
            try {
                const update = { visible: data[0].visible };
                const indices = data[1];
                ['plotTemp', 'plotHum', 'plotPress'].forEach(pid => {
                    if (pid === config.id) return;
                    const targetGd = document.getElementById(pid);
                    if (targetGd && targetGd.data) Plotly.restyle(targetGd, update, indices);
                });
            } finally { setTimeout(() => { window.isSyncingMultiLegend = false; }, 50); }
        });

        gd.on('plotly_relayout', function(eventData){
            for (let key in eventData) {
                if (key.startsWith('shapes[')) {
                    const idx = parseInt(key.match(/\[(\d+)\]/)[1]);
                    const newY = eventData[key];
                    const inputId = layout.shapes[idx].name;
                    if (inputId) document.getElementById(inputId).value = newY.toFixed(1);
                }
            }
        });

        config.limits.forEach(l => {
            const inputEl = document.getElementById(l.id);
            inputEl.oninput = () => {
                const newVal = parseFloat(inputEl.value);
                if (isNaN(newVal)) return;
                const currentGd = document.getElementById(config.id);
                const currentShapes = (currentGd.layout && currentGd.layout.shapes) ? currentGd.layout.shapes : [];
                const sIdx = currentShapes.findIndex(s => s.name === l.id);
                if (sIdx !== -1) {
                    const update = {};
                    update[`shapes[${sIdx}].y0`] = newVal;
                    update[`shapes[${sIdx}].y1`] = newVal;
                    Plotly.relayout(config.id, update);
                } else {
                    const newShape = { type: 'line', xref: 'paper', yref: 'y', x0: 0, x1: 1, y0: newVal, y1: newVal, line: { color: 'red', width: 2, dash: 'dash' }, name: l.id };
                    Plotly.relayout(config.id, { 'shapes': [...currentShapes, newShape] });
                }
            };
        });
    });
    
    const allPlotIds = ['plotTemp', 'plotHum', 'plotPress', 'violationTimelineChart'];
    allPlotIds.forEach(id => {
        const div = document.getElementById(id);
        if (!div) return;
        div.on('plotly_relayout', (e) => {
            if (isSyncing || Object.keys(e).some(k => k.startsWith('shapes['))) return;
            isSyncing = true;
            let update = {};
            if (e['xaxis.range[0]']) update = { 'xaxis.range': [e['xaxis.range[0]'], e['xaxis.range[1]']] };
            else if (e['xaxis.autorange']) update = { 'xaxis.autorange': true };
            if (Object.keys(update).length > 0) {
                const promises = allPlotIds.filter(oid => oid !== id).map(oid => {
                    const target = document.getElementById(oid);
                    return (target && target.data) ? Plotly.relayout(oid, update) : Promise.resolve();
                });
                Promise.all(promises).finally(() => { setTimeout(() => { isSyncing = false; }, 50); });
            } else { isSyncing = false; }
        });
    });
}

// Initialize plotBtn as disabled on page load
document.addEventListener('DOMContentLoaded', () => setPlotBtnEnabled(false));

// Log panel collapse toggle
document.getElementById('logToggleHeader').addEventListener('click', () => {
    const log  = document.getElementById('logOutput');
    const icon = document.getElementById('logCollapseIcon');
    const isCollapsed = log.style.display === 'none';
    log.style.display  = isCollapsed ? '' : 'none';
    icon.className     = isCollapsed ? 'fas fa-chevron-up' : 'fas fa-chevron-down';
});
