import Field from "../components/place/Field.tsx";
import "../assets/css/Field.css";
import {useState} from "react";

export default function Place() {
    document.title = "Place - TimeofJustice";

    const [canvas, set_canvas] = useState(
        <div className={"place-field"} style={
            {padding: "10px"}
        }>
            r/Place is a collaborative canvas where a multitude of people can place pixels on a 1000x1000 grid.
            <br/>
            <br/>
            This version of r/Place is a recreation of the original r/Place, but with a few changes.
            It is an experimental project, and is not affiliated with Reddit.
            It could lag, and it could crash. <strong>Use at your own risk!</strong>

            <div className={"place-button"} onClick={enter}>
                Enter
            </div>
        </div>
    );

    return canvas

    function enter() {
        set_canvas(<Field size={1000}/>)
    }
}