import React, { useContext, useState } from "react";
import { Button, Tooltip, Divider } from "antd";
import {
  PlayCircleOutlined,
  CameraOutlined,
  AppstoreAddOutlined,
  DashboardOutlined,
  LinkOutlined,
} from "@ant-design/icons";
import { DeviceContext } from "../../api/DeviceContext";
import runCommand from "../../api/runCommand";
import useIsMobile from "../../useIsMobile";

/*
 * StatusBarControls component to control the status of the device
 * Is used in the StatusBar component and is displayed in the middler of the StatusBar
 * Controls the camera, inference, benchmark, and MQTT client
 */

const StatusBarControls = () => {
  const { health, fetchHealth } = useContext(DeviceContext);
  const isMobile = useIsMobile();

  const [loadingStates, setLoadingStates] = useState({
    camera: false,
    counting: false,
    mqtt: false,
    benchmark: false,
    exporter: false,
  });

  const handleButtonClick = async (key, command) => {
    setLoadingStates((prevState) => ({
      ...prevState,
      [key]: true,
    }));

    try {
      await runCommand(command, key);
    } finally {
      setLoadingStates((prevState) => ({
        ...prevState,
        [key]: false,
      }));
      await fetchHealth();
    }
  };

  return (
    <>
      <Divider solid type="vertical" />
      <Tooltip
        title={
          health?.inference?.simulation
            ? "Simulation läuft"
            : health?.inference?.status
            ? `Inferenz aktiv seit ${health?.inference?.details?.init_time}`
            : "Inferenz starten"
        }
      >
        <Button
          icon={<PlayCircleOutlined />}
          type="default"
          loading={loadingStates.counting}
          onClick={() =>
            handleButtonClick(
              "counting",
              health?.inference?.status ? "stop" : "start"
            )
          }
          disabled={health?.benchmark?.status || health?.inference?.exporter}
          style={{
            backgroundColor: health?.inference?.simulation
              ? "lightblue"
              : health?.inference?.status
              ? "blue"
              : health?.benchmark?.status
              ? "dimgray"
              : "lightgray",
            color: "white",
            fontSize: isMobile ? "12px" : "inherit",
            width: isMobile ? "32px" : "auto",
            height: isMobile ? "32px" : "auto",
          }}
          shape="circle"
        />
      </Tooltip>
      <Tooltip title="Kamera">
        <Button
          icon={<CameraOutlined />}
          type="default"
          loading={loadingStates.camera}
          disabled={health?.inference?.status || loadingStates?.counting}
          onClick={() =>
            handleButtonClick(
              "camera",
              health?.camera?.status ? "stop" : "start"
            )
          }
          style={{
            backgroundColor: health?.camera?.status ? "blue" : "lightgray",
            color: "white",
            fontSize: isMobile ? "12px" : "inherit",
            width: isMobile ? "32px" : "auto",
            height: isMobile ? "32px" : "auto",
          }}
          shape="circle"
        />
      </Tooltip>
      <Tooltip title="Exporter">
        <Button
          icon={<AppstoreAddOutlined />}
          type="default"
          loading={health?.inference?.exporter}
          disabled
          style={{
            backgroundColor: health?.inference?.exporter ? "blue" : "lightgray",
            color: "white",
            fontSize: isMobile ? "12px" : "inherit",
            width: isMobile ? "32px" : "auto",
            height: isMobile ? "32px" : "auto",
          }}
          shape="circle"
        />
      </Tooltip>
      <Tooltip title="Benchmark">
        <Button
          icon={<DashboardOutlined />}
          type="default"
          loading={loadingStates.benchmark}
          disabled={health?.inference?.status || health?.inference?.simulation}
          onClick={() =>
            handleButtonClick(
              "benchmark",
              health?.benchmark?.status ? "stop" : "start"
            )
          }
          style={{
            backgroundColor: health?.benchmark?.status
              ? "blue"
              : health?.inference?.status
              ? "dimgray"
              : health?.inference?.simulation
              ? "dimgray"
              : "lightgray",
            color: "white",
            fontSize: isMobile ? "12px" : "inherit",
            width: isMobile ? "32px" : "auto",
            height: isMobile ? "32px" : "auto",
          }}
          shape="circle"
        />
      </Tooltip>
      <Tooltip
        title={
          loadingStates?.mqtt && health?.mqtt?.connected
            ? "Verbunden"
            : !health?.mqtt?.connected && health?.mqtt?.status
            ? "MQTT Nicht verbunden"
            : "MQTT Client starten"
        }
      >
        <Button
          icon={<LinkOutlined />}
          type="default"
          loading={loadingStates?.mqtt}
          onClick={() =>
            handleButtonClick("mqtt", health?.mqtt?.status ? "stop" : "start")
          }
          style={{
            backgroundColor:
              !health?.mqtt?.connected && health?.mqtt?.status
                ? "orange"
                : health?.mqtt?.status
                ? "blue"
                : "lightgray",
            color: "white",
            fontSize: isMobile ? "12px" : "inherit",
            width: isMobile ? "32px" : "auto",
            height: isMobile ? "32px" : "auto",
          }}
          shape="circle"
        />
      </Tooltip>
      <Divider solid type="vertical" />
    </>
  );
};

export default StatusBarControls;
