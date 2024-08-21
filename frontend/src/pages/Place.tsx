import Field from "../components/place/Field.tsx";
import "../assets/css/Field.css";
import {useRef, useState} from "react";
import ReCAPTCHA from "react-google-recaptcha";
import {getCookie} from "../helper/Cookie.tsx";

export default function Place() {
    document.title = "Place - TimeofJustice";

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
                    sitekey={process.env.REACT_APP_RECAPTCHA_SITE_KEY}
                    size="invisible"
                    ref={captchaRef}
                    onChange={onCaptchaChange}
                    badge="bottomright"
                />
                <div className={"place-button"} onClick={onClickEnter}>
                    Enter
                </div>
            </div>
        </div>
    );

    return canvas

    function onClickEnter() {
        captchaRef.current!.execute()
    }

    function onCaptchaChange() {
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