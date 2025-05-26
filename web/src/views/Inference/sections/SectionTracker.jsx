import React, { useContext, useEffect, useState } from "react";
import { Row } from "antd";
import { useUpdateHandler } from "../context/updateHandler";
import CardWithSelect from "./components/CardWithSelect";

import { accelerator, tracker } from "../../../../src/constants/constants";
import { DeviceContext } from "../../../api/DeviceContext";

const SectionTracker = () => {
  const { handleUpdateTracker } = useUpdateHandler();
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
    ? accelerator // Wenn GPU verfügbar ist, dann alle Acceleratoren anzeigen
    : accelerator.filter((a) => a.value !== "gpu"); // Wenn keine GPU verfügbar ist, dann nur CPU anzeigen

  const cardItemsSelect = [
    {
      title: "Tracker",
      value: deviceConfigs[0]?.tracker,
      options: tracker,
      width: "200px",
      height: "100px",
      onChange: handleUpdateTracker,
    },
  ];

  return (
    <>
      <Row style={{ display: "flex", alignItems: "stretch" }}>
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

export default SectionTracker;
