import React, { useState } from "react";
import { Spin } from "antd";

/* * LoadingOverlay component
 * * Displays a full loading overlay with a spinner and a message
 * */

const LoadingOverlay = () => {
  const [tip, setTip] = useState("Laden...");
  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: "rgba(255, 255, 255, 0.3)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 1000,
        backdropFilter: "blur(5px)",
      }}
    >
      <Spin size="large" fullscreen tip={tip} />
    </div>
  );
};

export default LoadingOverlay;
