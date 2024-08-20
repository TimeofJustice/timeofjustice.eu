import DarkModeSwitch from "../projects/DarkModeSwitch.tsx";
import {NavLink} from "react-router-dom";

export default function Navbar() {
    return <div className="header-container">
        <nav className="header">
            <div className="left-side">
                <i className="fas fa-code"></i>
                <span>TimeofJustice</span>
                <PageLink to="/">/Projects</PageLink>
                <PageLink to="/place">/Place</PageLink>
                <PageLink to="/privacy">/Privacy Policy</PageLink>
                <a href="/legal" className="legal-link">/Legal Notice</a>
            </div>

            <div className="right-side">
                <div className="socials">
                    <a href="https://github.com/TimeofJustice" target="_blank">
                        <i className="fa-brands fa-github"></i>
                    </a>
                    <a href="https://instagram.com/jonas.oel" target="_blank">
                        <i className="fa-brands fa-instagram"></i>
                    </a>
                    <a href="https://linkedin.com/in/jonas-oelschner-2569441b3" target="_blank">
                        <i className="fa-brands fa-linkedin"></i>
                    </a>
                    <a href="https://twitter.com/timeofjustice_" target="_blank">
                        <i className="fa-brands fa-twitter"></i>
                    </a>
                </div>
                <div className="functions">
                    <DarkModeSwitch/>
                </div>
            </div>
        </nav>
    </div>

    function PageLink({to, children = ""}: { to: string, children: string }) {
        return <>
            <NavLink to={to}>{children}</NavLink>
        </>
    }
}