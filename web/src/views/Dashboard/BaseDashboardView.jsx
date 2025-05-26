import React, { useState, useContext, useEffect } from "react";
import { Outlet } from "react-router-dom";
import { Card, Col, Image, Row } from "antd";
import { DeviceContext } from "../../api/DeviceContext";
import baseUrl from "../../api/baseUrl";

const BaseDashboardView = () => {
  const { data, health } = useContext(DeviceContext);

  const [frame, setFrame] = useState([]);

  useEffect(() => {
    if (health?.inference?.status) {
      const interval = setInterval(() => {
        fetch(`${baseUrl}api/inference/frame`)
          .then((response) => {
            if (!response.ok) {
              return null;
            }
            return response.blob();
          })
          .then((blob) => {
            const imageUrl = URL.createObjectURL(blob);
            setFrame(imageUrl);
            localStorage.setItem("lastFrame", imageUrl);
          })
          .catch((error) => {
            console.error("Fetch error:", error);
          });
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [health?.inference?.status]);

  useEffect(() => {
    const savedFrame = localStorage.getItem("lastFrame");
    if (savedFrame) {
      setFrame(savedFrame);
    }
  }, []);

  return (
    <>
      <div
        style={{
          width: "100%",
          padding: "12px",
          margin: "0 auto",
          height: "calc(100vh - 64px)",
          overflow: "hidden",
        }}
      >
        <Row
          gutter={16}
          style={{
            marginTop: 16,
            height: "100%",
            overflow: "hidden",
          }}
        >
          {frame && (
            <Card
              size="small"
              title="Bildvorschau"
              style={{
                width: "100%",
                marginBottom: 16,
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                }}
              >
                <Image
                  src={frame}
                  style={{
                    maxWidth: "100%",
                    maxHeight: "calc(100vh - 200px)",
                    objectFit: "contain",
                  }}
                />
              </div>
            </Card>
          )}
        </Row>
        <Outlet />
      </div>
    </>
  );
};

export default BaseDashboardView;
