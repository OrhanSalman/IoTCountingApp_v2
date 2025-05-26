import React, {
  useContext,
  useEffect,
  useState,
  useRef,
  useMemo,
  useCallback,
} from "react";
import {
  Table,
  Image,
  Carousel,
  Divider,
  Button,
  Tooltip,
  Row,
  message,
  Modal,
  InputNumber,
} from "antd";
import { DeviceContext } from "../../../api/DeviceContext";
import {
  MinusCircleOutlined,
  PlayCircleOutlined,
  CameraOutlined,
  EditOutlined,
} from "@ant-design/icons";
import { useUpdateHandler } from "../context/updateHandler";
import {
  processSimulationsData,
  createTableColumns,
  createExpandedRows,
  runSimulation,
  createTestVideo,
  saveSimulationConfig,
} from "../static/staticFunctions";

const SimulationView = () => {
  const {
    data,
    health,
    sample_video,
    simulations,
    fetchSimulations,
    fetchHealth,
    fetchSampleVideo,
  } = useContext(DeviceContext);

  // State
  const [selectedRowKey, setSelectedRowKey] = useState(null);
  const [expandedRowKeys, setExpandedRowKeys] = useState([]);
  const [customInferenceLoading, setCustomInferenceLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [activeCreatingTestVideo, setActiveCreatingTestVideo] = useState(false);
  const [duration, setDuration] = useState(10);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);

  // Refs
  const carouselRef = useRef(null);
  const { handleBatchUpdate } = useUpdateHandler();

  const tableData = useMemo(
    () => processSimulationsData(simulations),
    [simulations]
  );
  const columns = useMemo(() => createTableColumns(tableData), [tableData]);
  const expandedRows = useMemo(() => createExpandedRows(), []);

  const expandableConfig = useMemo(
    () => ({
      expandedRowRender: (record) => (
        <Table
          columns={expandedRows}
          dataSource={[record]}
          pagination={false}
          showHeader={true}
          size="small"
          bordered
          style={{ margin: 0 }}
        />
      ),
      rowExpandable: () => true,
      expandedRowKeys: expandedRowKeys,
      onExpandedRowsChange: (expandedKeys) => {
        setExpandedRowKeys(expandedKeys);
      },
    }),
    [expandedRows, expandedRowKeys]
  );

  useEffect(() => {
    if (!health?.inference?.simulation) {
      fetchSimulations("simvid");
    }
  }, [health?.inference?.simulation, fetchSimulations]);

  useEffect(() => {
    if (tableData.length > 0 && !selectedRowKey) {
      setSelectedRowKey(tableData[0].key);
    }
  }, [tableData, selectedRowKey]);

  useEffect(() => {
    setCustomInferenceLoading(false);
  }, [health?.inference?.simulation]);

  // Handler functions
  const handleRunSimulation = useCallback(async () => {
    await runSimulation(setCustomInferenceLoading, fetchHealth);
  }, [fetchHealth]);

  const handleCreateNewTestVideo = useCallback(() => {
    setIsModalVisible(true);
  }, []);

  const handleOk = useCallback(async () => {
    if (!duration) {
      message.error("Bitte geben Sie eine Dauer ein.");
      return;
    }
    setIsModalVisible(false);
    await createTestVideo(duration, setActiveCreatingTestVideo);
  }, [duration]);

  const handleCancel = useCallback(() => {
    setIsModalVisible(false);
  }, []);

  const onRowClick = useCallback((record) => {
    return {
      onClick: () => {
        setSelectedRowKey(record.key);
        if (carouselRef.current) {
          carouselRef.current.goTo(parseInt(record.key));
        }
      },
    };
  }, []);

  const onCarouselChange = useCallback((currentSlide) => {
    setSelectedRowKey(currentSlide.toString());
  }, []);

  const collapseAll = useCallback(() => {
    setExpandedRowKeys([]);
  }, []);

  const saveConfig = useCallback(() => {
    saveSimulationConfig(selectedRowKey, tableData, data, handleBatchUpdate);
  }, [selectedRowKey, tableData, data, handleBatchUpdate]);

  // Row selection configuration
  const rowSelection = useMemo(
    () => ({
      type: "radio",
      selectedRowKeys: selectedRowKey ? [selectedRowKey] : [],
      onChange: (selectedRowKeys) => {
        const key = selectedRowKeys[0];
        setSelectedRowKey(key);
        if (carouselRef.current && key) {
          carouselRef.current.goTo(parseInt(key));
        }
      },
    }),
    [selectedRowKey]
  );

  const tableTitle = useCallback(
    () => (
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Tooltip title="Zusammenklappen">
          <Button
            icon={<MinusCircleOutlined />}
            type="default"
            style={{ width: "36px", marginRight: "8px" }}
            onClick={collapseAll}
          />
        </Tooltip>
        <div>
          <Row>
            <Tooltip title="Neues Testvideo erstellen">
              <Button
                icon={<CameraOutlined />}
                type="default"
                onClick={handleCreateNewTestVideo}
                disabled={
                  activeCreatingTestVideo ||
                  health?.video_converter ||
                  health?.inference?.status ||
                  health?.inference?.simulation ||
                  health?.camera?.is_capturing
                }
                loading={
                  activeCreatingTestVideo || health?.video_converter?.status
                }
                style={{ width: "126px", marginRight: "8px" }}
              >
                {health?.video_converter
                  ? "Konvertieren..."
                  : health?.camera?.is_capturing
                  ? "Zeichne auf..."
                  : "Testvideo"}
              </Button>
            </Tooltip>

            <Tooltip title="Ausgewählte Konfiguration übernehmen">
              <Button
                icon={<EditOutlined />}
                type="default"
                style={{ width: "126px", marginRight: "8px" }}
                onClick={saveConfig}
              >
                Übernehmen
              </Button>
            </Tooltip>
            <Tooltip title="Führt eine Simulation mit den derzeit gespeicherten Konfigurationen durch. Kann oben über das Play-Symbol abgebrochen werden.">
              <Button
                icon={<PlayCircleOutlined />}
                type={!health?.inference?.simulation ? "default" : "dashed"}
                onClick={handleRunSimulation}
                disabled={
                  health?.inference?.status ||
                  health?.inference?.simulation ||
                  health?.inference?.exporter ||
                  health?.benchmark?.status
                }
                loading={
                  health?.inference?.simulation || customInferenceLoading
                }
              >
                {health?.inference?.simulation
                  ? "Simulation läuft..."
                  : "Simulieren"}
              </Button>
            </Tooltip>
          </Row>
        </div>
      </div>
    ),
    [
      collapseAll,
      handleCreateNewTestVideo,
      saveConfig,
      handleRunSimulation,
      health,
      activeCreatingTestVideo,
      customInferenceLoading,
    ]
  );

  const tableFooter = useCallback(
    () => <span>{`Simulationen: ${tableData.length} `}</span>,
    [tableData.length]
  );

  const videoPreview = useMemo(() => {
    if (!sample_video) {
      return (
        <span style={{ fontSize: "16px", color: "#999" }}>
          Kein Video vorhanden
        </span>
      );
    }

    if (isVideoPlaying) {
      return (
        <video
          autoPlay
          controls
          width="100%"
          height="100%"
          src={sample_video}
          style={{ objectFit: "contain" }}
          onEnded={() => setIsVideoPlaying(false)}
        />
      );
    }

    return (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
        onClick={() => {
          fetchSampleVideo();
          setIsVideoPlaying(true);
        }}
      >
        <PlayCircleOutlined style={{ fontSize: "64px", color: "#1890ff" }} />
      </div>
    );
  }, [sample_video, isVideoPlaying, fetchSampleVideo]);

  return (
    <div style={{ width: "100%" }}>
      <div style={{ display: "flex", flexDirection: "column" }}>
        <Table
          showSorterTooltip={false}
          columns={columns}
          expandable={expandableConfig}
          dataSource={tableData}
          rowKey={(record) => record.key}
          size="small"
          bordered
          pagination={false}
          title={tableTitle}
          footer={tableFooter}
          loading={!simulations}
          locale={{ emptyText: "Keine Simulationen gefunden" }}
          scroll={{ x: 950, y: "calc(60vh - 170px)" }}
          style={{ width: "100%", flex: 1, overflowX: "auto" }}
          rowSelection={rowSelection}
          onRow={onRowClick}
        />
      </div>

      <Divider style={{ margin: "16px 0" }} />

      <Carousel
        effect="fade"
        afterChange={onCarouselChange}
        ref={carouselRef}
        style={{ width: "100%" }}
      >
        {simulations &&
          simulations.map((simulation, index) => (
            <div
              key={index}
              style={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                height: "50vh",
              }}
            >
              <Image
                style={{
                  maxWidth: "80%",
                  maxHeight: "80%",
                  objectFit: "contain",
                  margin: "0 auto",
                }}
                src={simulation.image_url}
                fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMIAAADDCAYAAADQvc6UAAABRWlDQ1BJQ0MgUHJvZmlsZQAAK..."
                preview={{
                  destroyOnClose: true,
                  imageRender: () => (
                    <video
                      muted
                      width="70%"
                      controls
                      src={simulation.video_url}
                      style={{ margin: "0 auto", display: "block" }}
                    />
                  ),
                  toolbarRender: () => null,
                }}
              />
            </div>
          ))}
      </Carousel>

      <Modal
        title="Neues Testvideo erstellen"
        open={isModalVisible}
        onOk={handleOk}
        onCancel={handleCancel}
        okText="Erstellen"
        cancelText="Abbrechen"
      >
        <InputNumber
          placeholder="Geben Sie die Dauer in Sekunden ein"
          defaultValue={duration}
          onChange={(value) => setDuration(value)}
          type="number"
          min={10}
          max={180}
          style={{ width: "80%", marginLeft: "10px" }}
        />
        <p>
          Die Länge des Testvideos kann zwischen 10 und 180 Sekunden liegen.
          Eine höhere Dauer führt zu längeren Wartezeiten.
        </p>
        <Divider orientation="left" plain>
          Video
        </Divider>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            height: "200px",
            backgroundColor: "#f0f0f0",
            borderRadius: "8px",
            cursor: sample_video ? "pointer" : "default",
            overflow: "hidden",
          }}
        >
          {videoPreview}
        </div>
      </Modal>
    </div>
  );
};

export default SimulationView;
