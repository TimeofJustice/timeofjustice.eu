import Field from "../components/place/Field.tsx";
import "../assets/css/Field.css";
import {useRef, useState} from "react";
import ReCAPTCHA from "react-google-recaptcha";
import {isLocalhost} from "../helper/Localhost.tsx";
import {getCookie} from "../helper/Cookie.tsx";

export default function Place() {
    document.title = "Place - TimeofJustice";

    const apiSiteKey = isLocalhost ?
        "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI" : "6Lcba1cnAAAAAN3R3_W2gThRkiPkUrCjzgBCrNcu"
    const captchaRef = useRef<ReCAPTCHA>(null)

    const [canvas, set_canvas] = useState(
        <div className={"place-field"} style={
            {padding: "10px"}
        }>
            r/Place is a collaborative canvas where a multitude of people can place pixels on a 1000x1000 grid.
            <br/>
            <br/>
            This version of r/Place is a recreation of the original r/Place, but with a few changes.
            It is not affiliated with Reddit.
            <br/>
            The shown content is user-generated and do not necessarily reflect our views or opinions.
            We do not endorse or claim ownership of any specific image.
            Users are solely responsible for the content they create, and we cannot guarantee its accuracy or appropriateness.
            <br/>
            <br/>
            By using this website, you agree to these terms and accept the risks associated with user-generated content.
            <strong>Use at your own risk!</strong>

            <div className={"captcha-container"}>
                <ReCAPTCHA
                    sitekey={apiSiteKey}
                    ref={captchaRef}
                />
                <div className={"place-button"} onClick={onEnterSubmit}>
                    Enter
                </div>
            </div>
        </div>
    );

    return canvas

    function onEnterSubmit(event: any) {
        if (isLocalhost) set_canvas(<Field size={1000}/>); return;

        event.preventDefault()
        const token = captchaRef.current!.getValue();
        captchaRef.current!.reset();

        fetch('/api/validate', {
                method: "POST",
                headers: {
                    'X-CSRFToken': getCookie("csrftoken")
                },
                body: JSON.stringify({
                    token: token
                })
            }
        ).then(
            res => res.json()
        ).then(
            data => {
                if (data["status"]) set_canvas(<Field size={1000}/>)
            }
        )
    }
}