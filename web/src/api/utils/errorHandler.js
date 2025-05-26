import { message } from "antd";

const errorHandler = (status, detail = "", showMessage = true) => {
  // Standardisierte Fehlermeldungen
  const errorMessages = {
    400: `Bad Request: ${detail || "Die Anfrage war fehlerhaft."}`,
    401: `Unauthorized: ${detail || "Nicht autorisiert für diese Aktion."}`,
    403: `Forbidden: ${
      detail || "Zugriff auf diese Ressourcen ist untersagt."
    }`,
    //404: `Not Found: ${
    //  detail || "Die angeforderte Ressource wurde nicht gefunden."
    //}`,
    500: `Internal Server Error: ${
      detail || "Ein interner Serverfehler ist aufgetreten."
    }`,
    502: `Bad Gateway: ${
      detail || "Der Server hat eine ungültige Antwort erhalten."
    }`,
    503: `Service Unavailable: ${
      detail || "Der Server ist vorübergehend nicht verfügbar."
    }`,
    504: `Gateway Timeout: ${
      detail || "Zeitüberschreitung beim Warten auf Serverantwort."
    }`,
  };

  const errorObj = {
    status,
    message:
      errorMessages[status] ||
      `Error ${status}: ${detail || "Unbekannter Fehler"}`,
    timestamp: new Date().toISOString(),
    detail,
  };

  if (showMessage && errorObj.message) {
    message.error(errorObj.message);
  }

  //Debugging
  //console.error("API Error:", errorObj);

  return errorObj;
};

export default errorHandler;
