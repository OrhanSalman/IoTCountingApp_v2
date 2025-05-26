import { message } from "antd";
import baseURL from "./baseUrl";
import errorHandler from "./utils/errorHandler";

/**
 * Sends MQTT settings to the server
 * @param {Object} data - The MQTT settings to be saved
 * @param {String} data.host - MQTT Broker Host
 * @param {Number} data.port - MQTT Broker Port
 * @param {String} data.username - MQTT Username
 * @param {String} data.password - MQTT Password
 * @param {String} data.clientId - MQTT Client ID
 * @returns {Promise<void>}
 */
const postMQTTSettings = async (data) => {
  try {
    const response = await fetch(`${baseURL}api/mqtt`, {
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
    message.error(
      "Beim Speichern der MQTT-Einstellungen ist ein Fehler aufgetreten."
    );
  }
};

/**
 * Deletes MQTT settings from the server
 * @returns {Promise<void>}
 */
const deleteMQTTSettings = async () => {
  try {
    const response = await fetch(`${baseURL}api/mqtt`, {
      method: "DELETE",
      credentials: "include",
    });

    const result = await response.json();

    if (response.ok) {
      message.success(result.message || "Gelöscht.");
    } else {
      errorHandler(response.status, result.error);
    }
  } catch (error) {
    message.error(
      "Beim Löschen der MQTT-Einstellungen ist ein Fehler aufgetreten."
    );
  }
};

/**
 * Fetches MQTT settings from the server
 * @returns {Promise<Object|null>} The MQTT settings or null in case of error
 */
const getMQTTSettings = async () => {
  try {
    const response = await fetch(`${baseURL}api/mqtt`, {
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
    message.error("Fehler beim laden der MQTT-Einstellungen: " + error.message);
  }
};

export { postMQTTSettings, deleteMQTTSettings, getMQTTSettings };
