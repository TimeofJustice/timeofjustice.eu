import React from "react";

let mouseDownX = 0;
let mouseDownY = 0;

export const mouseDownCapture = (e: React.MouseEvent<any>) => {
    mouseDownX = e.clientX;
    mouseDownY = e.clientY;
};

export const handleClickCapture = (e: React.MouseEvent<any>) => {
    if (
        Math.abs(mouseDownX - e.clientX) >= 30 ||
        Math.abs(mouseDownY - e.clientY) >= 30
    ) {
        e.stopPropagation();
    }
};