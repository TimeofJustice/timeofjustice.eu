const data = document.currentScript.dataset;
let currentMode = getCookie("mode") ? getCookie("mode") : "dark";

function changeMode() {
    const stylingElement = document.getElementById("styling");
    const modeButton = document.getElementById("modeButton");

    if (currentMode === "dark") {
        stylingElement.href = data.lightcss;

        setCookie("mode", "light");

        setTimeout(function () {
            modeButton.getElementsByTagName("i")[0].classList.add("fa-sun");
            modeButton.getElementsByTagName("i")[0].classList.remove("fa-moon");
        }, 125);

        currentMode = "light";
    } else {
        stylingElement.href = data.darkcss;

        setCookie("mode", "dark");

        setTimeout(function () {
            modeButton.getElementsByTagName("i")[0].classList.add("fa-moon");
            modeButton.getElementsByTagName("i")[0].classList.remove("fa-sun");
        }, 125);

        currentMode = "dark";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const stylingElement = document.getElementById("styling");
    const modeButton = document.getElementById("modeButton");

    if (getCookie("mode") === "light") {
        stylingElement.href = data.lightcss;

        modeButton.getElementsByTagName("i")[0].classList.add("fa-sun");
        modeButton.getElementsByTagName("i")[0].classList.remove("fa-moon");
    } else {
        stylingElement.href = data.darkcss;

        modeButton.getElementsByTagName("i")[0].classList.add("fa-moon");
        modeButton.getElementsByTagName("i")[0].classList.remove("fa-sun");
    }
});