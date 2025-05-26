import { Progress } from "antd";

/* Progress Bar for interactive feedback for  video simulations */

const ProgressBar = () => (
  <Progress
    percent={50}
    status="active"
    strokeColor={{ from: "#108ee9", to: "#87d068" }}
    style={{ width: "100%" }}
    format={(percent) => <span style={{ color: "white" }}>{percent}%</span>}
  />
);

export default ProgressBar;
