let allRooms = [];
let roomsByArea = {};
let selectedRooms = new Set();
let currentArea = null;
let isSyncing = false; 

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
                body: JSON.stringify({ folder_path: folder })
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
    showLoading(true);
    try {
        const res = await fetch('/get-rooms', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ folder_path: folder, setpoint_path: setpoint, start_date: start, end_date: end })
        });
        const data = await res.json();
        if (data.error) {
            if (data.error.includes('ERR-002')) {
                showErrorModal('Limit File Error', 'ERR-002', data.error);
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
    showLoading(true);
    try {
        const res = await fetch('/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                folder_path: document.getElementById('folderPath').value,
                setpoint_path: document.getElementById('setpointPath').value,
                selected_rooms: Array.from(selectedRooms),
                start_date: document.getElementById('startDate').value,
                end_date: document.getElementById('endDate').value
            })
        });
        const data = await res.json();
        document.getElementById('statusSection').style.display = 'block';
        const msg = document.getElementById('statusMessage');
        const logs = document.getElementById('logOutput');
        if (data.error) {
            msg.innerHTML = `<span style="color:#ef4444">AQR Program: Analysis Failed</span>`;
            logs.innerText = data.logs || data.error;
            if (data.error.includes('ERR-001')) {
                showErrorModal('Header Missing Error', 'ERR-001', data.error);
            } else if (data.error.includes('ERR-002')) {
                showErrorModal('Limit File Error', 'ERR-002', data.error);
            } else if (data.error.includes('ERR-003')) {
                showErrorModal('Invalid Configuration Error', 'ERR-003', data.error);
            } else if (data.error.includes('ERR-005')) {
                showErrorModal('Invalid File Format', 'ERR-005', data.error);
            } else if (data.error.includes('ERR-006')) {
                showErrorModal('Logical Constraint Error', 'ERR-006', data.error);
            } else {
                showErrorModal('Analysis Error', 'ERR-UNKNOWN', data.error);
            }
        } else {
            msg.innerText = "AQR Program: Analysis Successful!";
            document.getElementById('resultLinks').innerHTML = `<a href="/download/${data.filename}" class="btn-glow-primary" style="text-decoration:none;">Download AQR Program Report</a>`;
            logs.innerText = data.logs;
        }
        document.getElementById('statusSection').scrollIntoView({ behavior: 'smooth' });
    } finally { showLoading(false); }
};

const commonRangeButtons = [
    {count: 1, label: '1H', step: 'hour', stepmode: 'backward'},
    {count: 1, label: '1D', step: 'day', stepmode: 'backward'},
    {count: 7, label: '7D', step: 'day', stepmode: 'backward'},
    {count: 30, label: '30D', step: 'day', stepmode: 'backward'},
    {step: 'all', label: 'ALL'}
];

document.getElementById('plotBtn').onclick = async () => {
    if (selectedRooms.size === 0) return alert("AQR Program: Select rooms first.");
    const limits = {
        temp_high: parseFloat(document.getElementById('limitTempHigh').value) || 0,
        hum_high: parseFloat(document.getElementById('limitHumHigh').value) || 0,
        hum_low: parseFloat(document.getElementById('limitHumLow').value) || 0,
        press_high: parseFloat(document.getElementById('limitPressHigh').value) || 0,
        press_low: parseFloat(document.getElementById('limitPressLow').value) || 0
    };
    showLoading(true);
    try {
        const res = await fetch('/get-plot-data', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                folder_path: document.getElementById('folderPath').value,
                setpoint_path: document.getElementById('setpointPath').value,
                selected_rooms: Array.from(selectedRooms),
                start_date: document.getElementById('startDate').value,
                end_date: document.getElementById('endDate').value,
                limits: limits
            })
        });
        const data = await res.json();
        if (data.error) return alert(data.error);
        if (!data.plot_data || Object.keys(data.plot_data).length === 0) return alert("AQR Program: No data found for the selected range.");

        updateAiMsg(3, "AQR Program: Visual engine engaged. All monitors synchronized.");
        document.getElementById('graphResults').style.display = 'block';
        renderTimelineChart(data.violation_intervals);
        renderSummaryChart(data.summary);
        renderSummaryTable(data.summary);
        renderPlots(data.plot_data, limits);
        renderHeatmap(data.violation_intervals);
        setTimeout(() => document.getElementById('graphResults').scrollIntoView({ behavior: 'smooth' }), 100);
    } finally { showLoading(false); }
};

