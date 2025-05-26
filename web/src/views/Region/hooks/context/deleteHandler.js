import { useCallback, useContext } from "react";
import { DeviceContext } from "../../../../api/DeviceContext";
import { message } from "antd";

export const useDeleteHandler = () => {
  const { data, dispatch } = useContext(DeviceContext);

  const findRoiIndex = (roiId) => {
    return data?.deviceRois.findIndex((roi) => roi.id === roiId);
  };

  const handleDelete = useCallback(
    (roiId) => {
      const roiIndex = findRoiIndex(roiId);
      // wenn nur noch eine Region übrig ist, löschen nicht erlauben
      //if (data.deviceRois.length <= 1) {
      //  message.error("Es muss mindestens eine Region vorhanden sein.");
      //  return;
      //}
      if (roiIndex === -1) {
        message.error("Region nicht gefunden.");
        return;
      }

      const updatedDeviceRois = data.deviceRois.filter(
        (roi) => roi.id !== roiId
      );
      dispatch({
        type: "LOCAL_UPDATE_DEVICE",
        path: ["deviceRois"],
        payload: updatedDeviceRois,
      });
    },
    [data, dispatch]
  );

  const handleDeletePointFromRoi = useCallback(
    (roiId, pointId) => {
      const roiIndex = data?.deviceRois?.findIndex((roi) => roi.id === roiId);
      if (roiIndex === -1) {
        message.error("ROI nicht gefunden.");
        return;
      }

      const roi = data?.deviceRois[roiIndex];
      const updatedPoints = roi.points.filter((point) => point.id !== pointId);

      // Automatisch die Formation öffnen, wenn weniger als 3 Punkte übrig sind
      const shouldOpenFormation =
        updatedPoints.length < 3 && roi.isFormationClosed;

      const updatedRoi = {
        ...roi,
        points: updatedPoints,
        isFormationClosed: shouldOpenFormation ? false : roi.isFormationClosed,
      };

      const updatedDeviceRois = data?.deviceRois?.map((r) =>
        r.id === roiId ? updatedRoi : r
      );

      dispatch({
        type: "LOCAL_UPDATE_DEVICE",
        path: ["deviceRois"],
        payload: updatedDeviceRois,
      });
    },
    [data, dispatch]
  );

  return { handleDelete, handleDeletePointFromRoi };
};
