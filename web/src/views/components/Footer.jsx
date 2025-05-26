import React, { useContext, useState, useEffect } from "react";
import { Layout, Spin, Progress } from "antd";
import { DeviceContext } from "../../api/DeviceContext";

const { Footer } = Layout;

/* * Footer for interactive feedback for video simulations
 * * Displays progress of video simulation and estimated time remaining
 * / Displays conversion status
 * */

const CustomFooter = () => {
  const { health } = useContext(DeviceContext);
  const [progress, setProgress] = useState(0);
  const [remainingTime, setRemainingTime] = useState("");
  const [isCompleted, setIsCompleted] = useState(false);
  const [isConverting, setIsConverting] = useState(false);

  useEffect(() => {
    if (!health) return;

    // Video-Converter Status prüfen
    setIsConverting(health.video_converter === true);
    if (health.video_converter === true) return;

    if (!health.inference) return;

    const framesProcessed = health.inference.details?.frames_processed || 0;
    const totalFramesToProcess =
      health.inference.simulation_frames_to_process || 1;
    const currentAvgFps = health.inference.details?.avg_fps || 1;

    // Fortschrittsberechnung
    if (totalFramesToProcess > 0) {
      const calculatedProgress = Math.min(
        (framesProcessed / totalFramesToProcess) * 100,
        100
      );
      setProgress(calculatedProgress);
      setIsCompleted(calculatedProgress >= 100);

      // Verbleibende Zeit berechnen
      if (calculatedProgress < 100) {
        const remainingFrames = totalFramesToProcess - framesProcessed;
        const estimatedSecondsRemaining = remainingFrames / currentAvgFps;

        // Zeit formatieren
        if (estimatedSecondsRemaining > 60) {
          const minutes = Math.floor(estimatedSecondsRemaining / 60);
          const seconds = Math.round(estimatedSecondsRemaining % 60);
          setRemainingTime(`${minutes}m ${seconds}s`);
        } else {
          setRemainingTime(`${Math.round(estimatedSecondsRemaining)}s`);
        }
      }
    }
  }, [health]);

  const footerStyle = {
    textAlign: "center",
    backgroundColor: "#001529",
    color: "white",
    position: "sticky",
    bottom: 0,
    padding: "8px 20px",
    height: "32px",
    display: "flex",
    alignItems: "center",
    overflow: "hidden",
  };

  return (
    <Footer style={footerStyle}>
      <div
        style={{
          width: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        {isConverting ? (
          <div style={{ display: "flex", justifyContent: "center" }}>
            <Spin size="small" style={{ marginRight: "10px" }} />
            <span>Wird konvertiert...</span>
          </div>
        ) : isCompleted && health?.inference?.simulation ? (
          <div style={{ display: "flex", justifyContent: "center" }}>
            <Spin size="small" style={{ marginRight: "10px" }} />
            <span>Verarbeite...</span>
          </div>
        ) : health?.inference?.simulation ? (
          <div style={{ display: "flex", alignItems: "center" }}>
            <div style={{ marginRight: "10px", whiteSpace: "nowrap" }}>
              Simulationsfortschritt:
            </div>
            <Progress
              percent={progress}
              status="active"
              strokeColor={{ from: "#108ee9", to: "#87d068" }}
              style={{ flex: 1 }}
              format={() => (
                <span style={{ color: "white" }}>
                  {remainingTime || "Berechne..."}
                </span>
              )}
            />
          </div>
        ) : (
          <div>&nbsp;</div>
        )}
      </div>
    </Footer>
  );
};

export default CustomFooter;
