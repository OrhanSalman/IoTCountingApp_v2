import runCommand from "../../../api/runCommand";
import { format as formatOptions } from "../../../../src/constants/constants";

export const parseDateTime = (datetime) => {
  if (!datetime) return new Date(0);

  const [date, time] = datetime.split("_");
  if (!date || !time) return new Date(0);

  const [year, month, day] = date.split("-");
  const [hour, minute] = time.split("-");

  if (!year || !month || !day || !hour || !minute) return new Date(0);

  return new Date(year, month - 1, day, hour, minute);
};

export const processSimulationsData = (simulations) => {
  if (!simulations) return [];

  return simulations
    .sort(
      (a, b) =>
        parseDateTime(b.config.datetime) - parseDateTime(a.config.datetime)
    )
    .map((simulation, index) => {
      return {
        key: index.toString(),
        deviceConfigId: simulation.config.device_config_id,
        no: index + 1,
        model: simulation.config.model,
        format: simulation.config.format,
        tracker: simulation.config.tracker,
        input_size: simulation.config.imgsz,
        precision: simulation.config.quantization,
        iou: simulation.config.iou,
        confidence: simulation.config.conf,
        video_fps: simulation.config.fps,
        avg_fps: simulation.config.performance?.avg_fps.toFixed(2),
        stride: simulation.config.vid_stride,
        last_id: simulation.config.last_track_id,
        ratio: simulation.config.detection_ratio?.toFixed(2),
        originalSimulation: simulation,
        IN: simulation.config.total_in,
        OUT: simulation.config.total_out,
        IN_CONF: simulation.config.total_in_conf?.toFixed(2),
        OUT_CONF: simulation.config.total_out_conf.toFixed(2),
      };
    });
};

export const createTableColumns = (tableData) => {
  if (!tableData || tableData.length === 0) return [];

  return [
    {
      title: "Nr.",
      dataIndex: "no",
      align: "center",
      width: 50,
    },
    {
      title: "Ø-FPS",
      dataIndex: "avg_fps",
      sorter: (a, b) => a.avg_fps - b.avg_fps,
      align: "center",
    },
    {
      title: "Ø-IN Vertrauen",
      dataIndex: "IN_CONF",
      sorter: (a, b) => a.ratio - b.ratio,
      align: "center",
    },
    {
      title: "Ø-OUT Vertrauen",
      dataIndex: "OUT_CONF",
      sorter: (a, b) => a.ratio - b.ratio,
      align: "center",
    },
    {
      title: "Treffer",
      dataIndex: "last_id",
      sorter: (a, b) => a.last_id - b.last_id,
      align: "center",
    },
    {
      title: "Verhältnis",
      dataIndex: "ratio",
      sorter: (a, b) => a.ratio - b.ratio,
      align: "center",
    },

    {
      title: "Σ IN",
      dataIndex: "IN",
      sorter: (a, b) => a.IN - b.IN,
      align: "center",
    },

    {
      title: "Σ OUT",
      dataIndex: "OUT",
      sorter: (a, b) => a.OUT - b.OUT,
      align: "center",
    },
  ];
};

export const createExpandedRows = () => [
  {
    title: "Model",
    dataIndex: "model",

    onFilter: (value, record) => record.model === value,
    filterSearch: true,
    align: "center",
  },
  {
    title: "Inputgröße",
    dataIndex: "input_size",
    onFilter: (value, record) => record.input_size === value,
    filterSearch: true,
    align: "center",
    width: 100,
  },
  {
    title: "Format",
    dataIndex: "format",
    render: (format) => format.split(".")[0],
    align: "center",
  },
  {
    title: "Präzision",
    dataIndex: "precision",
    align: "center",
  },
  {
    title: "Tracker",
    dataIndex: "tracker",
    render: (tracker) => tracker.split(".")[0],
    align: "center",
  },
  {
    title: "IoU",
    dataIndex: "iou",
    align: "center",
  },
  {
    title: "Vertrauen",
    dataIndex: "confidence",
    align: "center",
  },
  {
    title: "Videofps",
    dataIndex: "video_fps",
    align: "center",
  },
  {
    title: "Stride",
    dataIndex: "stride",
    align: "center",
  },
];

/**
 * Führt eine Simulation durch
 */
export const runSimulation = async (setCustomInferenceLoading, fetchHealth) => {
  setCustomInferenceLoading(true);
  await runCommand("start", "counting", {
    only_simulation: true,
  });
  await fetchHealth();
};

/**
 * Erstellt ein neues Test-Video
 */
export const createTestVideo = async (duration, setActiveCreatingTestVideo) => {
  setActiveCreatingTestVideo(true);
  await runCommand("video", "camera", { duration });
  setActiveCreatingTestVideo(false);
};

/**
 * Speichert die ausgewählte Konfiguration
 */
export const saveSimulationConfig = (
  selectedRowKey,
  tableData,
  data,
  handleBatchUpdate
) => {
  const selectedSimulation = tableData.find(
    (item) => item.key === selectedRowKey
  );

  if (selectedSimulation) {
    const deviceConfigId = data?.deviceConfigs?.[0]?.id;

    if (!deviceConfigId) return;

    const {
      model,
      imgsz,
      format,
      tracker,
      iou,
      conf,
      quantization,
      vid_stride,
    } = selectedSimulation.originalSimulation.config;

    const formatValue =
      formatOptions.find(
        (item) => item.label === format || format.includes(item.label)
      )?.value || format;

    const trackerValue = tracker.includes(".yaml")
      ? tracker
      : `${tracker}.yaml`;

    const updates = {
      model,
      imgsz,
      modelFormat: formatValue,
      tracker: trackerValue,
      iou,
      conf,
      quantization,
      vid_stride,
    };

    handleBatchUpdate(deviceConfigId, updates);
  }
};
