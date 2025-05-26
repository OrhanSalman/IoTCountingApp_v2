import { message } from "antd";
//import { useCookies } from "react-cookie";
import baseURL from "./baseUrl";
import errorHandler from "./utils/errorHandler";

/**
 * Sends system settings to the server
 * @param {Object} data - The system settings to be saved
 * @returns {Promise<void>}
 */
const postSystemSettings = async (data) => {
  try {
    const response = await fetch(`${baseURL}api/systemsettings`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify(data),
    });

    const result = await response.json();

    if (response.ok) {
      message.success(result.message || "Gespeichert.");
    } else {
      errorHandler(response.status, result.error);
    }
  } catch (error) {
    message.error(`Fehler beim speichern der Systemeinstellungen: ${error}`);
  }
};

/**
 * Fetches system settings from the server
 * @returns {Promise<Object|null>} The system settings or null in case of error
 */
const getSystemSettings = async () => {
  try {
    const response = await fetch(`${baseURL}api/systemsettings`, {
      method: "GET",
      credentials: "include",
    });

    const result = await response.json();

    if (response.ok) {
      return result;
    } else {
      //errorHandler(response.status, result.error);
      return null;
    }
  } catch (error) {
    message.error(`Fehler beim laden der Systemeinstellungen: ${error}`);
  }
};

export { postSystemSettings, getSystemSettings };
