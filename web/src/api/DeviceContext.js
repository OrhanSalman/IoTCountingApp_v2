import React, {
  createContext,
  useReducer,
  useCallback,
  useEffect,
  useRef,
} from "react";
import { message } from "antd";
import errorHandler from "./utils/errorHandler";

import baseURL from "./baseUrl";

export const DeviceContext = createContext();

const initialState = {
  data: [],
  counts: [],
  tracking: [],
  times: [],
  user: {},
  originalData: [],
  isModified: false,
  image: null,
  health: {},
  benchmarks: [],
  simulations: [],
  sample_video: null,
  loading: false,
  error: null,
};

const updateNestedObject = (obj, path, value) => {
  if (path.length === 0) return value;
  const [head, ...rest] = path;

  if (Array.isArray(obj)) {
    const index = parseInt(head, 10);
    if (isNaN(index)) {
      throw new Error(`Invalid array index: ${head}`);
    }
    const updatedArray = [...obj];
    updatedArray[index] = updateNestedObject(obj[index], rest, value);
    return updatedArray;
  }

  return {
    ...obj,
    [head]: updateNestedObject(obj ? obj[head] : {}, rest, value),
  };
};

function reducer(state, action) {
  switch (action.type) {
    case "FETCH_INIT":
      return { ...state, loading: true, error: null };
    case "FETCH_SUCCESS":
      return {
        ...state,
        loading: false,
        data: action.payload,
        originalDevice: action.payload,
        isModified: false,
      };
    case "FETCH_FAILURE":
      return { ...state, loading: false, error: action.error };

    // IMAGE
    case "FETCH_IMAGE_INIT":
      return { ...state, loading: true, error: null };
    case "FETCH_IMAGE_SUCCESS":
      return { ...state, loading: false, image: action.payload };
    case "FETCH_IMAGE_FAILURE":
      return { ...state, loading: false, error: action.error };

    // HEALTH
    case "FETCH_HEALTH_INIT":
      return { ...state, loading: false, error: null };
    case "FETCH_HEALTH_SUCCESS":
      return { ...state, loading: false, health: action.payload };
    case "FETCH_HEALTH_FAILURE":
      return { ...state, loading: false, error: action.error };

    // BENCHMARKS
    case "FETCH_BENCHMARKS_INIT":
      return { ...state, loading: true, error: null };
    case "FETCH_BENCHMARKS_SUCCESS":
      return { ...state, loading: false, benchmarks: action.payload };
    case "FETCH_BENCHMARKS_FAILURE":
      return { ...state, loading: false, error: action.error };

    // SIMULATION VIDEOS
    case "FETCH_SIMULATIONS_INIT":
      return { ...state, loading: true, error: null };
    case "FETCH_SIMULATIONS_SUCCESS":
      return { ...state, loading: false, simulations: action.payload };
    case "FETCH_SIMULATIONS_FAILURE":
      return { ...state, loading: false, error: action.error };

    // SAMPLE VIDEO
    case "FETCH_SAMPLE_VIDEO_INIT":
      return { ...state, loading: true, error: null };
    case "FETCH_SAMPLE_VIDEO_SUCCESS":
      return { ...state, loading: false, sample_video: action.payload };
    case "FETCH_SAMPLE_VIDEO_FAILURE":
      return { ...state, loading: false, error: action.error };

    // UPDATE CONFIG
    case "UPDATE_CONFIG_INIT":
      return { ...state, loading: true, error: null };
    case "UPDATE_CONFIG_SUCCESS":
      return {
        ...state,
        loading: false,
        data: action.payload,
        originalDevice: action.payload,
        isModified: false,
      };
    case "UPDATE_CONFIG_FAILURE":
      return { ...state, loading: false, error: action.error };

    // FETCH USER
    case "FETCH_USER_INIT":
      return { ...state, loading: false, error: null };
    case "FETCH_USER_SUCCESS":
      return { ...state, loading: false, user: action.payload };
    case "FETCH_USER_FAILURE":
      return { ...state, loading: false, error: action.error };

    // LOCAL UPDATE TO STORAGE
    case "LOCAL_UPDATE_DEVICE":
      const updatedState = {
        ...state,
        data: updateNestedObject(state.data, action.path, action.payload),
        loading: false,
        isModified: true,
      };
      return updatedState;

    case "LOCAL_UPDATE_DEVICE_TAGS":
      const updatedDeviceTags = {
        ...state.data,
        deviceTags: action.payload,
      };

      const newDeviceTagsState = {
        ...state,
        data: updatedDeviceTags,
        isModified: true,
        loading: false,
      };

      return newDeviceTagsState;

    default:
      throw new Error(`Unhandled action type: ${action.type}`);
  }
}

