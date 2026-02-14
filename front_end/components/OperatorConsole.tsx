"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Header } from "@/components/Header";

type RobotFailureType = "none" | "stuck" | "drop" | "grasp_failed";
type RobotStatus = "ROBOT_ACTIVE" | "WAITING_FOR_HELP";
type ModalStep = "ALERT" | "PAYMENT_REQUIRED" | "PAYMENT_ACCEPTED" | null;

type LogType = "info" | "success" | "error";
type LogLine = { ts: string; msg: string; type: LogType };

function nowTs() {
  return new Date().toLocaleTimeString("en-US", { hour12: false });
}

export function OperatorConsole() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [robotId] = useState("01");
  const [status, setStatus] = useState<RobotStatus>("ROBOT_ACTIVE");
  const [failureType, setFailureType] = useState<RobotFailureType>("none");
  const [risk, setRisk] = useState<number>(0.02);
  const [lastUpdate, setLastUpdate] = useState<string>(() => nowTs());

  const [modal, setModal] = useState<ModalStep>(null);
  const [controlsUnlocked, setControlsUnlocked] = useState(false);
  const [isSigning, setIsSigning] = useState(false);

  const bountyUsdc = 0.5;
  const [myTasksSolved, setMyTasksSolved] = useState(1);
  const [myEarnedUsdc, setMyEarnedUsdc] = useState(0.5);
  const [platformRobotsRescued, setPlatformRobotsRescued] = useState(8492);
  const [platformPaidUsdc, setPlatformPaidUsdc] = useState(42100);

  const [logs, setLogs] = useState<LogLine[]>(() => [
    { ts: nowTs(), msg: "System ready. Waiting for telemetry...", type: "info" },
  ]);

  const activeRobotName = useMemo(() => `Robot #${robotId}`, [robotId]);

  function pushLog(msg: string, type: LogType = "info") {
    setLogs((prev) => [{ ts: nowTs(), msg, type }, ...prev].slice(0, 200));
  }

  function transitionToActive() {
    setStatus("ROBOT_ACTIVE");
    setFailureType("none");
    setRisk(0.02);
    setLastUpdate(nowTs());
    setModal(null);
    setControlsUnlocked(false);
    setIsSigning(false);
    pushLog(`Robot #${robotId} state: ROBOT_ACTIVE`, "success");
  }

  function transitionToWaitingForHelp(nextFailure: RobotFailureType, nextRisk: number) {
    setStatus("WAITING_FOR_HELP");
    setFailureType(nextFailure);
    setRisk(nextRisk);
    setLastUpdate(nowTs());
    setModal("ALERT");
    setControlsUnlocked(false);
    setIsSigning(false);
    pushLog(`ALERT: Robot #${robotId} ${nextFailure} (risk: ${nextRisk})`, "error");
  }

  useEffect(() => {
    const t = window.setTimeout(() => {
      transitionToWaitingForHelp("stuck", 0.8);
    }, 3000);
    return () => window.clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const el = videoRef.current;
    if (!el) return;

    if (status === "WAITING_FOR_HELP") {
      el.pause();
      return;
    }

    const p = el.play();
    if (p && typeof (p as Promise<void>).catch === "function") {
      (p as Promise<void>).catch(() => {});
    }
  }, [status]);

  function onHelpRobot() {
    setModal("PAYMENT_REQUIRED");
    setLastUpdate(nowTs());
    pushLog("X402: 402 Payment Required", "info");
  }

  function onSign() {
    if (isSigning) return;
    setIsSigning(true);
    pushLog("Wallet: signature requested", "info");
    window.setTimeout(() => {
      setIsSigning(false);
      setModal("PAYMENT_ACCEPTED");
      setControlsUnlocked(true);
      setLastUpdate(nowTs());
      setMyEarnedUsdc((v) => +(v + bountyUsdc).toFixed(2));
      setPlatformPaidUsdc((v) => +(v + bountyUsdc).toFixed(2));
      pushLog("Payment Accepted", "success");
    }, 1200);
  }

  function onClosePaymentAccepted() {
    setModal(null);
    setLastUpdate(nowTs());
    pushLog("Control authority unlocked", "success");
  }

  function onResetRobot() {
    pushLog("POST /assist/reset", "info");
    window.setTimeout(() => {
      if (controlsUnlocked) {
        setMyTasksSolved((v) => v + 1);
        setPlatformRobotsRescued((v) => v + 1);
      }
      transitionToActive();
    }, 800);
  }

  function renderStatusLabel(s: RobotStatus) {
    return s === "ROBOT_ACTIVE" ? "Robot Active" : "WAITING FOR HELP";
  }

  return (
    <div className="rb-console">
      <div className="glow-bg" />

      <div style={{ display: "none" }}>
        <svg xmlns="http://www.w3.org/2000/svg" id="icon-sprite">
          <symbol
            id="icon-wallet-v2"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <rect x="2" y="5" width="20" height="14" rx="2" stroke="url(#grad-icon)" />
            <path d="M2 10h20" />
            <path d="M6 15h2" />
            <path d="M16 15h2" />
            <defs>
              <linearGradient id="grad-icon" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stopColor="#6366f1" />
                <stop offset="100%" stopColor="#a853ba" />
              </linearGradient>
            </defs>
          </symbol>

          <symbol id="icon-alert-v2" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="#ef4444" strokeWidth="1.5" />
            <circle cx="12" cy="12" r="3" fill="#ef4444">
              <animate attributeName="opacity" values="1;0.2;1" dur="1s" repeatCount="indefinite" />
            </circle>
          </symbol>

          <symbol
            id="icon-success-v2"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#10b981"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M2 12l5 5L17 7" />
            <path d="M12 17l2 2L24 9" />
          </symbol>

          <symbol
            id="icon-sign-v2"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 19l7-7 3 3-7 7-3-3z" />
            <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z" />
            <path d="M2 2l7.586 7.586" />
            <circle cx="11" cy="11" r="2" />
          </symbol>

          <symbol
            id="icon-reset-v2"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
            <path d="M3 3v5h5" />
          </symbol>
        </svg>
      </div>

      <div className="app-container">
        <Header />

        <div className="col-fleet">
          <div
            className="card"
            style={{
              flex: 1,
              padding: 12,
              display: "flex",
              flexDirection: "column",
              gap: 8,
            }}
          >
            <div
              style={{
                padding: "0 8px 8px 8px",
                fontSize: 11,
                textTransform: "uppercase",
                color: "var(--color-text-muted)",
                fontWeight: 600,
                borderBottom: "1px solid rgba(255,255,255,0.05)",
              }}
            >
              Active Units (3)
            </div>

            <div className="fleet-item active">
              <div className="robot-avatar">#{robotId}</div>
              <div className="fleet-info">
                <div className="robot-name">{activeRobotName}</div>
                <div className="robot-status">
                  <div className={`dot ${status === "ROBOT_ACTIVE" ? "green" : "red"}`} />
                  <span>{status === "ROBOT_ACTIVE" ? "Operational" : "Intervention Req."}</span>
                </div>
              </div>
            </div>

            <div className="fleet-item">
              <div className="robot-avatar">#02</div>
              <div className="fleet-info">
                <div className="robot-name">Robot #02</div>
                <div className="robot-status">
                  <div className="dot gray" />
                  <span>Idle / Charging</span>
                </div>
              </div>
            </div>

            <div className="fleet-item">
              <div className="robot-avatar">#03</div>
              <div className="fleet-info">
                <div className="robot-name">Robot #03</div>
                <div className="robot-status">
                  <div className="dot gray" />
                  <span>Idle / Standby</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <main className="col-center">
          <div className={`card status-banner ${status === "WAITING_FOR_HELP" ? "alert" : ""}`}>
            <div className="status-group">
              <span className="status-label">Robot ID</span>
              <span className="status-value">ROBOT #{robotId}</span>
            </div>
            <div className="status-group">
              <span className="status-label">Current Status</span>
              <span className="status-value" style={{ color: status === "ROBOT_ACTIVE" ? "#10b981" : "#ef4444" }}>
                <div className={`dot ${status === "ROBOT_ACTIVE" ? "green" : "red"}`} />
                {renderStatusLabel(status)}
              </span>
            </div>
            <div className="status-group">
              <span className="status-label">Error Type</span>
              <span
                className="status-value"
                style={{
                  color: status === "ROBOT_ACTIVE" ? "var(--color-text-muted)" : "#ef4444",
                  fontSize: 14,
                }}
              >
                {failureType}
              </span>
            </div>
            <div className="status-group">
              <span className="status-label">Risk Score</span>
              <span className="status-value" style={{ color: status === "ROBOT_ACTIVE" ? "#10b981" : "#ef4444" }}>
                {risk.toFixed(2)}
              </span>
            </div>
            <div className="status-group">
              <span className="status-label">Last Update</span>
              <span className="status-value" style={{ fontSize: 12, color: "var(--color-text-muted)" }}>
                {lastUpdate}
              </span>
            </div>
          </div>

          <div className="card video-card">
            <div className="video-wrapper">
              <video ref={videoRef} autoPlay muted loop playsInline>
                <source src="/assets/52aff143030c7066a01470f13fe12a54.mp4" type="video/mp4" />
              </video>

              <div className="overlay-ui">
                <div className="tag live">CAM_01</div>
                <div className="tag">24ms Latency</div>
              </div>

              <div className={`glass-modal ${modal === "ALERT" ? "visible" : ""}`}>
                <div className="modal-header">
                  <div className="icon-box alert">
                    <svg className="icon-lg">
                      <use href="#icon-alert-v2" />
                    </svg>
                  </div>
                  <div>
                    <div className="modal-title">Robot Needs Help</div>
                    <div className="modal-desc">
                      Robot #{robotId} is {failureType} (risk: {risk})
                    </div>
                  </div>
                </div>
                <div className="price-display">
                  <span className="modal-desc">Bounty</span>
                  <span className="price-val" style={{ color: "#10b981" }}>
                    {bountyUsdc.toFixed(2)} USDC
                  </span>
                </div>
                <button className="btn-premium btn-primary" onClick={onHelpRobot}>
                  Help Robot
                </button>
              </div>

              <div className={`glass-modal ${modal === "PAYMENT_REQUIRED" ? "visible" : ""}`}>
                <div className="modal-header">
                  <div className="icon-box">
                    <svg className="icon-lg">
                      <use href="#icon-sign-v2" />
                    </svg>
                  </div>
                  <div>
                    <div className="modal-title">Sign Request</div>
                    <div className="modal-desc">This is a signature request, not a token transfer.</div>
                  </div>
                </div>

                <div
                  style={{
                    background: "rgba(0,0,0,0.4)",
                    padding: 12,
                    borderRadius: 8,
                    fontFamily: "var(--font-mono)",
                    fontSize: 11,
                    color: "var(--color-text-muted)",
                    border: "1px dashed rgba(255,255,255,0.1)",
                    marginBottom: 16,
                  }}
                >
                  <div style={{ marginBottom: 6, color: "#fff" }}>Sign Message:</div>
                  &quot;I agree to pay 0.5 USDC to help Robot #{robotId}&quot;
                </div>

                <button className="btn-premium btn-primary" onClick={onSign} disabled={isSigning}>
                  {isSigning ? "Signing..." : `Sign & Pay ${bountyUsdc.toFixed(2)} USDC`}
                </button>
              </div>

              <div className={`glass-modal ${modal === "PAYMENT_ACCEPTED" ? "visible" : ""}`}>
                <div className="modal-header">
                  <div className="icon-box success">
                    <svg className="icon-lg">
                      <use href="#icon-success-v2" />
                    </svg>
                  </div>
                  <div>
                    <div className="modal-title">Payment Accepted</div>
                    <div className="modal-desc">Control authority transferred.</div>
                  </div>
                </div>
                <button className="btn-premium btn-primary" onClick={onClosePaymentAccepted}>
                  Launch Controls
                </button>
              </div>
            </div>

            <div className="controls-deck">
              <button
                className={`btn-premium ${!controlsUnlocked ? "btn-ghost" : "btn-primary"} w-[200px]`}
                onClick={onResetRobot}
                disabled={!controlsUnlocked}
              >
                <svg className="icon-svg">
                  <use href="#icon-reset-v2" />
                </svg>
                Reset Robot
              </button>
              <button
                className="btn-premium btn-ghost"
                style={{ flex: "0 0 40px", opacity: 0.2 }}
                onClick={() => transitionToWaitingForHelp("grasp_failed", 0.8)}
                aria-label="Trigger demo error"
              >
                !
              </button>
            </div>
          </div>
        </main>

        <aside className="col-data">
          <div className="card">
            <div className="metrics-card-body">
              <div className="metrics-section">
                <div className="metrics-header">My Contributions</div>
                <div className="stat-grid-2x2">
                  <div className="stat-block">
                    <span className="stat-label">Tasks Solved</span>
                    <span className="stat-value-lg">{myTasksSolved}</span>
                  </div>
                  <div className="stat-block">
                    <span className="stat-label">Earned</span>
                    <span className="stat-value-lg stat-value-highlight">
                      {myEarnedUsdc.toFixed(2)}
                      <span className="stat-unit">USDC</span>
                    </span>
                  </div>
                </div>
              </div>

              <div className="metrics-section">
                <div className="metrics-header">Platform Metrics</div>
                <div className="stat-grid-2x2">
                  <div className="stat-block">
                    <span className="stat-label">Total Robots </span>
                    <span className="stat-label">Rescued</span>
                    <span className="stat-value-lg">{platformRobotsRescued.toLocaleString()}</span>
                  </div>
                  <div className="stat-block">
                    <span className="stat-label">Total Paid </span>
                    <span className="stat-label">(USDC)</span>
                    <span className="stat-value-lg">
                      {(platformPaidUsdc / 1000).toFixed(1)}
                      <span className="stat-unit">kUSDC</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="card" style={{ flex: 1, display: "flex", flexDirection: "column" }}>
            <div
              style={{
                padding: 12,
                borderBottom: "1px solid rgba(255,255,255,0.05)",
                fontSize: 11,
                textTransform: "uppercase",
                color: "var(--color-text-muted)",
                fontWeight: 600,
              }}
            >
              System Logs
            </div>
            <div className="console-output">
              {logs.map((l, idx) => (
                <div className="log-line" key={`${l.ts}-${idx}`}>
                  <span className="log-ts">{l.ts}</span>
                  <span className={`log-msg ${l.type}`}>{l.msg}</span>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
