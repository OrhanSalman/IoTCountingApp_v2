import React, { useContext, useEffect, useState } from "react";
import { Row } from "antd";
import { useUpdateHandler } from "../context/updateHandler";
import CardWithSelect from "./components/CardWithSelect";

import {
  model,
  accelerator,
  format,
  imgsz,
  quantization,
} from "../../../../src/constants/constants";
import { DeviceContext } from "../../../api/DeviceContext";

const SectionInference = () => {
  const {
    handleUpdateModel,
    handleUpdateFormat,
    handleUpdateDeviceType,
    handleUpdateImgsz,
    handleUpdatePrecision,
  } = useUpdateHandler();
  const { data } = useContext(DeviceContext);
  const deviceConfigs = data?.deviceConfigs || [];
  const [gpuEnabled, setGpuEnabled] = useState(false);

  useEffect(() => {
    const isGpuEnabled =
      data?.cuda === true ||
      (data?.mps_available === true && data?.mps_built === true);

    setGpuEnabled(isGpuEnabled);
  }, [data]);

  const availableAccelerators = gpuEnabled
    ? accelerator
    : accelerator.filter((a) => a.value !== "gpu");

  const cardItemsSelect = [
    {
      title: "Model",
      value: deviceConfigs[0]?.model,
      options: model,
      tooltip:
        "Kleinere Modelle: schnelle Erkennung, CPU-günstig. Größere Modelle: höhere Genauigkeit, GPU-geeignet.",
      width: "140px",
      height: "100px",
      onChange: handleUpdateModel,
    },
    {
      title: "Inputgröße",
      value: deviceConfigs[0]?.imgsz,
      options: imgsz,
      tooltip:
        "256-512: schnelle Verarbeitung, nahe Objekte. 640-1280: maximale Größe, für entfernte Objekte geeignet.",
      width: "100px",
      height: "100px",
      onChange: handleUpdateImgsz,
    },

    {
      title: "Beschleuniger",
      value: deviceConfigs[0]?.deviceType,
      options: availableAccelerators,
      width: "140px",
      height: "100px",
      onChange: handleUpdateDeviceType,
    },
    {
      title: "Präzision",
      value: deviceConfigs[0]?.quantization,
      options: quantization,
      width: "100px",
      height: "100px",
      onChange: handleUpdatePrecision,
    },
    {
      title: "Format",
      value: deviceConfigs[0]?.modelFormat,
      options: format,
      width: "160px",
      height: "100px",
      onChange: handleUpdateFormat,
    },
  ];

  return (
    <>
      <Row style={{ display: "flex" }}>
        {cardItemsSelect.map((item, index) => (
          <CardWithSelect
            key={index}
            item={item}
            deviceConfigs={deviceConfigs[0]}
            width={item.width}
            height={item.height}
          />
        ))}
      </Row>
    </>
  );
};

export default SectionInference;
