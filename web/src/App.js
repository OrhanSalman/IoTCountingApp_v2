import "./App.css";
import { BrowserRouter as Router } from "react-router-dom";
import BaseView from "./views/BaseView";
import { DeviceProvider } from "./api/DeviceContext";

const App = () => {
  return (
    <Router>
      <DeviceProvider>
        <BaseView />
      </DeviceProvider>
    </Router>
  );
};

export default App;
