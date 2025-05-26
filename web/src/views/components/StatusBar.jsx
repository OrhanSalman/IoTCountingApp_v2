import React, { useContext } from "react";
import { Row, Col, Dropdown, Modal } from "antd";
import { MoreOutlined } from "@ant-design/icons";
import { DeviceContext } from "../../api/DeviceContext";
import runCommand from "../../api/runCommand";
import useIsMobile from "../../useIsMobile";
import StatusBarMetrics from "./StatusBarMetrics";
import StatusBarActions from "./StatusBarActions";
import StatusBarControls from "./StatusBarControls";

/**
 * * StatusBar component for the application
 * * Displays the control buttons, metrics, and actions
 * * in a sticky bar at the top of the page
 */

const { confirm } = Modal;

const StatusBar = () => {
  const { dispatch } = useContext(DeviceContext);
  const isMobile = useIsMobile();

  const moreOptions = [
    {
      key: "restart",
      label: "Neustart",
      onClick: () => {
        confirm({
          title: "Neustart",
          content:
            "Dies wird die Anwendung neustarten und ein Cleanup aller Prozesse durchführen. Fortfahren?",
          onOk: () => {
            runCommand("restart", "server");
            dispatch({ type: "FETCH_INIT" });
          },
        });
      },
    },
  ];

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: 20,
        position: "sticky",
        zIndex: 1,
        margin: 0,
        fontSize: 15,
        fontWeight: "bold",
        maxHeight: "30px",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
      }}
    >
      <Row style={{ width: "100%" }}>
        {/* Spalte 1: Links - Metriken */}
        <Col
          span={8}
          width="33%"
          style={{
            display: "flex",
            justifyContent: "flex-start",
            gap: "10px",
            alignItems: "center",
          }}
        >
          {!isMobile && <StatusBarMetrics />}
        </Col>

        {/* Spalte 2: Zentrum */}
        <Col
          span={8}
          width="33%"
          style={{
            display: "flex",
            justifyContent: isMobile ? "center" : "center",
            gap: isMobile ? "12px" : "32px",
            fontSize: isMobile ? "12px" : "inherit",
          }}
        >
          <StatusBarControls />
        </Col>

        {/* Spalte 3: Rechts */}
        <Col
          span={8}
          width="33%"
          style={{
            display: "flex",
            justifyContent: "flex-end",
            gap: "10px",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", gap: "12px" }}>
            {!isMobile && <StatusBarActions />}

            <Dropdown
              menu={{
                items: isMobile
                  ? [
                      ...moreOptions,
                      {
                        key: "actionButtons",
                        label: (
                          <div style={{ display: "flex", gap: "10px" }}>
                            <StatusBarActions />
                          </div>
                        ),
                      },
                    ]
                  : moreOptions,
              }}
              trigger={["hover"]}
              placement="bottomRight"
            >
              <MoreOutlined style={{ fontSize: "20px" }} />
            </Dropdown>
          </div>
        </Col>
      </Row>
    </div>
  );
};

export default StatusBar;
