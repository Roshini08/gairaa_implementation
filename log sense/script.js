
let latestAnalysis = null;
let severityChart = null;
let timelineChart = null;

const sampleLogs = `2026-11-10 10:20:00 INFO service=auth User login successful
2026-11-10 10:20:15 INFO service=inventory Product catalog loaded
2026-11-10 10:21:00 ERROR service=payment Database connection failed
2026-11-10 10:21:10 ERROR service=payment Database connection failed
2026-11-10 10:21:20 WARNING service=auth High response time detected
2026-11-10 10:22:00 INFO service=auth Session created successfully
2026-11-10 10:22:30 ERROR service=payment Database connection failed
2026-11-10 10:23:00 WARNING service=inventory Low memory warning
2026-11-10 10:23:15 DEBUG service=inventory Cache lookup completed
2026-11-10 10:24:00 CRITICAL service=payment Payment database unavailable
2026-11-10 10:24:10 ERROR service=payment Connection timeout while processing order
2026-11-10 10:24:20 ERROR service=payment Connection timeout while processing order
2026-11-10 10:25:00 INFO service=auth User logout successful
2026-11-10 10:25:30 WARNING service=auth High response time detected
2026-11-10 10:26:00 ERROR service=auth Authentication service timeout
2026-11-10 10:26:10 ERROR service=auth Authentication service timeout
2026-11-10 10:27:00 INFO service=inventory Stock update completed
2026-11-10 10:27:30 DEBUG service=inventory Cache refresh completed
2026-11-10 10:28:00 WARNING service=payment Retry attempt detected
2026-11-10 10:28:30 ERROR service=payment Database connection failed
2026-11-10 10:29:00 INFO service=auth Login request processed
2026-11-10 10:29:30 WARNING service=inventory API response time above threshold
2026-11-10 10:30:00 ERROR service=inventory Inventory database query failed
2026-11-10 10:30:10 ERROR service=inventory Inventory database query failed
2026-11-10 10:31:00 CRITICAL service=payment Payment processing service unavailable
2026-11-10 10:31:30 INFO service=auth Health check passed
2026-11-10 10:32:00 WARNING service=payment Multiple retry attempts detected
2026-11-10 10:32:30 ERROR service=payment Database connection failed
2026-11-10 10:33:00 DEBUG service=auth Token validation completed
2026-11-10 10:33:30 INFO service=inventory Inventory request completed`;

function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[char]);
}

function loadSample() {
    document.getElementById("logFile").value = "";
    document.getElementById("fileName").textContent = "Sample data loaded";
    document.getElementById("logText").value = sampleLogs;
}

document.getElementById("logFile").addEventListener("change", function () {
    const file = this.files[0];

    if (file) {
        document.getElementById("fileName").textContent = file.name;
        document.getElementById("logText").value = "";
    }
});

function renderChart(canvasId, type, labels, values, label) {
    const canvas = document.getElementById(canvasId);

    if (canvasId === "severityChart" && severityChart) {
        severityChart.destroy();
    }

    if (canvasId === "timelineChart" && timelineChart) {
        timelineChart.destroy();
    }

    const chart = new Chart(canvas, {
        type,
        data: {
            labels,
            datasets: [{
                label,
                data: values,
                backgroundColor: type === "doughnut"
                    ? ["#ff7186", "#f4bd62", "#65aaff", "#4de0ae", "#a78bfa", "#64758d"]
                    : "rgba(77,224,174,0.18)",
                borderColor: type === "line" ? "#4de0ae" : undefined,
                borderWidth: type === "line" ? 2 : 0,
                fill: type === "line",
                tension: 0.35,
                pointRadius: 4,
                pointBackgroundColor: "#4de0ae",
                borderRadius: type === "bar" ? 5 : 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: type === "doughnut",
                    labels: {
                        color: "#aabbd0",
                        boxWidth: 10,
                        padding: 14,
                        font: { size: 10 }
                    }
                }
            },
            scales: type === "doughnut" ? {} : {
                x: {
                    ticks: { color: "#91a2b9", font: { size: 9 } },
                    grid: { color: "#243247" }
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: "#91a2b9", precision: 0 },
                    grid: { color: "#243247" }
                }
            }
        }
    });

    if (canvasId === "severityChart") severityChart = chart;
    if (canvasId === "timelineChart") timelineChart = chart;
}

function renderClusters(data) {
    const container = document.getElementById("clustersGrid");
    const status = document.getElementById("clusterStatus");

    if (!data.available) {
        status.textContent = data.message || "Clustering is unavailable.";
        container.innerHTML = "";
        return;
    }

    status.textContent = data.algorithm
        ? `${data.algorithm} completed · ${data.unique_error_messages} unique error messages`
        : data.message;

    if (!data.clusters || !data.clusters.length) {
        container.innerHTML =
            '<div class="empty-state">Not enough distinct error messages to create clusters.</div>';
        return;
    }

    container.innerHTML = data.clusters.map(cluster => `
        <article class="cluster-card">
            <div class="cluster-head">
                <b>Cluster ${cluster.cluster_id}</b>
                <span class="cluster-count">${cluster.count} messages</span>
            </div>
            <p>${escapeHTML(cluster.representative)}</p>
            <small>Grouped error pattern</small>
        </article>
    `).join("");
}

