import React, { useContext, useState, useEffect } from "react";
import { App, Layout, theme } from "antd";
import { useLocation, Routes, Route, Navigate } from "react-router-dom";
import {
  AppstoreOutlined,
  SettingOutlined,
  ScanOutlined,
  BarChartOutlined,
  NodeIndexOutlined,
} from "@ant-design/icons";
import BaseDashboardView from "./Dashboard/BaseDashboardView";
import BaseInferenceView from "./Inference/BaseInferenceView";
import BaseSettingsView from "./Settings/BaseSettingsView";
import LoadingOverlay from "./components/LoadingOverlay";
import { DeviceContext } from "../api/DeviceContext";
import CustomHeader from "./components/Header";
import StatusBar from "./components/StatusBar";
import BaseBenchmarkView from "./Benchmark/BaseBenchmarkView";
import BaseRegionView from "./Region/BaseRegionView";
import Footer from "./components/Footer";
import useIsMobile from "../useIsMobile";

const { Content } = Layout;

const BaseView = ({ children }) => {
  const { loading, fetchConfig, fetchHealth } = useContext(DeviceContext);
  const [activeNavKey, setActiveNavKey] = useState("dashboard");
  const location = useLocation();
  const isMobile = useIsMobile();
  const iconColor = isMobile ? "#282c34" : "white";

  const navigationConfig = [
    {
      key: "dashboard",
      title: "Dashboard",
      path: "/",
      element: <BaseDashboardView />,
      icon: <AppstoreOutlined style={{ fontSize: 20, color: iconColor }} />,
    },
    {
      key: "inference",
      title: "Inferenz",
      path: "/inference",
      element: <BaseInferenceView />,
      icon: <ScanOutlined style={{ fontSize: 20, color: iconColor }} />,
    },
    {
      key: "roi",
      title: "Regionen",
      path: "/roi",
      element: <BaseRegionView />,
      icon: <NodeIndexOutlined style={{ fontSize: 20, color: iconColor }} />,
    },
    {
      key: "benchmarks",
      title: "Benchmarks",
      path: "/benchmarks",
      element: <BaseBenchmarkView />,
      icon: <BarChartOutlined style={{ fontSize: 20, color: iconColor }} />,
    },
    {
      key: "settings",
      title: "Einstellungen",
      path: "/settings",
      element: <BaseSettingsView />,
      icon: <SettingOutlined style={{ fontSize: 20, color: iconColor }} />,
    },
  ];

  useEffect(() => {
    const intervalId = setInterval(async () => {
      await fetchHealth();
    }, 3000);

    return () => clearInterval(intervalId);
  }, []);

  const handleNavChange = (e) => {
    setActiveNavKey(e.key);
  };

  useEffect(() => {
    const path = location.pathname.split("/")[1] || "dashboard";
    setActiveNavKey(
      navigationConfig.find((item) => item.path.split("/")[1] === path)?.key ||
        "dashboard"
    );
  }, [location.pathname]);

  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  useEffect(() => {
    const fetchDataFromContext = async () => {
      await fetchConfig();
    };
    fetchDataFromContext();
  }, [fetchConfig]);

  return (
    <>
      <Layout style={{ height: "100vh", overflow: "hidden" }}>
        <CustomHeader
          activeNavKey={activeNavKey}
          onNavChange={handleNavChange}
          navigationConfig={navigationConfig}
        />

        <StatusBar />

        <Layout
          style={{
            height: "calc(100vh - 64px - 70px - 40px)",
            overflow: "hidden",
          }}
        >
          <Content
            style={{
              overflowY: "auto",
              backgroundColor: colorBgContainer,
              borderRadius: borderRadiusLG,
            }}
          >
            {loading && <LoadingOverlay />}
            <Routes>
              {navigationConfig.map((navItem) => (
                <Route
                  key={navItem.key}
                  path={navItem.path + "/*"}
                  element={navItem.element}
                />
              ))}
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
            {children}
          </Content>
        </Layout>
        <Footer />
      </Layout>
    </>
  );
};

export default BaseView;
