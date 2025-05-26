import React, { useContext, useEffect, useState } from "react";
import { Row } from "antd";
import { useUpdateHandler } from "../context/updateHandler";
import CardWithSlider from "./components/CardWithSlider";
import {
  iou,
  conf,
  vid_stride,
  limit,
} from "../../../../src/constants/constants";
import { DeviceContext } from "../../../api/DeviceContext";

const SectionThresholds = () => {
  const {
    handleUpdateVidStride,

    handleUpdateIOU,
    handleUpdateConf,
    handleUpdateMaxDet,
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

  const cardItemsSlider = [
    {
      title: "IoU",
      value: deviceConfigs[0]?.iou,
      options: iou,
      //width: "300px",
      //height: "100px",
      onChange: handleUpdateIOU,
    },
    {
      title: "Vertrauensschwelle",
      value: deviceConfigs[0]?.conf,
      options: conf,
      //width: "300px",
      //height: "100px",
      onChange: handleUpdateConf,
    },
    {
      title: "Limit",
      value: deviceConfigs[0]?.max_det,
      options: limit,
      //width: "300px",
      //height: "100px",
      onChange: handleUpdateMaxDet,
    },
    {
      title: "Stride",
      value: deviceConfigs[0]?.vid_stride,
      options: vid_stride,
      //width: "300px",
      //height: "100px",
      tooltip: vid_stride.tooltip,
      onChange: handleUpdateVidStride,
    },
  ];

  return (
    <>
      <Row style={{ display: "flex", alignItems: "stretch" }}>
        {cardItemsSlider.map((item, index) => (
          <CardWithSlider
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

export default SectionThresholds;