function renderAnomalies(data) {
    const container = document.getElementById("anomaliesList");
    const status = document.getElementById("anomalyStatus");

    status.textContent = data.message || "Anomaly analysis completed.";

    if (!data.available || !data.anomalies || !data.anomalies.length) {
        container.innerHTML =
            '<div class="empty-state">No anomaly intervals to display. More timestamp intervals may be needed.</div>';
        return;
    }

    container.innerHTML = data.anomalies.map(item => `
        <article class="anomaly-card">
            <b>Unusual activity · ${escapeHTML(item.time)}</b>
            <span>${item.event_count} events · Anomaly score ${item.anomaly_score}</span>
        </article>
    `).join("");
}

function renderSources(data) {
    const container = document.getElementById("sourcesList");

    if (!data.length) {
        container.innerHTML = '<div class="empty-state">No source data found.</div>';
        return;
    }

    const maximum = Math.max(...data.map(item => item.count), 1);

    container.innerHTML = data.map(item => `
        <div class="source-row">
            <div class="source-meta">
                <b>${escapeHTML(item.source)}</b>
                <span>${item.count} events</span>
            </div>
            <div class="source-track">
                <div style="width:${item.count / maximum * 100}%"></div>
            </div>
        </div>
    `).join("");
}

function renderEvents(events) {
    const container = document.getElementById("eventsTable");

    if (!events.length) {
        container.innerHTML =
            '<tr><td colspan="4" class="empty-state">No events found.</td></tr>';
        return;
    }

    container.innerHTML = events.map(event => `
        <tr>
            <td>${escapeHTML(event.timestamp)}</td>
            <td><span class="severity ${escapeHTML(event.severity)}">${escapeHTML(event.severity)}</span></td>
            <td>${escapeHTML(event.source)}</td>
            <td>${escapeHTML(event.message)}</td>
        </tr>
    `).join("");
}

function displayResults(data) {
    latestAnalysis = data;

    const counts = data.severity_counts;

    document.getElementById("totalLines").textContent =
        data.total_lines.toLocaleString();

    document.getElementById("errorCount").textContent =
        (counts.ERROR + counts.CRITICAL).toLocaleString();

    document.getElementById("errorRate").textContent =
        `${data.error_rate}%`;

    document.getElementById("anomalyCount").textContent =
        data.anomaly_detection.anomalies.length;

    renderChart(
        "severityChart",
        "doughnut",
        Object.keys(counts),
        Object.values(counts),
        "Severity"
    );

    renderChart(
        "timelineChart",
        "line",
        data.timeline.map(item => item.time),
        data.timeline.map(item => item.count),
        "Events"
    );

    renderClusters(data.clustering);
    renderAnomalies(data.anomaly_detection);
    renderSources(data.top_sources);
    renderEvents(data.recent_events);

    document.getElementById("recommendations").innerHTML =
        data.recommendations.map(item =>
            `<li>${escapeHTML(item)}</li>`
        ).join("");

    document.getElementById("explainButton").disabled = false;

    document.getElementById("explanation").classList.remove("visible");
    document.getElementById("explanation").textContent = "";

    document.getElementById("llmStatus").textContent =
        "Analysis ready. Generate an LLM explanation if your API key is configured.";
}

async function analyzeLogs() {
    const file = document.getElementById("logFile").files[0];
    const text = document.getElementById("logText").value.trim();
    const message = document.getElementById("analysisMessage");
    const button = document.getElementById("analyzeButton");

    if (!file && !text) {
        message.textContent = "Upload a file or paste log content first.";
        return;
    }

    if (file && file.size > 5 * 1024 * 1024) {
        message.textContent = "File size must be below 5 MB.";
        return;
    }

    const formData = new FormData();

    if (file) {
        formData.append("file", file);
    } else {
        formData.append("text", text);
    }

    button.disabled = true;
    button.textContent = "Analyzing logs...";
    message.textContent = "Running ML analysis...";

    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Analysis failed.");
        }

        displayResults(data);

        message.textContent =
            `Analysis complete · Cache ${data.cache_status}`;

    } catch (error) {
        message.textContent = error.message;
    } finally {
        button.disabled = false;
        button.innerHTML = 'Run intelligent analysis <span>→</span>';
    }
}

async function explainRootCause() {
    if (!latestAnalysis) return;

    const button = document.getElementById("explainButton");
    const status = document.getElementById("llmStatus");
    const output = document.getElementById("explanation");

    button.disabled = true;
    button.textContent = "Generating explanation...";
    status.textContent = "Sending analysis summary to the LLM...";

    output.classList.remove("visible");
    output.textContent = "";

    try {
        const response = await fetch("/api/explain", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ analysis: latestAnalysis })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Explanation request failed.");
        }

        if (!data.available) {
            status.textContent = data.message;
            return;
        }

        output.textContent = data.explanation;
        output.classList.add("visible");
        status.textContent = `Explanation generated using ${data.model}.`;

    } catch (error) {
        status.textContent = error.message;
    } finally {
        button.disabled = false;
        button.textContent = "Generate AI explanation →";
    }
}

async function checkSystem() {
    try {
        const response = await fetch("/api/health");
        if (!response.ok) throw new Error("Backend unavailable");

        const data = await response.json();

        document.getElementById("sideStatus").textContent =
            `Backend ${data.status}`;

        document.getElementById("sideRedis").textContent =
            `Redis: ${data.redis}`;

        if (!data.ml_available) {
            document.getElementById("sideStatus").textContent =
                "Backend online · ML unavailable";
        }

    } catch {
        document.getElementById("sideStatus").textContent =
            "Backend unavailable";
        document.getElementById("sideRedis").textContent =
            "Check the Python server";
    }
}

checkSystem();











