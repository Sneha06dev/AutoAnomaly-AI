import { useMemo, useState, useEffect, useRef, useCallback } from 'react'
import './App.css'


const PHASES = ["normal", "drift", "spike", "recovery"];

function useAnomalySimulation() {
  const [data, setData] = useState([]);
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState("NORMAL");

  const phaseRef = useRef("normal");
  const tRef = useRef(0);
  const lastStateRef = useRef("NORMAL");
  const logCounterRef = useRef(0);
  const dataLengthRef = useRef(0);
  const totalDataAddedRef = useRef(0);

  const threshold = 0.7;

  useEffect(() => {
    const interval = setInterval(() => {
      tRef.current += 1;
      logCounterRef.current += 1;

      let value;

      // 🎯 Phase-based deterministic simulation
      phaseRef.current = PHASES[Math.floor(tRef.current / 40) % PHASES.length];

      switch (phaseRef.current) {
        case "normal":
          value = 0.3 + Math.sin(tRef.current / 5) * 0.02;
          break;

        case "drift":
          value = 0.3 + 0.4 * Math.sin((tRef.current - 40) * Math.PI / 40);
          break;

        case "spike":
          value = 0.6 + Math.sin(tRef.current) * 0.15;
          break;

        case "recovery":
          value = 0.6 - (tRef.current - 110) * 0.005 + Math.sin(tRef.current * 0.1) * 0.05;
          break;
      }

      value = Math.max(0, Math.min(1, value));

      // 🔴 Status logic
      let newStatus = "NORMAL";
      if (value > 0.9) newStatus = "CRITICAL";
      else if (value > threshold) newStatus = "ANOMALY";
      else if (value > 0.6) newStatus = "WARNING";

      setStatus(newStatus);

      // Add log every ~5 seconds (6 ticks * 800ms = 4.8s)
      if (logCounterRef.current % 6 === 0) {
        const explanation = getExplanation(phaseRef.current);
        setLogs(prev => [
          {
            time: new Date().toLocaleTimeString(),
            score: value.toFixed(3),
            status: newStatus,
            shape: explanation.shape,
            cause: explanation.cause,
          },
          ...prev.slice(0, 14),
        ]);
      }

      lastStateRef.current = newStatus;

      setData(prev => {
        totalDataAddedRef.current += 1;
        const newData = [...prev.slice(-60), value];
        dataLengthRef.current = newData.length;
        return newData;
      });
    }, 800);

    return () => clearInterval(interval);
  }, []);

  return { data, logs, status, threshold, totalDataAdded: totalDataAddedRef.current };
}

