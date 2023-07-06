let maxImg = 3;
let currentImg = 0;

function changeImage(changer, isTouch = true) {
    let newImg = (currentImg + changer + maxImg) % maxImg;

    const imagesElement = document.getElementById("images");
    const imageElements = imagesElement.getElementsByTagName("img");
    const currentImgElement = imageElements[currentImg];
    const newImgElement = imageElements[newImg];

    const dotsElement = document.getElementById("dots");
    const currentDotElement = dotsElement.getElementsByTagName("i")[currentImg];
    const newDotElement = dotsElement.getElementsByTagName("i")[newImg];

    if (newImg === currentImg) {
        return;
    }

    if (changer < 0) {
        newImgElement.style.transition = "none";
        newImgElement.style.left = "-100%";

        setTimeout(() => {
            currentImgElement.style.transition = "";
            newImgElement.style.transition = "";

            currentImgElement.style.left = "100%";
            newImgElement.style.left = "0";
        }, 10);
    } else {
        newImgElement.style.transition = "none";
        newImgElement.style.left = "100%";

        setTimeout(() => {
            currentImgElement.style.transition = "";
            newImgElement.style.transition = "";

            currentImgElement.style.left = "-100%";
            newImgElement.style.left = "0";
        }, 10);
    }

    newDotElement.classList.add("active");
    currentDotElement.classList.remove("active");

    currentImg = newImg;

    if (isTouch) lastTouchX = new Date().getTime();
}

function changeImageTo(newImg) {
    if (newImg === currentImg) {
        return;
    }

    changeImage(newImg - currentImg);
}

function loadProject(projectId) {
    jQuery.get("/project/" + projectId, function(data) {
        const images = data.images;
        maxImg = images.length;

        const imagesElement = document.getElementById("images");
        const dotsElement = document.getElementById("dots");

        imagesElement.innerHTML = "";
        dotsElement.innerHTML = "";

        for (let i = 0; i < maxImg; i++) {
            const image = images[i];

            const imageElement = document.createElement("img");
            imageElement.src = image;
            imageElement.classList.add("image");
            if (i === 0) imageElement.style.left = "0";

            imagesElement.appendChild(imageElement);

            const dotElement = document.createElement("i");
            dotElement.classList.add("fa");
            dotElement.classList.add("fa-circle");
            if (i === 0) dotElement.classList.add("active");

            dotElement.onclick = () => changeImageTo(i);
            dotsElement.appendChild(dotElement);
        }
    });
}

let lastTouchX = 0;

document.addEventListener("DOMContentLoaded", function() {
    const imagesElement = document.getElementById("images");
    const dotsElement = document.getElementById("dots");

    loadProject(0);

    setInterval(() => {
        if (30000 < new Date().getTime() - lastTouchX) {
            changeImage(1, false);
        }
    }, 5000);
});
