import React from "react";
import { Modal, Button, Tooltip } from "antd";
import { SaveOutlined } from "@ant-design/icons";
import runCommand from "../../../api/runCommand";

/**
 * Component to handle the save action
 *
 * @param {Object} props - Component props
 * @param {boolean} props.isModified - Flag if the data is modified
 * @param {Function} props.updateData - Function to update the data
 * @param {Object} props.health - Health status of the device
 */
const SaveButton = ({ isModified, updateData, health }) => {
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

  return (
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
      />
    </Tooltip>
  );
};

export default SaveButton;