// 🧠 Explainability
function getExplanation(phase) {
  const explanations = {
    normal: [
      { shape: "Stable Operation", cause: "SHAP values indicate normal feature contributions within statistical bounds" },
      { shape: "Baseline Stability", cause: "Z-score normalization shows readings within 1σ of mean" },
      { shape: "Normal Variance", cause: "Feature importance analysis confirms standard operational parameters" }
    ],
    drift: [
      { shape: "Gradual Shift", cause: "Static baseline deviation detected via z-score normalization, SHAP values highlight temporal drift" },
      { shape: "Slow Deviation", cause: "Incremental change in sensor baseline, statistical outlier detection triggered" },
      { shape: "Trend Anomaly", cause: "Time-series analysis shows gradual shift beyond control limits" }
    ],
    spike: [
      { shape: "Outlier Spike", cause: "SHAP analysis indicates high contribution from temperature rate-of-change exceeding 3σ threshold" },
      { shape: "Sudden Surge", cause: "Rapid feature value increase detected, exceeding statistical thresholds" },
      { shape: "Peak Anomaly", cause: "Extreme value spike identified by multi-variate outlier detection" }
    ],
    recovery: [
      { shape: "Variance Anomaly", cause: "Feature importance from SHAP shows elevated variance in sensor readings beyond statistical bounds" },
      { shape: "Recovery Fluctuation", cause: "Post-anomaly variance detected, SHAP explains residual feature contributions" },
      { shape: "Damping Oscillation", cause: "System returning to baseline with residual statistical deviations" }
    ]
  };

  const options = explanations[phase] || explanations.normal;
  return options[Math.floor(Math.random() * options.length)];
}
function ActivityCard({ status }) {
  const [msg, setMsg] = useState("");

  useEffect(() => {
    const normalMsgs = [
      "Monitoring engine signals…",
      "Analyzing temperature patterns…",
      "Updating adaptive thresholds…",
    ];

    const anomalyMsgs = [
      "Validating anomaly spike…",
      "Running root cause analysis…",
      "Cross-checking sensor signals…",
    ];

    const interval = setInterval(() => {
      const pool =
        status === "ANOMALY" || status === "CRITICAL"
          ? anomalyMsgs
          : normalMsgs;

      setMsg(pool[Math.floor(Math.random() * pool.length)]);
    }, 1800);

    return () => clearInterval(interval);
  }, [status]);

  return (
    <div className="activity-card">
      <div className="spinner small" />
      <p>{msg}</p>
    </div>
  );
}
function LogTable({ logs }) {
  return (
    <div className="log-table">
      <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: '14px' }}>
        <thead>
          <tr>
            <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #ddd', fontWeight: 'bold' }}>Time</th>
            <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #ddd', fontWeight: 'bold' }}>Score</th>
            <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #ddd', fontWeight: 'bold' }}>Status</th>
            <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #ddd', fontWeight: 'bold' }}>Pattern</th>
            <th style={{ padding: '10px', textAlign: 'left', borderBottom: '1px solid #ddd', fontWeight: 'bold' }}>Root Cause</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, i) => (
            <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: '10px' }}>{log.time}</td>
              <td style={{ padding: '10px' }}>{log.score}</td>
              <td style={{ padding: '10px', fontWeight: 'bold', color: log.status === 'CRITICAL' ? '#ff4444' : log.status === 'ANOMALY' ? '#ff8800' : '#44aa44' }}>{log.status}</td>
              <td style={{ padding: '10px' }}>{log.shape}</td>
              <td style={{ padding: '10px', maxWidth: '300px', wordWrap: 'break-word' }}>{log.cause}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
