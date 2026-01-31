document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadTopEndpoints();
    loadTopIPs();
    loadRequestsOverTime();
});

function loadStats() {
    fetch('http://localhost:8000/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-logs').textContent = data.total_logs;
            document.getElementById('error-4xx').textContent = data.error_4xx_percentage + '%';
            document.getElementById('error-5xx').textContent = data.error_5xx_percentage + '%';
        })
        .catch(error => console.error('Error loading stats:', error));
}

function loadTopEndpoints() {
    fetch('http://localhost:8000/top-endpoints')
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById('top-endpoints');
            list.innerHTML = '';
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.endpoint}: ${item.count}`;
                list.appendChild(li);
            });
        })
        .catch(error => console.error('Error loading top endpoints:', error));
}

function loadTopIPs() {
    fetch('http://localhost:8000/top-ips')
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById('top-ips');
            list.innerHTML = '';
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.ip}: ${item.count}`;
                list.appendChild(li);
            });
        })
        .catch(error => console.error('Error loading top IPs:', error));
}

function loadRequestsOverTime() {
    fetch('http://localhost:8000/requests-over-time')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('requestsChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Requests',
                        data: data.data,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Time'
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Request Count'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading requests over time:', error));
}

function searchLogs() {
    const query = document.getElementById('search-query').value;
    fetch(`http://localhost:8000/search?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            const resultsDiv = document.getElementById('search-results');
            resultsDiv.innerHTML = '';
            
            if (data.type === 'logs') {
                resultsDiv.innerHTML = '<h3>Search Results:</h3>';
                if (data.data.length > 0) {
                    const table = document.createElement('table');
                    table.innerHTML = `
                        <tr>
                            <th>IP</th>
                            <th>Timestamp</th>
                            <th>Method</th>
                            <th>Endpoint</th>
                            <th>Status</th>
                            <th>Size</th>
                        </tr>
                    `;
                    data.data.forEach(log => {
                        const row = table.insertRow();
                        row.innerHTML = `
                            <td>${log.ip}</td>
                            <td>${log.timestamp}</td>
                            <td>${log.method}</td>
                            <td>${log.endpoint}</td>
                            <td>${log.status}</td>
                            <td>${log.size}</td>
                        `;
                    });
                    resultsDiv.appendChild(table);
                } else {
                    resultsDiv.innerHTML += '<p>No logs found.</p>';
                }
            } else if (data.type === 'analysis') {
                resultsDiv.innerHTML = '<h3>🔍 Security Analysis:</h3>';
                data.data.forEach(insight => {
                    resultsDiv.innerHTML += `
                        <div class="insight">
                            <h4>${insight.category} <span class="risk-${insight.risk_level}">${insight.risk_level}</span></h4>
                            <p><strong>Count:</strong> ${insight.count}</p>
                            ${insight.source_ip ? `<p><strong>Source IP:</strong> ${insight.source_ip}</p>` : ''}
                            ${insight.sample ? `<p><strong>Sample:</strong> ${insight.sample}</p>` : ''}
                            <p><strong>Insight:</strong> ${insight.insight}</p>
                        </div>
                    `;
                });
            }
        })
        .catch(error => {
            console.error('Error searching logs:', error);
            document.getElementById('search-results').innerHTML = '<p>Error: Could not fetch results.</p>';
        });
}
