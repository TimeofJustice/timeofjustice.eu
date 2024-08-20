import Cookies from 'universal-cookie';
import {trySetCookie} from "../../helper/Cookie.tsx";
import { useState } from "react";

const cookies = new Cookies();

export default function Cookie() {
    let initial_style = "-200px";
    if (!cookies.get("cookie_consent")) initial_style = "10px";

    const [object_style, set_style] = useState(initial_style);

    return <div className="cookie-banner" style={{bottom: object_style}}>
        <div className="text">
            This website uses cookies to improve your experience 🍪
        </div>
        <a href="https://gdpr-info.eu/" target="_blank">Read more</a>
        <div className="buttons">
            <div className="accept" onClick={() => onAccept()}>Accept</div>
            <div className="decline" onClick={() => onDecline()}>Decline</div>
        </div>
    </div>

    function onAccept() {
        trySetCookie("cookie_consent", "true", 30, true);
        set_style("-200px");
    }

    function onDecline() {
        set_style("-200px");
    }
}





