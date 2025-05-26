import { useState, useEffect } from "react";

// https://stackoverflow.com/questions/39435395/reactjs-how-to-determine-if-the-application-is-being-viewed-on-mobile-or-deskto
// https://medium.com/@josephat94/building-a-simple-react-hook-to-detect-screen-size-404a867fa2d2

const useIsMobile = () => {
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  const handleResize = () => {
    setIsMobile(window.innerWidth < 768);
  };

  useEffect(() => {
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return isMobile;
};

export default useIsMobile;
