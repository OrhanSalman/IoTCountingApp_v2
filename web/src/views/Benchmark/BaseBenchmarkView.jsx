import React from "react";
import { Outlet } from "react-router-dom";

import BenchmarkView from "./pages/BenchmarkView";
import GenericBaseViewSinglePage from "../../constants/GenericBaseViewSinglePage";

const BaseBenchmarkView = () => {
  const contentComponents = {
    1: BenchmarkView,
  };

  return (
    <>
      <GenericBaseViewSinglePage components={contentComponents} />
      <Outlet />
    </>
  );
};

export default BaseBenchmarkView;
