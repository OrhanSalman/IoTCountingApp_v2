import React, { useContext, useEffect, useState } from "react";
import { Collapse, Button, Tabs } from "antd";
import SectionInference from "../sections/SectionInference";
import SectionThresholds from "../sections/SectionThresholds";
import SectionTracker from "../sections/SectionTracker";
import SectionVideo from "../sections/SectionVideo";

const ConfigView = () => {
  const [activeKey, setActiveKey] = useState("1");

  const onChange = (newActiveKey) => {
    setActiveKey(newActiveKey);
  };

  const items = [
    {
      key: "1",
      label: "Inferenz",
      children: <SectionInference />,
    },
    {
      key: "2",
      label: "Schwellen",
      children: <SectionThresholds />,
    },
    {
      key: "3",
      label: "Video",
      children: <SectionVideo />,
    },

    {
      key: "4",
      label: "Tracker",
      children: <SectionTracker />,
    },
  ];

  return (
    <>
      <Tabs
        type="card"
        onChange={onChange}
        activeKey={activeKey}
        items={items}
        //tabBarExtraContent={
        //  <Button type="primary" icon={<PlayCircleOutlined />}>
        //    Speichern und Simulieren
        //  </Button>
        //}
      />
    </>
  );
};

export default ConfigView;