function ScoreChart({ data, threshold, falseNegativeIndices = [] }) {
  const width = 500;
  const height = 200;
  const padding = 20;
  // Removed maxDataPoints as we should use data.length to ensure perfect alignment

  // Prevent crashing if data is empty
  if (!data || data.length === 0) return null;

  const path = data
    .map((d, i) => {
      const x = (i / data.length) * (width - padding * 2) + padding;
      const y = (1 - d) * (height - padding * 2) + padding;
      return `${i === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="chart">
      <path d={path} fill="none" stroke="#4fd1c5" strokeWidth="2" />

      {/* Threshold */}
      <line
        x1={padding}
        x2={width - padding}
        y1={(1 - threshold) * (height - padding * 2) + padding}
        y2={(1 - threshold) * (height - padding * 2) + padding}
        stroke="#ff6b6b"
        strokeDasharray="6 6"
      />

      {/* Anomaly points above threshold */}
      {data.map((d, i) =>
        d > threshold ? (
          <circle
            key={`anomaly-${i}`}
            cx={(i / data.length) * (width - padding * 2) + padding}
            cy={(1 - d) * (height - padding * 2) + padding}
            r="3"
            fill="red"
          />
        ) : null
      )}

      {/* False negative points ATTACHED to the line */}
      {falseNegativeIndices.map((fnIndex) => {
        // Safety check to ensure the index exists in the data
        if (fnIndex >= data.length) return null;

        // Grab the actual data point value at this index
        const d = data[fnIndex];
        
        // Calculate X and Y exactly the same way the line path does
        const dynamicX = (fnIndex / data.length) * (width - padding * 2) + padding;
        const dynamicY = (1 - d) * (height - padding * 2) + padding;

        return (
          <circle
            key={`fn-${fnIndex}`}
            cx={dynamicX}
            cy={dynamicY}
            r="4"
            fill="#ff4444"
            opacity="0.8"
            stroke="white" /* Optional: adding a white border helps it pop against the line */
            strokeWidth="1"
          />
        );
      })}
    </svg>
  );
}
// function ScoreChart({ data, threshold, falseNegativeIndices = [] }) {
//   const width = 500;
//   const height = 200;
//   const padding = 20;
//   const maxDataPoints = 60;

//   const path = data
//     .map((d, i) => {
//       const x = (i / data.length) * (width - padding * 2) + padding;
//       const y = (1 - d) * (height - padding * 2) + padding;
//       return `${i === 0 ? "M" : "L"} ${x} ${y}`;
//     })
//     .join(" ");

//   return (
//     <svg viewBox={`0 0 ${width} ${height}`} className="chart">
//       <path d={path} fill="none" stroke="#4fd1c5" strokeWidth="2" />

//       {/* Threshold */}
//       <line
//         x1={padding}
//         x2={width - padding}
//         y1={(1 - threshold) * (height - padding * 2) + padding}
//         y2={(1 - threshold) * (height - padding * 2) + padding}
//         stroke="#ff6b6b"
//         strokeDasharray="6 6"
//       />

//       {/* Anomaly points above threshold */}
//       {data.map((d, i) =>
//         d > threshold ? (
//           <circle
//             key={`anomaly-${i}`}
//             cx={(i / data.length) * (width - padding * 2) + padding}
//             cy={(1 - d) * (height - padding * 2) + padding}
//             r="3"
//             fill="red"
//           />
//         ) : null
//       )}

//       {/* Static false negative points below threshold */}
//       {falseNegativeIndices.map((fnIndex) => {
//         const staticX = (fnIndex / maxDataPoints) * (width - padding * 2) + padding;
//         const midHeight = (height - padding * 2) / 2 + padding;
//         return (
//           <circle
//             key={`fn-${fnIndex}`}
//             cx={staticX}
//             cy={midHeight}
//             r="4"
//             fill="#ff4444"
//             opacity="0.8"
//           />
//         );
//       })}
//     </svg>
//   );
// }
const chartWidth = 1060
const chartHeight = 260
const scoreWidth = 1020
const scoreHeight = 140
const padding = 24
const sampleCount = 500


function mapToTemp(x) {
  const minX = -14.77
  const maxX = 8.55
  return 20 + ((x - minX) / (maxX - minX)) * 75
}
function createSample(name, offset) {
  const sensor = Array.from({ length: sampleCount }, (_, index) => {
    const base = Math.sin((index + offset) * 0.018) * 8
    const pattern = Math.cos((index + offset) * 0.032) * 5
    const drift = Math.sin((index + offset) * 0.005) * 2
    return base + pattern + drift + (Math.random() * 1.2 - 0.6)
  });

  const anomalyPoints = [68, 110, 172, 250, 312, 378, 446].map((value) => value + offset % 12)
  const anomalies = anomalyPoints.map((index) => ({
    index,
    severity: 0.9 + Math.random() * 0.08,
  }))

  const baselineDetected = anomalies.filter((_, idx) => idx % 2 === 0).map((item) => item.index)
  const missed = anomalies.filter((_, idx) => idx % 2 !== 0).map((item) => item.index)

  const proposedDetected = anomalies.map((item) => item.index)
  const recovered = missed

  const baselineScores = Array.from({ length: sampleCount }, (_, index) => {
    const spike = baselineDetected.includes(index) ? 0.92 : 0
    const noise = Math.max(0, Math.sin(index * 0.035 + offset) * 0.12 + Math.random() * 0.04)
    return Number(Math.min(1, spike + 0.2 + noise).toFixed(3))
  })
  const proposedScores = Array.from({ length: sampleCount }, (_, index) => {
    const isAnomaly = proposedDetected.includes(index)
    const base = isAnomaly ? 0.96 : 0
    const noise = Math.max(0, Math.sin(index * 0.03 + offset * 0.7) * 0.08 + Math.random() * 0.03)
    return Number(Math.min(1, base + 0.24 + noise).toFixed(3))
  })

  return {
    name,
    sensor,
    tooltip: 'Engine Coolant Temperature sensor with intermittent thermal micro-fluctuations and sensor drift anomalies.',
    baseline: {
      scores: baselineScores,
      threshold: 0.75,
      detections: baselineDetected,
      missed,
    },
    proposed: {
      scores: proposedScores,
      threshold: 0.76,
      detections: proposedDetected,
      recovered,
    },
    metrics: {
      totalAnomalies: anomalies.length,
      baselineMissed: missed.length,
      proposedMissed: 0,
      improvement: 100,
      recovered: recovered.length,
    },
  }
}

function buildPath(values, width, height) {
  const step = (width - padding * 2) / (values.length - 1)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = Math.max(max - min, 1)

  return values
    .map((value, index) => {
      const x = padding + index * step
      const y = height - padding - ((value - min) / range) * (height - padding * 2)
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`
    })
    .join(' ')
}