export const DeviceProvider = ({ children }) => {
  const deviceIdRef = useRef(null);
  const userIdRef = useRef(null);
  const [state, dispatch] = useReducer(reducer, initialState);
  //const [cookies] = useCookies([]);

  const fetchConfig = useCallback(async () => {
    dispatch({ type: "FETCH_INIT" });
    try {
      const response = await fetch(`${baseURL}api/config`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          //authorization: `Bearer ${cookies.access_token}`,
        },
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();
        deviceIdRef.current = data.id;
        dispatch({ type: "FETCH_SUCCESS", payload: data });
      } else {
        dispatch({
          type: "FETCH_FAILURE",
          error: `${response.status} ${response.statusText}`,
        });
        errorHandler(response.status, response.statusText);
      }
    } catch (error) {
      const status = error?.status || "Unbekannt";
      const statusText = error?.statusText || "Unbekannter Fehler";
      dispatch({ type: "FETCH_FAILURE", error: statusText });
      errorHandler(status, statusText);
    }
  }, []);

  const fetchImage = useCallback(async (snap = false) => {
    dispatch({ type: "FETCH_IMAGE_INIT" });

    try {
      const response = await fetch(`${baseURL}api/image?snap=${snap}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          // authorization: `Bearer ${cookies.access_token}`,
        },
        credentials: "include",
      });

      if (response.ok) {
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        dispatch({ type: "FETCH_IMAGE_SUCCESS", payload: imageUrl });
      } else {
        const result = await response.text();

        dispatch({
          type: "FETCH_IMAGE_FAILURE",
          error: result,
        });
        errorHandler(response.status, result);
      }
    } catch (error) {
      const status = error?.status || "Unbekannt";
      const statusText = error?.message || "Unbekannter Fehler";
      dispatch({
        type: "FETCH_IMAGE_FAILURE",
        error: statusText,
      });
      //errorHandler(status, statusText);
    }
  }, []);

  const fetchHealth = useCallback(async () => {
    dispatch({ type: "FETCH_HEALTH_INIT" });

    try {
      const response = await fetch(`${baseURL}api/health`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          //authorization: `Bearer ${cookies.access_token}`,
        },
        credentials: "include",
      });

      if (response.ok) {
        const healthData = await response.json();
        if (JSON.stringify(healthData) !== JSON.stringify(state.health)) {
          dispatch({ type: "FETCH_HEALTH_SUCCESS", payload: healthData });
        }
        //dispatch({ type: "FETCH_HEALTH_SUCCESS", payload: health });
      } else {
        dispatch({
          type: "FETCH_HEALTH_FAILURE",
          error: `${response.status} ${response.statusText}`,
        });
      }
    } catch (error) {
      const statusText =
        error?.statusText || "Unbekannter Fehler beim holen der Health";
      dispatch({
        type: "FETCH_HEALTH_FAILURE",
        error: statusText,
      });
    }
  }, []);

  const fetchBenchmarks = useCallback(async () => {
    dispatch({ type: "FETCH_BENCHMARKS_INIT" });

    try {
      const response = await fetch(`${baseURL}api/benchmarks`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          //authorization: `Bearer ${cookies.access_token}`,
        },
        credentials: "include",
      });

      if (response.ok) {
        const benchmarks = await response.json();
        dispatch({ type: "FETCH_BENCHMARKS_SUCCESS", payload: benchmarks });
      } else {
        dispatch({
          type: "FETCH_BENCHMARKS_FAILURE",
          error: `${response.status} ${response.statusText}`,
        });
        //errorHandler(response.status, response.statusText);
      }
    } catch (error) {
      const status = error?.status || "Unbekannt";
      const statusText =
        error?.statusText || "Unbekannter Fehler beim holen der Benchmarks";
      dispatch({
        type: "FETCH_BENCHMARKS_FAILURE",
        error: statusText,
      });
      //errorHandler(status, statusText);
    }
  }, []);

  const fetchSimulations = useCallback(async (simType) => {
    let dispatcher = "";
    if (simType === "simvid") {
      dispatcher = "FETCH_SIMULATIONS_";
    } else {
      message.error("Ungültiger Daten-Typ für die Fetch-Anforderung");
      return;
    }

    dispatch({ type: `${dispatcher}INIT` });

    try {
      const response = await fetch(
        `${baseURL}api/simulations?type=${simType}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            //authorization: `Bearer ${cookies.access_token}`,
          },
          credentials: "include",
        }
      );

      if (response.ok) {
        const simulations = await response.json();
        dispatch({ type: `${dispatcher}SUCCESS`, payload: simulations });
      } else {
        dispatch({
          type: `${dispatcher}FAILURE`,
          error: `${response.status} ${response.statusText}`,
        });
        //errorHandler(response.status, response.statusText);
      }
    } catch (error) {
      const status = error?.status || "Unbekannt";
      const statusText =
        error?.statusText || "Unbekannter Fehler beim holen der Simulationen";
      dispatch({
        type: `${dispatcher}FAILURE`,
        error: statusText,
      });
      //errorHandler(status, statusText);
    }
  }, []);

  const fetchSampleVideo = useCallback(async () => {
    dispatch({ type: "FETCH_SAMPLE_VIDEO_INIT" });
    try {
      const response = await fetch(`${baseURL}api/video/sample`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          //authorization: `Bearer ${cookies.access_token}`,
        },
        credentials: "include",
      });
      if (response.ok) {
        const blob = await response.blob();
        const videoUrl = URL.createObjectURL(blob);
        dispatch({ type: "FETCH_SAMPLE_VIDEO_SUCCESS", payload: videoUrl });
      } else {
        dispatch({
          type: "FETCH_SAMPLE_VIDEO_FAILURE",
          error: `${response.status} ${response.statusText}`,
        });
        //errorHandler(response.status, response.statusText);
      }
    } catch (error) {
      const status = error?.status || "Unbekannt";
      const statusText =
        error?.statusText || "Unbekannter Fehler beim holen des Videos";
      dispatch({
        type: "FETCH_SAMPLE_VIDEO_FAILURE",
        error: statusText,
      });
      //errorHandler(status, statusText);
    }
  }, []);

  const fetchData = useCallback(async (type, session_id) => {
    dispatch({ type: `FETCH_${type.toUpperCase()}DATA_INIT` });

    try {
      const response = await fetch(
        `${baseURL}api/data?type=${type}&session_id=${session_id}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
        }
      );

      if (response.ok) {
        const data = await response.json();
        if (type === "tracking") {
        }
        dispatch({
          type: `FETCH_${type.toUpperCase()}DATA_SUCCESS`,
          payload: data,
        });
      } else {
        dispatch({
          type: `FETCH_${type.toUpperCase()}DATA_FAILURE`,
          error: `${response.status} ${response.statusText}`,
        });
      }
    } catch (error) {
      const status = error?.status || "Unbekannt";
      const statusText =
        error?.statusText || "Unbekannter Fehler beim holen der Daten";
      dispatch({
        type: `FETCH_${type.toUpperCase()}DATA_FAILURE`,
        error: statusText,
      });
      errorHandler(status, statusText);
    }
  }, []);

  const updateData = useCallback(async () => {
    dispatch({ type: "UPDATE_CONFIG_INIT" });

    try {
      const response = await fetch(`${baseURL}api/config`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(state.data),
      });

      if (response.ok) {
        if (
          state.data?.deviceTags &&
          state.data?.deviceTags[0]?.tags &&
          state.data?.deviceRois
        ) {
          const availableTags = state.data.deviceTags[0].tags;
          state.data.deviceRois = state.data.deviceRois.map((roi) => ({
            ...roi,
            tagsInThisRegion: (roi.tagsInThisRegion || []).filter((tag) =>
              availableTags.includes(tag)
            ),
          }));
        }

        dispatch({ type: "UPDATE_CONFIG_SUCCESS", payload: state.data });
        message.success("Konfiguration erfolgreich gespeichert");
        return response;
      } else {
        const errorText = await response.text();

        errorHandler(response.status, errorText, false);

        const errorMessage = `${response.status} ${errorText}`;

        dispatch({
          type: "UPDATE_CONFIG_FAILURE",
          error: errorMessage,
        });

        message.error(`Fehler: ${errorMessage}`);

        return response;
      }
    } catch (error) {
      const errorMessage =
        error.message || "Unbekannter Fehler beim Speichern der Konfiguration";

      errorHandler("Unbekannt", errorMessage, false);

      dispatch({
        type: "UPDATE_CONFIG_FAILURE",
        error: errorMessage,
      });

      message.error(`Fehler: ${errorMessage}`);

      return null;
    }
  }, [state.data]);

  const fetchUserData = useCallback(async () => {
    dispatch({ type: "FETCH_USER_INIT" });
    try {
      const response = await fetch(`${baseURL}api/userinfo`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          //authorization: `Bearer ${cookies.access_token}`,
        },
        credentials: "include",
      });

      if (response.ok) {
        const user = await response.json();
        userIdRef.current = user.id;
        dispatch({ type: "FETCH_USER_SUCCESS", payload: user });
      } else {
        dispatch({
          type: "FETCH_USER_FAILURE",
          error: `${response.status} ${response.statusText}`,
        });
        //errorHandler(response.status, response.statusText);
      }
    } catch (error) {
      const status = error?.status || "Unbekannt";
      const statusText =
        error?.statusText || "Unbekannter Fehler beim holen der User-Daten";
      dispatch({ type: "FETCH_FAILURE", error: statusText });
      //errorHandler(status, statusText);
    }
  }, []);

  useEffect(() => {
    const loadData = async () => {
      try {
        await Promise.all([
          fetchConfig(),
          fetchImage(),
          fetchUserData(),
          fetchHealth(),
          fetchBenchmarks(),
          fetchSimulations("simvid"),
          fetchSampleVideo(),
        ]);
      } catch (error) {
        //errorHandler(error.status, error.statusText);
      }
    };

    loadData();
  }, [
    fetchConfig,
    fetchImage,
    fetchUserData,
    fetchHealth,
    fetchSimulations,
    fetchBenchmarks,
    fetchData,
  ]);

  useEffect(() => {
    const intervalId = setInterval(async () => {
      await fetchHealth();
    }, 2400);

    return () => clearInterval(intervalId);
  }, [fetchHealth]);

  useEffect(() => {
    const userCheckInterval = setInterval(async () => {
      await fetchUserData();
    }, 60000);

    return () => clearInterval(userCheckInterval);
  }, [fetchUserData]);

  return (
    <DeviceContext.Provider
      value={{
        ...state,
        dispatch,
        fetchConfig,
        fetchImage,
        fetchHealth,
        fetchBenchmarks,
        fetchSimulations,
        fetchSampleVideo,
        updateData,
        fetchUserData,
        fetchData,
      }}
    >
      {children}
    </DeviceContext.Provider>
  );
};
