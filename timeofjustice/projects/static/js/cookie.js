const standardCookieExpiry = 30;

function setCookie(cname, cvalue, exdays = standardCookieExpiry, isConsent = false) {
    if (getCookie("cookie_consent") !== "true" && !isConsent) return;

    const d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    let expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function onAccept() {
    setCookie("cookie_consent", "true", standardCookieExpiry, true);
    const cookieBannerElement = document.getElementsByClassName("cookie-banner")[0];
    cookieBannerElement.style.bottom = "-200px";
}

function onDecline() {
    const cookieBannerElement = document.getElementsByClassName("cookie-banner")[0];
    cookieBannerElement.style.bottom = "-200px";
}

document.addEventListener("DOMContentLoaded", function () {
    const cookieBannerElement = document.getElementsByClassName("cookie-banner")[0];
    const cookieConsent = getCookie("cookie_consent");

    if (cookieConsent === "true") {
        cookieBannerElement.style.bottom = "-200px";
    } else {
        cookieBannerElement.style.bottom = "10px";
    }
});