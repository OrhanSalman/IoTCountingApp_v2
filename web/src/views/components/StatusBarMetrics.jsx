import React, { useContext, useState, useEffect } from "react";
import { Tooltip, Divider, Tag, Alert } from "antd";
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  ArrowsAltOutlined,
} from "@ant-design/icons";
import { DeviceContext } from "../../api/DeviceContext";

/*
 * Metrics component to display CPU, RAM, GPU, and FPS metrics
 * Is used in the StatusBar component and is displayed in the left corner of the StatusBar
 */

const Metrics = () => {
  const { health, data } = useContext(DeviceContext);

  // Metrics data
  const cpu_percent = Math.round(health?.cpu?.percent || 0);
  const ram_total = Math.round(health?.ram?.total || 0);
  const ram_used = Math.round(health?.ram?.used || 0);
  const ramUsedPercent = Math.round((ram_used / ram_total) * 100);
  const gpu_percent = Math.round(
    health?.gpu && health.gpu.length > 0 ? health.gpu[0]?.load || 0 : 0
  );
  const vram_total = Math.round(
    health?.gpu && health.gpu.length > 0 ? health.gpu[0]?.memory_total || 0 : 0
  );
  const vram_used = Math.round(
    health?.gpu && health.gpu.length > 0 ? health.gpu[0]?.memory_used || 0 : 0
  );
  const vramUsedPercent = Math.round((vram_used / vram_total) * 100);

  // FPS metrics
  const avg_fps = health?.inference?.details?.avg_fps || 0;
  const avg_fps_model = health?.inference?.details?.avg_fps_model || 0;
  const real_time = health?.inference?.real_time || 0;
  const config_fps =
    data?.deviceConfigs?.length > 0 ? data.deviceConfigs[0]?.stream_fps : 0;
  const cam_fps = health?.camera?.details?.fps || 0;

  const [prevAvgFps, setPrevAvgFps] = useState(null);
  const [prevAvgModelFps, setPrevAvgModelFps] = useState(null);
  const [fpsChange, setFpsChange] = useState("equal");
  const [modelFpsChange, setModelFpsChange] = useState("equal");

  useEffect(() => {
    if (!health?.inference?.status) {
      setFpsChange("equal");
      setModelFpsChange("equal");
      return;
    }

    const currentAvgFps = avg_fps;
    const currentAvgModelFps = avg_fps_model;

    // FPS-Änderungen
    if (prevAvgFps !== null && currentAvgFps !== undefined) {
      if (currentAvgFps - prevAvgFps > 0.25) {
        setFpsChange("up");
      } else if (prevAvgFps - currentAvgFps > 0.25) {
        setFpsChange("down");
      } else {
        setFpsChange("equal");
      }
    }

    // Model FPS-Änderungen
    if (prevAvgModelFps !== null && currentAvgModelFps !== undefined) {
      if (currentAvgModelFps - prevAvgModelFps > 0.25) {
        setModelFpsChange("up");
      } else if (prevAvgModelFps - currentAvgModelFps > 0.25) {
        setModelFpsChange("down");
      } else {
        setModelFpsChange("equal");
      }
    }

    setPrevAvgFps(currentAvgFps);
    setPrevAvgModelFps(currentAvgModelFps);
  }, [health, avg_fps, avg_fps_model, health?.inference?.status]);

  const getChangeIcon = (change) => {
    if (change === "up")
      return <ArrowUpOutlined style={{ fontSize: "14px" }} />;
    if (change === "down")
      return <ArrowDownOutlined style={{ fontSize: "14px" }} />;
    return <ArrowsAltOutlined style={{ fontSize: "14px" }} />;
  };

  let fpsAlertMessage = "";
  let fpsAlertDescription = "";
  let fpsAlertType = "default";

  if (health?.inference?.status) {
    if (real_time === 2) {
      fpsAlertMessage = "Echtzeit";
      fpsAlertDescription = `Die ausgewählte Konfiguration erfüllt die Echtzeitanforderung mit einer Ziel-FPS von ${cam_fps}.`;
      fpsAlertType = "success";
    } else if (real_time === 1) {
      fpsAlertMessage = "Warnung";
      fpsAlertDescription = `Die ausgewählte Konfiguration erfüllt die Ziel-FPS von ${cam_fps} nicht vollständig.`;
      fpsAlertType = "warning";
    } else if (real_time === 0) {
      fpsAlertMessage = "Achtung";
      fpsAlertDescription = `Die ausgewählte Konfiguration ist für die Echtzeitverarbeitung von ${cam_fps} FPS nicht geeignet.`;
      fpsAlertType = "error";
    }
  }

  let modelAlertMessage = "";
  let modelAlertDescription = "";
  let modelAlertType = "default";

  if (health?.inference?.status) {
    if (real_time === 2 && avg_fps_model > avg_fps * 1.25) {
      modelAlertMessage = "Empfehlung";
      modelAlertType = "success";
      modelAlertDescription =
        "Die Inferenzleistung liegt in einem sehr guten Rahmen. Es empfiehlt sich, die Parameter zu erhöhen.";
    } else if (avg_fps_model < config_fps) {
      modelAlertMessage = "Empfehlung";
      modelAlertType = "warning";
      modelAlertDescription =
        "Die Inferenzleistung liegt unterhalb der Zielfps. Es empfiehlt sich, die Parameter zu verringern.";
    } else {
      modelAlertType = "default";
    }
  }

  const labelStyle = {
    fontSize: "11px",
    fontWeight: "bold",
    marginRight: "4px",
  };

  const valueStyle = {
    fontSize: "12px",
    fontWeight: "bold",
    minWidth: "28px",
    display: "inline-block",
  };

  const metricContainerStyle = {
    display: "flex",
    alignItems: "center",
    marginRight: "15px",
  };

  const tooltipContent = (title, message, description, type) => (
    <div style={{ maxWidth: "350px" }}>
      {message && description && (
        <Alert
          message={message}
          description={description}
          type={type}
          showIcon
          style={{ marginTop: "8px" }}
        />
      )}
    </div>
  );

  return (
    <div style={{ display: "flex", alignItems: "center" }}>
      {/* CPU */}
      <div style={metricContainerStyle}>
        <Tooltip title="CPU Auslastung">
          <span style={labelStyle}>CPU:</span>
          <span style={valueStyle}>{cpu_percent}%</span>
        </Tooltip>
      </div>

      {/* RAM */}
      <div style={metricContainerStyle}>
        <Tooltip title={`RAM: ${ram_used}/${ram_total} MB`}>
          <span style={labelStyle}>RAM:</span>
          <span style={valueStyle}>{ramUsedPercent}%</span>
        </Tooltip>
      </div>

      {/* GPU metrics if available */}
      {health?.gpu && health.gpu.length > 0 && (
        <>
          <div style={metricContainerStyle}>
            <Tooltip title="GPU Auslastung">
              <span style={labelStyle}>GPU:</span>
              <span style={valueStyle}>{gpu_percent}%</span>
            </Tooltip>
          </div>

          <div style={metricContainerStyle}>
            <Tooltip title={`VRAM: ${vram_used}/${vram_total} MB`}>
              <span style={labelStyle}>VRAM:</span>
              <span style={valueStyle}>{vramUsedPercent}%</span>
            </Tooltip>
          </div>
        </>
      )}

      <>
        <Divider type="vertical" style={{ height: "20px", margin: "0 10px" }} />

        <div style={metricContainerStyle}>
          {health?.inference?.status ? (
            <Tooltip
              color="white"
              overlayInnerStyle={{ padding: 0 }}
              title={tooltipContent(
                "Durchschnittliche FPS",
                fpsAlertMessage,
                fpsAlertDescription,
                fpsAlertType
              )}
            >
              <Tag
                icon={getChangeIcon(fpsChange)}
                color={fpsAlertType !== "default" ? fpsAlertType : undefined}
                style={{
                  padding: "1px 8px",
                  fontSize: "12px",
                  fontWeight: "bold",
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  width: "90px",
                  justifyContent: "center",
                }}
              >
                FPS: {Math.round(avg_fps)}
              </Tag>
            </Tooltip>
          ) : (
            <Tag
              icon={getChangeIcon(fpsChange)}
              style={{
                padding: "1px 8px",
                fontSize: "12px",
                fontWeight: "bold",
                display: "flex",
                alignItems: "center",
                gap: "4px",
                width: "90px",
                justifyContent: "center",
              }}
            >
              FPS: {Math.round(avg_fps)}
            </Tag>
          )}
        </div>

        <div style={metricContainerStyle}>
          {health?.inference?.status && modelAlertType !== "default" ? (
            <Tooltip
              color="white"
              overlayInnerStyle={{ padding: 0 }}
              title={tooltipContent(
                "Modell FPS",
                modelAlertMessage,
                modelAlertDescription,
                modelAlertType
              )}
            >
              <Tag
                icon={getChangeIcon(modelFpsChange)}
                color={
                  modelAlertType !== "default" ? modelAlertType : undefined
                }
                style={{
                  padding: "1px 8px",
                  fontSize: "12px",
                  fontWeight: "bold",
                  display: "flex",
                  alignItems: "center",
                  gap: "4px",
                  width: "90px",
                  justifyContent: "center",
                }}
              >
                MFPS: {Math.round(avg_fps_model)}
              </Tag>
            </Tooltip>
          ) : (
            <Tag
              icon={getChangeIcon(modelFpsChange)}
              style={{
                padding: "1px 8px",
                fontSize: "12px",
                fontWeight: "bold",
                display: "flex",
                alignItems: "center",
                gap: "4px",
                width: "90px",
                justifyContent: "center",
              }}
            >
              MFPS: {Math.round(avg_fps_model)}
            </Tag>
          )}
        </div>
      </>
    </div>
  );
};

export default Metrics;
