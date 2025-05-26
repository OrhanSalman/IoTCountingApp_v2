import React from "react";
import GenericBaseView from "../../constants/GenericBaseView";
import MQTTSettingsView from "./pages/MQTTSettingsView";
import SystemInfoView from "./pages/SystemInfoView";
import ConfigSettingsView from "./pages/ConfigSettingsView";
import {
  LinkOutlined,
  ApiOutlined,
  InfoCircleOutlined,
  SettingOutlined,
} from "@ant-design/icons";
import { Outlet } from "react-router-dom";

const BaseSettingsView = () => {
  const menuItems = [
    {
      key: "1",
      label: "MQTT",
      icon: <LinkOutlined />,
      path: "/settings/mqtt",
    },
    {
      key: "2",
      label: "Konfiguration",
      icon: <SettingOutlined />,
      path: "/settings/config",
    },
    {
      key: "3",
      label: "System",
      icon: <InfoCircleOutlined />,
      path: "/settings/system",
    },
  ];

  const contentComponents = {
    1: MQTTSettingsView,
    2: ConfigSettingsView,
    3: SystemInfoView,
  };

  return (
    <>
      <GenericBaseView
        menuItems={menuItems}
        defaultKey="1"
        contentComponents={contentComponents}
      />
      <Outlet />
    </>
  );
};

export default BaseSettingsView;
