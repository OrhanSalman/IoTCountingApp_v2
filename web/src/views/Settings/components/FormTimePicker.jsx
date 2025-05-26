import React from "react";

import { Form, TimePicker } from "antd";

const FormTimePicker = ({ label, name, disabled }) => {
  return (
    <Form.Item label={label} name={name}>
      <TimePicker
        style={{ marginBottom: "6px" }}
        allowClear={false}
        showNow={false}
        format={"HH:mm"}
        needConfirm={false}
        disabled={disabled}
      />
    </Form.Item>
  );
};

export default FormTimePicker;
