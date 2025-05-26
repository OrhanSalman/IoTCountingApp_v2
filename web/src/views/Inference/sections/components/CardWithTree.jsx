import React from "react";
import { Tooltip, TreeSelect, Checkbox, Col } from "antd";
import { QuestionCircleOutlined } from "@ant-design/icons";

const CardWithTree = ({
  item,
  treeData,
  width,
  height,
  handleSelectedTagsChange,
}) => (
  <Col
    style={{
      flex: "1 0 auto",
      padding: "0",
      margin: "0",
      maxWidth: width,
      display: "flex",
      alignItems: "center",
    }}
  >
    <TreeSelect
      showSearch
      style={{ width: "100%", marginBottom: 8 }}
      treeData={treeData}
      value={item.value}
      dropdownStyle={{ maxHeight: 400, overflow: "auto" }}
      placeholder="Bitte auswählen"
      multiple
      treeDefaultExpandAll
      treeLine
      treeNodeFilterProp="title"
      onChange={handleSelectedTagsChange}
    />

    {item.tooltip && (
      <Tooltip title={item.tooltip}>
        <QuestionCircleOutlined style={{ marginLeft: 8 }} />
      </Tooltip>
    )}
  </Col>
);

export default CardWithTree;
