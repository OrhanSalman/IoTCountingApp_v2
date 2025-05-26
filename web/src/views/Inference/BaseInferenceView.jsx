import React from "react";
import { Row, Col, Divider } from "antd";
import GenericBaseViewSinglePage from "../../constants/GenericBaseViewSinglePage";
import ConfigView from "./pages/ConfigView";
import SimulationView from "./pages/SimulationView";

import { Outlet } from "react-router-dom";

const BaseInferenceView = () => {
  const configComponents = {
    1: ConfigView,
  };

  const simulationComponents = {
    1: SimulationView,
  };

  return (
    <>
      <div style={{ padding: "8px" }}>
        <Row gutter={16}>
          <Col
            span={17}
            style={{
              boxShadow: "0 0 14px rgba(0, 0, 0, 0.1)",
            }}
          >
            <GenericBaseViewSinglePage components={simulationComponents} />
          </Col>
          <Col
            span={7}
            style={{
              height: "calc(100vh - 116px)",
            }}
          >
            <GenericBaseViewSinglePage components={configComponents} />
          </Col>
        </Row>
        <Outlet />
      </div>
    </>
  );
};

export default BaseInferenceView;
