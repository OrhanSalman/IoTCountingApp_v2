import { useCallback, useContext } from "react";
import { DeviceContext } from "../../../../api/DeviceContext";
import { message } from "antd";
import {
  getDeviceTags,
  calculateNewColor,
  calculatePointCoordinates,
  generateTempId,
} from "../staticFunctions";

export const useAddHandler = (imageSize, deviceTags) => {
  const { data, dispatch } = useContext(DeviceContext);
  const maxNumberOfRegions = 5;
  const maxNumberOfRegionPoints = 8;

  const handleAdd = useCallback(() => {
    if (data?.deviceRois?.length >= maxNumberOfRegions) {
      message.error(
        `Maximale Anzahl an Regionen erreicht (${maxNumberOfRegions}).`
      );
      return;
    }

    try {
      const tagObjects = getDeviceTags(deviceTags);
      const tagIds = tagObjects.map((tag) => tag.key);

      const newRoiId = generateTempId();
      const newKey = Date.now();
      const { x1, y1, x2, y2 } = calculatePointCoordinates(imageSize);

      const newROI = {
        deviceId: data?.id,
        id: newRoiId,
        isFormationClosed: false,
        line_thickness: 3,
        points: [
          {
            id: generateTempId(),
            direction: "Norden",
            x: x1,
            y: y1,
            roi: newRoiId,
          },
          {
            id: generateTempId(),
            direction: "Osten",
            x: x2,
            y: y2,
            roi: newRoiId,
          },
        ],
        region_color: calculateNewColor(data),
        roiName: `ROI_${newKey}`,
        tagsInThisRegion: tagIds,
      };

      dispatch({
        type: "LOCAL_UPDATE_DEVICE",
        path: ["deviceRois"],
        payload: [...(data?.deviceRois || []), newROI],
      });
    } catch (error) {
      console.error("Error in handleAdd:", error);
      message.error("Fehler beim Erstellen der Region");
    }
  }, [data, dispatch, imageSize, deviceTags, maxNumberOfRegions]);

  const handleAddPointToRoi = useCallback(
    (roiId) => {
      if (!imageSize || !imageSize.width || !imageSize.height) {
        message.error("Inputgröße ist nicht definiert oder unvollständig.");
        return;
      }
      const roiIndex = data?.deviceRois?.findIndex((roi) => roi.id === roiId);
      if (roiIndex === -1) {
        message.error("ROI not found.");
        return;
      }

      const roi = data?.deviceRois[roiIndex];

      if (roi.points.length >= maxNumberOfRegionPoints) {
        message.error(
          `Maximale Anzahl an Koordinaten in dieser Region erreicht (${maxNumberOfRegionPoints}).`
        );
        return;
      }

      // Define all possible directions
      const allDirections = [
        "Norden",
        "Osten",
        "Süden",
        "Westen",
        "Nordosten",
        "Südosten",
        "Südwesten",
        "Nordwesten",
      ];

      // Get directions already used in this ROI
      const usedDirections = roi.points
        .map((point) => point.direction)
        .filter(Boolean);

      // Filter out used directions to get available ones
      const availableDirections = allDirections.filter(
        (dir) => !usedDirections.includes(dir)
      );

      // Choose a direction that hasn't been used yet
      let newDirection =
        availableDirections.length > 0 ? availableDirections[0] : "Norden";

      const newPoint = {
        id: generateTempId(),
        direction: newDirection,
        x: imageSize.width / 2,
        y: imageSize.height / 2,
        roi: roiId ?? null,
      };

      const shouldCloseFormation =
        roi.points.length === 2 && !roi.isFormationClosed;

      const updatedRoi = {
        ...roi,
        points: [...roi.points, newPoint],
        isFormationClosed: shouldCloseFormation ? true : roi.isFormationClosed,
      };

      const updatedDeviceRois = data?.deviceRois?.map((roi) =>
        roi.id === roiId ? updatedRoi : roi
      );

      dispatch({
        type: "LOCAL_UPDATE_DEVICE",
        path: ["deviceRois"],
        payload: updatedDeviceRois,
      });
    },
    [data, dispatch, imageSize, maxNumberOfRegionPoints]
  );

  return {
    handleAdd,
    handleAddPointToRoi,
  };
};