function renderHeatmap(intervals) {
    if (!intervals || intervals.length === 0) {
        document.getElementById('violationHeatmap').innerHTML = '<div style="display:flex; height:100%; align-items:center; justify-content:center; color:#94a3b8; font-weight:600;">AQR Program: Insufficient violation data for heatmap</div>';
        return;
    }

    // Process intervals to count by Hour and Day
    const counts = {}; // "YYYY-MM-DD|HH" -> count
    intervals.forEach(inv => {
        const start = new Date(inv.start);
        const end = new Date(inv.end);
        let curr = new Date(start.getTime());
        curr.setMinutes(0, 0, 0);
        
        while (curr <= end) {
            const dayKey = curr.toISOString().split('T')[0];
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
        type: 'heatmap', colorscale: 'YlOrRd', showscale: true,
        hoverongaps: false,
        hovertemplate: 'Day: %{y}<br>Hour: %{x}<br>Violations: %{z}<extra></extra>'
    };

    const layout = {
        template: document.body.getAttribute('data-theme') === 'dark' ? 'plotly_dark' : 'plotly_white',
        margin: { t: 30, b: 50, l: 100, r: 30 },
        xaxis: { title: 'Hour of Day', tickmode: 'linear' },
        yaxis: { title: 'Date', automargin: true }
    };

    Plotly.newPlot('violationHeatmap', [trace], layout, { responsive: true, displaylogo: false });
}

function renderTimelineChart(intervals) {
    const chartDiv = document.getElementById('violationTimelineChart');
    if (!intervals || intervals.length === 0) {
        chartDiv.innerHTML = '<div style="display:flex; height:100%; align-items:center; justify-content:center; color:#94a3b8; font-weight:600;">AQR Program: No major violations detected (> 25 mins)</div>';
        return;
    }

    const typeColors = { 'Temperature': '#fbbf24', 'Humidity': '#3b82f6', 'Pressure': '#ef4444' };
    const traces = intervals.map(inv => ({
        x: [inv.start, inv.end], y: [inv.room_id, inv.room_id], name: inv.type,
        mode: 'lines', line: { color: typeColors[inv.type] || '#6366f1', width: 20 },
        customdata: [inv], hoverinfo: 'text',
        hovertext: `<b>Room: ${inv.room_id}</b><br>Type: ${inv.type} (${inv.status})<br>Start: ${inv.start}<br>End: ${inv.end}<br>Duration: ${inv.duration} mins`,
        showlegend: false
    }));

    ['Temperature', 'Humidity', 'Pressure'].forEach(type => {
        traces.push({ x: [null], y: [null], name: type, mode: 'lines', line: { color: typeColors[type], width: 10 }, showlegend: true });
    });

    const layout = {
        template: document.body.getAttribute('data-theme') === 'dark' ? 'plotly_dark' : 'plotly_white',
        margin: { t: 40, b: 100, l: 150, r: 150 },
        font: { family: 'Inter, sans-serif', color: document.body.getAttribute('data-theme') === 'dark' ? '#f1f5f9' : '#1e293b' },
        xaxis: { 
            type: 'date', title: { text: 'Time', font: { size: 12, weight: 700 } }, automargin: true,
            tickfont: { family: 'JetBrains Mono, monospace', size: 10, color: '#64748b' },
            rangeselector: { buttons: commonRangeButtons, x: 0, y: 1.15, bgcolor: '#f8fafc' },
            rangeslider: { visible: true, bordercolor: '#e2e8f0', borderwidth: 1, thickness: 0.05 }
        },
        yaxis: { 
            title: { text: 'Room ID', font: { size: 12, weight: 700 } }, automargin: true, autorange: 'reversed',
            tickfont: { family: 'JetBrains Mono, monospace', size: 10, color: '#64748b' }
        },
        hovermode: 'closest',
        legend: { orientation: 'v', x: 1.05, y: 1, xanchor: 'left', font: { size: 11, weight: 600 } }
    };

    Plotly.newPlot('violationTimelineChart', traces, layout, { responsive: true, displaylogo: false });

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
    const roomIds = summary.map(s => s.room_id);
    const traceTemp = { x: roomIds, y: summary.map(s => s.temp_v), name: 'Temperature', type: 'bar', marker: { color: '#fbbf24' } };
    const traceHum = { x: roomIds, y: summary.map(s => s.hum_v), name: 'Humidity', type: 'bar', marker: { color: '#3b82f6' } };
    const tracePress = { x: roomIds, y: summary.map(s => s.press_v), name: 'Pressure', type: 'bar', marker: { color: '#ef4444' } };

    const layout = {
        barmode: 'stack', template: document.body.getAttribute('data-theme') === 'dark' ? 'plotly_dark' : 'plotly_white',
        margin: { t: 40, b: 80, l: 60, r: 20 },
        font: { family: 'Inter, sans-serif', color: document.body.getAttribute('data-theme') === 'dark' ? '#f1f5f9' : '#1e293b' },
        xaxis: { title: { text: 'Room ID', font: { size: 12, weight: 700 } }, tickangle: -45, automargin: true },
        yaxis: { title: { text: 'Violation Event Count', font: { size: 12, weight: 700 } }, gridcolor: '#f1f5f9' },
        legend: { orientation: 'h', y: 1.1, x: 0.5, xanchor: 'center', font: { size: 11, weight: 600 } },
        hovermode: 'closest'
    };

    Plotly.newPlot('summaryViolationChart', [traceTemp, traceHum, tracePress], layout, { responsive: true, displaylogo: false });

    document.getElementById('summaryViolationChart').on('plotly_click', function(data){
        if(!data.points || data.points.length === 0) return;
        isolateRoomInDetailPlots(data.points[0].x);
    });
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

function renderSummaryTable(summary) {
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

function renderPlots(plotData, initialLimits) {
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
            margin: { t: 40, b: 100, l: 60, r: 250 },
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
