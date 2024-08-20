import './assets/css/App.css';
import './assets/fontawesome/css/all.css';
import Navbar from './components/main/Navbar.tsx';
import Cookie from "./components/main/Cookie.tsx";
import {useState} from "react";
import Projects from "./pages/Projects.tsx";
import Privacy from "./pages/Privacy.tsx";
import {Navigate, Route, Routes} from "react-router-dom";
import Place from "./pages/Place.tsx";

function App() {
    const [current_index, set_index] = useState(0);

    return <>
        <Navbar />
        <div className="content-container">
            <div className="content">
                <Routes>
                    <Route path="/" element={<Projects callback={callback} current_index={current_index} />} />
                    <Route path="/privacy" element={<Privacy />} />
                    <Route path="/place" element={<Place />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </div>
        </div>
        <Cookie />
    </>

    function callback(index: number) {
        set_index(index);
    }
}

export default App;
