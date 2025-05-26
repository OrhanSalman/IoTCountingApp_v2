// Local changes, we do not push changes from here to the API

import { categories } from "../../../constants/constants";
import { v4 as uuidv4 } from "uuid";

export const generateTempId = () => {
  return `${uuidv4()}`;
};

// Mapper function to find the label name of a tag by its ID.
export const findLabelByTagId = (tagId) => {
  //const numericTagId = parseInt(tagId, 10);
  for (const category of categories) {
    for (const item of category.items) {
      if (item.value === tagId) {
        return item.label;
      }
    }
  }
  return `Undefiniertes Tag ${tagId}`;
};

export const getDeviceTags = (data) => {
  /*
   * We use the following function to get all tags of a data.
   * This function handles different tag formats and structures.
   */

  if (!data) {
    return [];
  }
  if (Array.isArray(data)) {
    if (data[0] && Array.isArray(data[0].tags)) {
      const actualTags = data[0].tags;

      return actualTags
        .map((tag) =>
          typeof tag === "string"
            ? { key: tag, label: findLabelByTagId(tag), active: false }
            : { key: tag.id, label: findLabelByTagId(tag.id), active: false }
        )
        .filter((tag) => Boolean(tag.key));
    }
    return data
      .map((tag) =>
        typeof tag === "string"
          ? { key: tag, label: findLabelByTagId(tag), active: false }
          : { key: tag.id, label: findLabelByTagId(tag.id), active: false }
      )
      .filter((tag) => Boolean(tag.key));
  }

  if (
    !data?.deviceTags ||
    data?.deviceTags?.length === 0 ||
    !data?.deviceTags?.tags
  ) {
    return [];
  }

  const tags = data?.deviceTags.tags;

  const tagDetails = tags.map((tagId) => ({
    key: tagId,
    label: findLabelByTagId(tagId),
    active: false,
  }));

  return tagDetails;
};

export const calculateNewColor = (data) => {
  /* We use the following function to calculate a new color for a region of interest. */

  // Create a set of unique colors.
  const uniqueColors = new Set(
    data?.deviceRois?.map((roi) => roi.region_color)
  );
  let newColor;

  // Generate a new color.
  do {
    newColor =
      "#" +
      Math.floor(Math.random() * 16777215)
        .toString(16)
        .padStart(6, "0");
  } while (uniqueColors.has(newColor) && uniqueColors.size < 16777216);

  return newColor;
};

export const calculatePointCoordinates = (imageSize) => {
  /*
   * We use the following when we add a new ROI. Each ROI has at least 2 tuples of coordinates.
   * Based on the image size, we calculate the initial x and y coordinates of the points.
   */
  if (imageSize.width && imageSize.height) {
    const offset = imageSize.width * 0.1;
    const centerX = imageSize.width / 2;
    const centerY = imageSize.height / 2;

    const x1 = centerX - offset;
    const y1 = centerY;
    // If we create a new ROI, we need to add at least 2 points.
    // Else we only need the coordinates above
    const x2 = centerX + offset;
    const y2 = centerY;
    return { x1, y1, x2, y2 };
  }
};

export const handleDragMove = (roiIndex, pointIndex, e, data) => {
  const updatedDeviceRois = data?.deviceRois?.map((roi, index) => {
    if (index === roiIndex) {
      return {
        ...roi,
        points: roi.points.map((point, index) => {
          if (index === pointIndex) {
            return {
              ...point,
              x: e.target.x(),
              y: e.target.y(),
            };
          }
          return point;
        }),
      };
    }
    return roi;
  });
  return updatedDeviceRois;
};