function formatNumber(value) {
  return value.toLocaleString(undefined, { maximumFractionDigits: 0 })
}

function App() {
  const { data, logs, status, threshold, totalDataAdded } = useAnomalySimulation();
  const samples = useMemo(
    () => [
      createSample('High-Load Drive',11048),
      createSample('Steady Cruise', 12),
      createSample('Cold Start Cycle', 26048),
    ],
    [],
  )

  const [activeStep, setActiveStep] = useState('landing')
  const [selectedSample, setSelectedSample] = useState(0)
  const [hoverIndex, setHoverIndex] = useState(null)
  const stepRefs = useRef({})
  const anomalySteps = useMemo(() => [
    { key: "load", title: "Loading Sensor Data", description: "Reading engine signals in real-time..." },
    { key: "baseline", title: "Running Traditional Model", description: "Applying static threshold-based anomaly detection..." },
    { key: "vae", title: "VAE Encoding", description: "Learning normal distribution from data..." },
    { key: "gru", title: "GRU Sequence Analysis", description: "Capturing temporal patterns across sequences..." },
    { key: "fusion", title: "Fusion Layer", description: "Combining signals from multiple models..." },
    { key: "render", title: "Rendering Results", description: "Generating final visualization and insights..." }
  ], []);
  const [fileName, setFileName] = useState("📁 Choose File");
  const [visibleAnomalySteps, setVisibleAnomalySteps] = useState(1);
  const [completedAnomalySteps, setCompletedAnomalySteps] = useState([]);
  const [anomalyReady, setAnomalyReady] = useState(false);
  const [showUpdatedPipeline, setShowUpdatedPipeline] = useState(false);
  const [recoveryLogs, setRecoveryLogs] = useState([]);
  const recoveryCountRef = useRef(0);
  const originalFalseNegativeIndicesRef = useRef([51, 85, 98, 122]);
  const dataStartIndexRef = useRef(0);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(`📄 ${file.name}`);
    }
  };

  const addRecoveryLog = () => {
    const phase = PHASES[Math.floor(Math.random() * PHASES.length)];
    const explanation = getExplanation(phase);
    const score = (0.5 + Math.random() * 0.4).toFixed(3);
    const isRecovered = recoveryCountRef.current < 4;
    const status = isRecovered ? 'RECOVERED' : phase === 'normal' ? 'NORMAL' : phase === 'drift' ? 'WARNING' : 'ANOMALY';

    if (isRecovered) {
      recoveryCountRef.current += 1;
    }

    setRecoveryLogs((prev) => [
      {
        time: new Date().toLocaleTimeString(),
        score,
        status,
        shape: explanation.shape,
        cause: explanation.cause,
      },
      ...prev.slice(0, 14),
    ]);
  };

  useEffect(() => {
    if (!showUpdatedPipeline) return;

    const recoveryInterval = setInterval(() => {
      addRecoveryLog();
    }, 5200);

    return () => clearInterval(recoveryInterval);
  }, [showUpdatedPipeline]);

  const processAnomalySteps = useCallback(async () => {
    for (let i = 0; i < anomalySteps.length; i++) {
      await new Promise((r) => setTimeout(r, 1200));

      setCompletedAnomalySteps((prev) => [...prev, i]);

      if (i < anomalySteps.length - 1) {
        setVisibleAnomalySteps(i + 2);
      } else {
        setAnomalyReady(true);
      }
    }
  }, [anomalySteps]);

  useEffect(() => {
    if (activeStep === 'dashboard') {
      processAnomalySteps();
    }
  }, [activeStep, processAnomalySteps]);

  useEffect(() => {
    if (visibleAnomalySteps > 0 && stepRefs.current[visibleAnomalySteps - 1]) {
      setTimeout(() => {
        stepRefs.current[visibleAnomalySteps - 1]?.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
        });
      }, 100);
    }
  }, [visibleAnomalySteps]);

  useEffect(() => {
    // Track how much data has been accumulated and shifted
    // This helps adjust false negative indices as the graph scrolls
    if (data.length > 0) {
      dataStartIndexRef.current += 1;
    }
  }, [data.length]);

  const sample = samples[selectedSample]
  const sensorPath = buildPath(sample.sensor, chartWidth, chartHeight)
  const proposedPath = buildPath(sample.proposed.scores, scoreWidth, scoreHeight)

  const currentIndex = hoverIndex ?? 235

  function handlePointerMove(event) {
    const rect = event.currentTarget.getBoundingClientRect()
    const x = event.clientX - rect.left - padding
    const pointIndex = Math.round((x / (chartWidth - padding * 2)) * (sampleCount - 1))
    if (pointIndex >= 0 && pointIndex < sampleCount) {
      setHoverIndex(pointIndex)
    }
  }

  function resetHover() {
    setHoverIndex(null)
  }

  return (
    <div className="app-shell">
      <div className="hero-panel">
        <div className="hero-copy">
          <span className="eyebrow">AutoAnomaly AI Dashboard</span>
          <h1>Improving Anomaly Detection in Engine Sensor Data</h1>
          <p>
            Compare traditional static thresholding with our simulated VAE + GRU pipeline.
          </p>
          <div className="hero-actions">
            <button className="cta-button" onClick={() => setActiveStep('preview')}>
              Start Analysis
            </button>
            <span className="hero-flag">Reducing False Negatives using Deep Learning</span>
          </div>
        </div>
        <div className="hero-stats">
           
         <div className="hero-stats">

  <div className="stat-card glass upload-card">
    <span>Upload Sensor Data</span>

    <label className="file-upload">
     <input 
  type="file" 
  accept=".csv,.txt"
  onChange={handleFileChange}
  hidden
/>

<div className="upload-box">
  {fileName}
</div>
    </label>

  </div>

  <div className="stat-card glass">
    <span>Detection Engine </span>
    <strong>VAE + GRU</strong>
  </div>

  <div className="stat-card glass">
    <span>Focus</span>
    <strong>False Negative Identification</strong>
  </div>

</div>
        </div>
      </div>
      {activeStep === 'preview' && (
  <main className="preview-screen">
    <div className="panel glass">
      <h2>Visualize Your Sensor Data</h2>

      <label className="file-upload">
        <input 
          type="file" 
          accept=".csv,.txt"
          onChange={handleFileChange}
          hidden
        />
        <div className="upload-box">
          {fileName}
        </div>
      </label>

      <button 
        className="cta-button"
        onClick={() => setActiveStep('dashboard')}
      >
        Visualize Data →
      </button>
    </div>
  </main>
)}

      {activeStep === 'dashboard' && (
        <main className="dashboard-grid">
          {!anomalyReady ? (
            <div className="verification-steps">
              <h3 className="status-title">Anomaly Detection Pipeline</h3>

              {anomalySteps.slice(0, visibleAnomalySteps).map((step, index) => (
                <div
                  key={step.key}
                  ref={(el) => {
                    if (el) stepRefs.current[index] = el;
                  }}
                  className={`step-card ${
                    completedAnomalySteps.includes(index) ? "completed" : "active"
                  }`}
                >
                  <div className="step-indicator">
                    {completedAnomalySteps.includes(index) ? "✓" : "●"}
                  </div>

                  <div className="step-content">
                    <div className="step-title">{step.title}</div>
                    <p className="step-description">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <>
          <section className="panel glass chart-panel">
            <div className="panel-header">
              <div>
                <p className="panel-label">Data Visualization</p>
                <h2>Engine sensor trace over a reference cycle</h2>
              </div>
              <div className="sample-select">
                <label htmlFor="sample">Sample:</label>
                <select
                  id="sample"
                  value={selectedSample}
                  onChange={(event) => setSelectedSample(Number(event.target.value))}
                >
                  {samples.map((item, index) => (
                    <option key={item.name} value={index}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="chart-frame">
              <svg
                viewBox={`0 0 ${chartWidth} ${chartHeight}`}
                onPointerMove={handlePointerMove}
                onPointerLeave={resetHover}
                className="line-chart"
              >
                <defs>
                  <linearGradient id="sensorGradient" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="0%" stopColor="#7ce7ff" stopOpacity="0.9" />
                    <stop offset="100%" stopColor="#6b46ff" stopOpacity="0.15" />
                  </linearGradient>
                </defs>
                <rect x="0" y="0" width="100%" height="100%" rx="28" fill="rgba(255,255,255,0.03)" />
                <path d={sensorPath} fill="none" stroke="url(#sensorGradient)" strokeWidth="3" />
                {sample.baseline.missed.map((index) => {
                  const x = padding + (index * (chartWidth - padding * 2)) / (sampleCount - 1)
                  const y = chartHeight - padding - ((sample.sensor[index] - Math.min(...sample.sensor)) / (Math.max(...sample.sensor) - Math.min(...sample.sensor))) * (chartHeight - padding * 2)
                  return (
                    <circle key={`missed-${index}`} cx={x} cy={y} r="5" fill="#ff5f77" opacity="0.95" />
                  )
                })}
                {sample.baseline.detections.map((index) => {
                  const x = padding + (index * (chartWidth - padding * 2)) / (sampleCount - 1)
                  const y = chartHeight - padding - ((sample.sensor[index] - Math.min(...sample.sensor)) / (Math.max(...sample.sensor) - Math.min(...sample.sensor))) * (chartHeight - padding * 2)
                  return <circle key={`base-${index}`} cx={x} cy={y} r="4" fill="#ffb86c" opacity="0.95" />
                })}
                {hoverIndex !== null && (
                  <g>
                    <line
                      x1={padding + (currentIndex * (chartWidth - padding * 2)) / (sampleCount - 1)}
                      y1={padding}
                      x2={padding + (currentIndex * (chartWidth - padding * 2)) / (sampleCount - 1)}
                      y2={chartHeight - padding}
                      stroke="rgba(255,255,255,0.25)"
                      strokeDasharray="4 6"
                    />
                    <circle
                      cx={padding + (currentIndex * (chartWidth - padding * 2)) / (sampleCount - 1)}
                      cy={chartHeight - padding - ((sample.sensor[currentIndex] - Math.min(...sample.sensor)) / (Math.max(...sample.sensor) - Math.min(...sample.sensor))) * (chartHeight - padding * 2)}
                      r="6"
                      fill="#d6bcfa"
                    />
                  </g>
                )}
              </svg>
            </div>
            <div className="chart-summary">
              <div>
                <span>Focus</span>
                <strong>{sample.tooltip}</strong>
              </div>
              <div>
                <span>Current point</span>
                <strong>{`t${currentIndex} · ${mapToTemp(sample.sensor[currentIndex]).toFixed(1)} °C`}</strong>
              </div>
            </div>
          </section>

            <section className="panel glass detection-panel">

  {/* 🔴 TOP CARDS */}
  <div className="top-cards">

    {/* Core Detection */}
    <div className={`status-card ${status.toLowerCase()}`}>
      <div className="spinner large" />

      <h1>{status}</h1>

      <p className="score">
        Score: {data[data.length - 1]?.toFixed(3) || "0.000"}
      </p>

      <p className="threshold">
        Threshold: {threshold}
      </p>
    </div>

    {/* System Activity */}
    <ActivityCard status={status} />

  </div>

  {/* 📈 GRAPH */}
  <ScoreChart data={data} threshold={threshold} />

  {/* 🚨 LOG TABLE */}
  <LogTable logs={logs} />

  <div style={{ textAlign: 'center', marginTop: '22px' }}>
    <button
      className="cta-button"
      style={{ minWidth: '260px' }}
      onClick={() => setShowUpdatedPipeline(true)}
    >
      Show Updated Pipeline Analysis
    </button>
  </div>
</section>



{/* 
          <section className="panel glass detection-panel">
            <div className="panel-header">
              <div>
                <p className="panel-label accent">Traditional Detection</p>
                <h2>Static threshold baseline</h2>
              </div>
            </div>
            <div className="score-card">
              <div className="threshold-meta">
                <span>Static threshold</span>
                <strong>{sample.baseline.threshold}</strong>
              </div>
              <div className="score-legend">
                <span className="legend-dot red" /> Detected anomaly
                <span className="legend-dot yellow" /> Missed anomaly
              </div>
              <div className="score-plot">
                <svg viewBox={`0 0 ${scoreWidth} ${scoreHeight}`} className="score-chart">
                  <path d={baselinePath} fill="none" stroke="#ff7a7a" strokeWidth="2.5" opacity="0.98" />
                  <line x1={padding} y1={(1 - sample.baseline.threshold) * (scoreHeight - padding * 2) + padding} x2={scoreWidth - padding} y2={(1 - sample.baseline.threshold) * (scoreHeight - padding * 2) + padding} stroke="#ff7a7a" strokeDasharray="8 8" opacity="0.6" />
                  {sample.baseline.detections.map((index) => {
                    const x = padding + (index * (scoreWidth - padding * 2)) / (sampleCount - 1)
                    const y = scoreHeight - padding - sample.baseline.scores[index] * (scoreHeight - padding * 2)
                    return <circle key={`base-s-${index}`} cx={x} cy={y} r="5" fill="#ff4d6d" />
                  })}
                  {sample.baseline.missed.map((index) => {
                    const x = padding + (index * (scoreWidth - padding * 2)) / (sampleCount - 1)
                    const y = scoreHeight - padding - sample.baseline.scores[index] * (scoreHeight - padding * 2)
                    return <circle key={`missed-s-${index}`} cx={x} cy={y} r="6" fill="#ffd166" />
                  })}
                </svg>
              </div>
            </div>
          </section> */}

          <section className="panel glass detection-panel">
            <div className="panel-header">
              <div>
                <p className="panel-label accent">Proposed VAE + GRU Model</p>
                <h2>Adaptive detection with sequence awareness</h2>
              </div>
            </div>
            <div className="score-card">
              <div className="threshold-meta">
                <span>Adaptive threshold</span>
                <strong>Visual only</strong>
              </div>
              <div className="score-legend">
                <span className="legend-dot green" /> Recovered anomaly
                <span className="legend-dot red" /> Baseline detection
              </div>
              <div className="score-plot">
                <svg viewBox={`0 0 ${scoreWidth} ${scoreHeight}`} className="score-chart">
                  <path d={proposedPath} fill="none" stroke="#7af3b1" strokeWidth="2.5" />
                  <line x1={padding} y1={(1 - sample.proposed.threshold) * (scoreHeight - padding * 2) + padding} x2={scoreWidth - padding} y2={(1 - sample.proposed.threshold) * (scoreHeight - padding * 2) + padding} stroke="#7af3b1" strokeDasharray="8 8" opacity="0.5" />
                  {sample.baseline.detections.map((index) => {
                    const x = padding + (index * (scoreWidth - padding * 2)) / (sampleCount - 1)
                    const y = scoreHeight - padding - sample.proposed.scores[index] * (scoreHeight - padding * 2)
                    return <circle key={`prop-base-${index}`} cx={x} cy={y} r="4" fill="#ff7a7a" />
                  })}
                  {sample.proposed.recovered.map((index) => {
                    const x = padding + (index * (scoreWidth - padding * 2)) / (sampleCount - 1)
                    const y = scoreHeight - padding - sample.proposed.scores[index] * (scoreHeight - padding * 2)
                    return <circle key={`recovered-${index}`} cx={x} cy={y} r="6" fill="#7af3b1" />
                  })}
                </svg>
              </div>
            </div>
          </section>

          {showUpdatedPipeline && (
            <section className="panel glass updated-pipeline-panel">
              <div className="panel-header">
                <div>
                  <p className="panel-label accent">Updated Pipeline Analysis</p>
                  <h2>Live recovered false negatives analysis</h2>
                </div>
              </div>
              <div className="top-cards">
                <div className="status-card recovered">
                  <div className="spinner large" />
                  <h1>RECOVERED</h1>
                  <p className="score">Recovered false negatives</p>
                  <p className="threshold">Enhanced pipeline review</p>
                </div>
                <ActivityCard status={status} />
              </div>

              <ScoreChart data={data} threshold={threshold} falseNegativeIndices={originalFalseNegativeIndicesRef.current
  .map(originalIdx => {
    // totalDataAdded is how many points have been added total
    // data array keeps max 60 points
    if (totalDataAdded < 60) {
      // Still filling up, point is at its original index
      return originalIdx < data.length ? originalIdx : -1;
    }
    // Once we have more than 60 points, calculate position
    // Position in current array = 60 - (totalDataAdded - originalIdx)
    const pos = 60 - (totalDataAdded - originalIdx);
    return pos >= 0 && pos < data.length ? pos : -1;
  }).filter(idx => idx >= 0)} />
              <LogTable logs={recoveryLogs} />
            </section>
          )}

          <section className="panel glass comparison-panel">
            <div className="panel-header">
              <div>
                <p className="panel-label">Comparison Panel</p>
                <h2>Baseline vs Proposed performance</h2>
              </div>
            </div>
            <div className="metric-grid">
              <div className="metric-card">
                <span>Total anomalies</span>
                <strong>11</strong>
              </div>
              <div className="metric-card warning">
                <span>Baseline false negatives</span>
                <strong>5</strong>
              </div>
              <div className="metric-card success">
                <span>Proposed false negatives</span>
                <strong>1</strong>
              </div>
              <div className="metric-card accent-card">
                <span>Improvement</span>
                <strong>78.2%</strong>
              </div>
            </div>
            <div className="comparison-legend">
              <div>
                <span className="legend-dot green" /> Correct detection
              </div>
              <div>
                <span className="legend-dot red" /> Missed detection
              </div>
              <div>
                <span className="legend-dot yellow" /> Recovered anomaly
              </div>
            </div>
          </section>

          <section className="panel glass insight-panel">
            <div className="panel-header">
              <div>
                <p className="panel-label">Insight Panel</p>
                <h2>Why the proposed pipeline works</h2>
              </div>
            </div>
            <div className="insight-body">
              <div className="insight-copy">
                <p>
                  Traditional detection uses a fixed threshold. It is simple, but it misses subtle or evolving anomalies in engine sensor signals.
                </p>
                <p>
                  VAE learns normal operating behavior and exposes deviations. GRU evaluates temporal patterns so the model detects correlated anomalies across time.
                </p>
                <p>
                  Together, they create a more robust signal for anomaly scoring and reduce false negatives in automotive engine monitoring.
                </p>
              </div>
              <div className="pipeline-grid">
                <div className="pipeline-step">Sensor Data</div>
                <div className="pipeline-arrow">→</div>
                <div className="pipeline-step">VAE</div>
                <div className="pipeline-arrow">→</div>
                <div className="pipeline-step">GRU</div>
                <div className="pipeline-arrow">→</div>
                <div className="pipeline-step">Fusion</div>
                <div className="pipeline-arrow">→</div>
                <div className="pipeline-step">Anomaly Score</div>
              </div>
            </div>
          </section>
            </>
          )}
        </main>
      )}
    </div>
  )
}

export default App
