import React, { useState } from "react";
import { Tabs } from "antd";

const ConfigTab = ({ initialItems }) => {
  const [activeKey, setActiveKey] = useState(initialItems[0].key);

  const onChange = (newActiveKey) => {
    setActiveKey(newActiveKey);
  };

  return (
    <Tabs
      type="card"
      onChange={onChange}
      activeKey={activeKey}
      items={initialItems}
    />
  );
};

export default ConfigTab;
