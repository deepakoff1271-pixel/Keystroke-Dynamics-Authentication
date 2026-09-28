(() => {
  const passwordSelect = document.getElementById('dashboardPassword');
  const perplexityInput = document.getElementById('perplexity');
  const refreshButton = document.getElementById('refreshDashboard');
  const summaryStrip = document.getElementById('summaryStrip');
  const varianceTable = document.getElementById('varianceTable');
  const correlationTable = document.getElementById('correlationTable');
  const knnTable = document.getElementById('knnTable');
  const kdaTable = document.getElementById('kdaTable');

  const varianceChartCanvas = document.getElementById('varianceChart');
  const knnChartCanvas = document.getElementById('knnChart');
  const tsneChartCanvas = document.getElementById('tsneChart');

  if (!passwordSelect) {
    return;
  }

  const chartStore = {};

  const destroyChart = (name) => {
    if (chartStore[name]) {
      chartStore[name].destroy();
      chartStore[name] = null;
    }
  };

  const buildTable = (headers, rows) => {
    const headerHtml = headers.map((header) => `<th>${header}</th>`).join('');
    const rowHtml = rows
      .map((row) => `<tr>${row.map((cell) => `<td>${cell}</td>`).join('')}</tr>`)
      .join('');
    return `<table><thead><tr>${headerHtml}</tr></thead><tbody>${rowHtml}</tbody></table>`;
  };

  const showSummary = async () => {
    const response = await fetch('/api/summary');
    const summary = await response.json();
    summaryStrip.innerHTML = summary
      .map(
        (item) => `
          <article class="summary-card panel">
            <span class="summary-caption">${item.password}</span>
            <strong>${item.avg_std}</strong>
            <div class="summary-caption">${item.keystrokes} keys · ${item.dimensions} dims · entropy ${item.entropy}</div>
          </article>
        `,
      )
      .join('');
  };

  const showVariance = async (password) => {
    const response = await fetch(`/api/variance`);
    const payload = await response.json();
    const selected = payload[password] || {};
    const labels = Object.keys(selected);
    const values = Object.values(selected);

    varianceTable.innerHTML = buildTable(['Group', 'Std. Dev.'], labels.map((label, index) => [label, values[index]]));

    destroyChart('variance');
    chartStore.variance = new Chart(varianceChartCanvas, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Average standard deviation',
          data: values,
          backgroundColor: 'rgba(57, 208, 197, 0.7)',
          borderColor: 'rgba(57, 208, 197, 1)',
          borderWidth: 1,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } },
      },
    });
  };

  const showCorrelation = async (password) => {
    const response = await fetch(`/api/correlation?password=${encodeURIComponent(password)}`);
    const payload = await response.json();
    const labels = Object.keys(payload);
    const headerRow = ['Participant', ...labels];
    const rows = labels.map((label) => [label, ...labels.map((inner) => payload[label][inner])]);
    correlationTable.innerHTML = buildTable(headerRow, rows);
  };

  const showKnn = async (password) => {
    const response = await fetch(`/api/knn?password=${encodeURIComponent(password)}&k=3`);
    const payload = await response.json();
    const labels = Object.keys(payload);
    const metrics = ['TAR', 'FRR', 'TRR', 'FAR'];
    const rows = labels.map((label) => [label, ...metrics.map((metric) => payload[label][metric])]);
    knnTable.innerHTML = buildTable(['Participant', ...metrics], rows);

    destroyChart('knn');
    chartStore.knn = new Chart(knnChartCanvas, {
      type: 'bar',
      data: {
        labels,
        datasets: metrics.map((metric, index) => ({
          label: metric,
          data: labels.map((label) => payload[label][metric]),
          backgroundColor: [
            'rgba(244, 179, 93, 0.78)',
            'rgba(255, 99, 132, 0.68)',
            'rgba(57, 208, 197, 0.68)',
            'rgba(140, 208, 255, 0.68)',
          ][index],
        })),
      },
      options: {
        responsive: true,
        scales: { y: { beginAtZero: true, max: 1 } },
      },
    });
  };

  const showKda = async (password) => {
    const response = await fetch(`/api/correlation_kda?password=${encodeURIComponent(password)}`);
    const payload = await response.json();
    const rows = Object.entries(payload).map(([label, values]) => [
      label,
      values.self_correlation,
      values.attack_correlation,
      `${values.EER}%`,
      values.FRR_at_FAR0 + '%',
    ]);
    kdaTable.innerHTML = buildTable(['Participant', 'Self corr.', 'Attack corr.', 'EER', 'FRR @ FAR0'], rows);
  };

  const showTsne = async (password) => {
    const perplexity = perplexityInput ? perplexityInput.value : 30;
    const response = await fetch(`/api/tsne?password=${encodeURIComponent(password)}&perplexity=${encodeURIComponent(perplexity)}`);
    const payload = await response.json();

    const groups = payload.reduce((accumulator, point) => {
      if (!accumulator[point.label]) {
        accumulator[point.label] = [];
      }
      accumulator[point.label].push(point);
      return accumulator;
    }, {});

    destroyChart('tsne');
    chartStore.tsne = new Chart(tsneChartCanvas, {
      type: 'scatter',
      data: {
        datasets: Object.entries(groups).map(([label, points]) => ({
          label,
          data: points.map((point) => ({ x: point.x, y: point.y })),
          backgroundColor: points[0]?.color || '#cbd5e1',
          borderColor: points[0]?.color || '#cbd5e1',
          pointRadius: 5,
        })),
      },
      options: {
        responsive: true,
        plugins: { legend: { position: 'bottom' } },
        scales: { x: { title: { display: true, text: 'Component 1' } }, y: { title: { display: true, text: 'Component 2' } } },
      },
    });
  };

  const refresh = async () => {
    const password = passwordSelect.value;
    await showSummary();
    await Promise.all([
      showVariance(password),
      showCorrelation(password),
      showKnn(password),
      showKda(password),
      showTsne(password),
    ]);
  };

  document.querySelectorAll('.tab-button').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('.tab-button').forEach((item) => item.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach((item) => item.classList.remove('active'));
      button.classList.add('active');
      document.getElementById(`tab-${button.dataset.tab}`).classList.add('active');
    });
  });

  passwordSelect.addEventListener('change', refresh);
  if (refreshButton) {
    refreshButton.addEventListener('click', refresh);
  }
  if (perplexityInput) {
    perplexityInput.addEventListener('change', refresh);
  }

  refresh();
})();
