import React, { useContext } from "react";
import { Button, Tooltip, Dropdown, Modal, message } from "antd";
import {
  DeleteOutlined,
  ReloadOutlined,
  SaveOutlined,
} from "@ant-design/icons";
import { DeviceContext } from "../../api/DeviceContext";
import { deleteData, deleteBenchmarkData } from "../../api/deleteData";
import runCommand from "../../api/runCommand";

/*
 * StatusBarActions component to control the status of the device
 * Is used in the StatusBar component and is displayed in the right of the StatusBar
 * Controls the save, reload, and delete actions
 */

const { confirm } = Modal;

const StatusBarActions = () => {
  const {
    health,
    isModified,
    loading,
    fetchConfig,
    fetchImage,
    fetchHealth,
    fetchBenchmarks,
    fetchSimulations,
    fetchSampleVideo,
    updateData,
  } = useContext(DeviceContext);

  const handleDeleteFunction = async (type) => {
    if (type === "benchmarks") {
      await deleteBenchmarkData();
      await fetchBenchmarks();
    } else {
      await deleteData(type);
      await fetchSimulations(type);
    }
  };

  const deleteOptions = [
    {
      key: "simvid",
      label: "Videosimulationen",
      onClick: () => {
        confirm({
          title: "Videosimulationen löschen",
          content: "Möchten Sie wirklich alle Videosimulationen löschen?",
          onOk: () => {
            handleDeleteFunction("simvid");
          },
        });
      },
    },
    {
      key: "benchmarks",
      label: "Benchmarks",
      onClick: () => {
        confirm({
          title: "Benchmarks löschen",
          content: "Möchten Sie wirklich alle Benchmarks löschen?",
          onOk: () => {
            handleDeleteFunction("benchmarks");
          },
        });
      },
    },
  ];

  const handleSave = async () => {
    await updateData();

    if (!health?.inference.simulation && health?.inference?.status) {
      Modal.confirm({
        title: "Zählung neu starten?",
        content:
          "Die Änderungen sind nicht auf die laufende Zählung angewandt. Ein Neustart ist erforderlich.",
        okText: "Ja",
        cancelText: "Nein",
        onOk: async () => {
          await runCommand("stop", "counting");
          await runCommand("stop", "camera");
          runCommand("start", "counting");
        },
      });
    }
  };

  const handleReloadData = async () => {
    await Promise.all([
      fetchConfig(),
      fetchImage(),
      fetchHealth(),
      fetchBenchmarks(),
      fetchSampleVideo(),
      fetchSimulations("simvid"),
    ]);
    message.info("Gerätedaten neu geladen");
  };

  return (
    <>
      <Tooltip title="Neu laden">
        <Button
          type="default"
          disabled={loading}
          onClick={handleReloadData}
          loading={loading}
          icon={<ReloadOutlined />}
          style={{ width: "36px" }}
        />
      </Tooltip>

      <Tooltip title="Speichern">
        <Button
          icon={<SaveOutlined />}
          type="primary"
          style={{
            width: "36px",
            boxShadow: isModified ? "0 4px 8px rgba(0, 0, 0, 0.2)" : "none",
          }}
          disabled={!isModified}
          onClick={handleSave}
          loading={loading}
        />
      </Tooltip>

      <Dropdown
        menu={{ items: deleteOptions }}
        trigger={["hover"]}
        placement="bottomRight"
      >
        <Button danger style={{ width: "36px" }} icon={<DeleteOutlined />} />
      </Dropdown>
    </>
  );
};

export default StatusBarActions;
