import React, { useState, useContext } from "react";
import {
  Layout,
  Menu,
  Button,
  Tooltip,
  Dropdown,
  Badge,
  theme,
  Modal,
} from "antd";
import { NavLink } from "react-router-dom";
import { LogoutOutlined, AppstoreOutlined } from "@ant-design/icons";
import useIsMobile from "../../useIsMobile";
import useHandleLogout from "../../api/useHandleLogout";
import { DeviceContext } from "../../api/DeviceContext";

/**
 * * Header component for the application
 * * Dashboard | Inference | Regions | Benchmarks | Settings | Logout
 */

const { Header } = Layout;
const { confirm } = Modal;
const CustomHeader = ({ activeNavKey, onNavChange, navigationConfig }) => {
  const { user } = useContext(DeviceContext);
  const logout = useHandleLogout();
  const isMobile = useIsMobile();
  const [dropdownVisible, setDropdownVisible] = useState(false);

  const {
    token: { colorTextBase },
  } = theme.useToken();

  const handleLogout = () => {
    confirm({
      title: "Logout bestätigen",
      //content: "",
      okText: "Ja",
      cancelText: "Abbrechen",
      onOk: () => {
        logout();
      },
    });
  };

  const iconMenuItems = navigationConfig.map((item) => ({
    key: item.key,
    icon: item.icon,
    title: item.title,
    path: item.path,
  }));

  const menu = (
    <Menu
      theme="dark"
      selectedKeys={[activeNavKey]}
      onClick={(e) => {
        onNavChange(e);
        setDropdownVisible(false);
      }}
      items={iconMenuItems.map((item) => ({
        key: item.key,
        icon: item.icon,
        label: (
          <NavLink
            to={item.path}
            style={({ isActive }) => ({
              color: isActive ? colorTextBase : colorTextBase,
              padding: "5px",
              display: "block",
            })}
          >
            {item.title}
          </NavLink>
        ),
      }))}
    />
  );

  return (
    <Header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 1,
        width: "100%",
        height: "48px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        backgroundColor: "#001529",
      }}
    >
      {/* Linker Bereich */}
      <div style={{ flex: 1, textAlign: "left" }}>
        {isMobile && (
          <Dropdown
            overlay={menu}
            onOpenChange={setDropdownVisible}
            open={dropdownVisible}
            trigger={["click"]}
          >
            <Button type="text" style={{ color: "white" }}>
              <AppstoreOutlined style={{ fontSize: 20 }} />
            </Button>
          </Dropdown>
        )}
      </div>

      {/* Mittlerer Bereich */}
      <div style={{ flex: 3, textAlign: "center" }}>
        {!isMobile && (
          <Menu
            theme="dark"
            mode="horizontal"
            selectedKeys={[activeNavKey]}
            onClick={onNavChange}
            style={{
              width: "100%",
              lineHeight: "40px",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              backgroundColor: "transparent",
            }}
            items={iconMenuItems.map((item) => ({
              key: item.key,
              icon: item.icon,
              label: (
                <NavLink
                  to={item.path}
                  style={({ isActive }) => ({
                    color: isActive ? "white" : "white",
                    padding: "5px",
                  })}
                >
                  {item.title}
                  {item?.badge && (
                    <Badge size="small" count={5} offset={[5, -15]} />
                  )}
                </NavLink>
              ),
            }))}
          />
        )}
      </div>

      {/* Rechter Bereich */}
      <div
        style={{
          flex: 1,
          display: "flex",
          justifyContent: "flex-end",
          alignItems: "center",
          gap: "8px",
        }}
      >
        <p
          style={{
            color: "white",
            fontSize: 15,
            fontWeight: "bold",
            margin: 0,
            whiteSpace: "nowrap",
          }}
        >
          {user?.preferred_username || ""}
        </p>

        {user && user.message !== "OIDC not configured." && (
          <Tooltip title="Logout">
            <Button
              type="text"
              icon={<LogoutOutlined />}
              style={{ color: "white" }}
              size={{ xs: "small", sm: "middle" }}
              onClick={handleLogout}
            />
          </Tooltip>
        )}
      </div>
    </Header>
  );
};

export default CustomHeader;
