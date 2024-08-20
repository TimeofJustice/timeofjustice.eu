import Switch from "../main/Switch.tsx";
import {trySetCookie} from "../../helper/Cookie.tsx";

export default function DarkModeSwitch() {
    let current_mode = document.getElementsByTagName("html")[0].className

    return <Switch callback={() => {onChange()}} />

    function onChange() {
        if (current_mode === "dark") {
            current_mode = "light"
        } else {
            current_mode = "dark"
        }

        trySetCookie("mode", current_mode, 30)
        document.getElementsByTagName("html")[0].className = current_mode
    }
}