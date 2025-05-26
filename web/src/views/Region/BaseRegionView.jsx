import React from "react";
import { Outlet } from "react-router-dom";

import GenericBaseViewSinglePage from "../../constants/GenericBaseViewSinglePage";
import ROIView from "../Region/pages/ROIView";

const BaseRegionView = () => {
  const contentComponents = {
    1: ROIView,
  };

  return (
    <>
      <GenericBaseViewSinglePage components={contentComponents} />
      <Outlet />
    </>
  );
};

export default BaseRegionView;
