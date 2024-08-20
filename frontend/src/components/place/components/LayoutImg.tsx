import React from "react";
import {OverlayImage} from "../../../data/OverlayImage.tsx";
import {handleClickCapture, mouseDownCapture} from "../../../helper/MouseHelper.tsx";

export default function LayoutImg({overlayImages, i, cellSize, onImageClick}:
{
    overlayImages: OverlayImage[],
    i: number,
    cellSize: number,
    onImageClick: (e: React.MouseEvent<HTMLImageElement>) => void
}) {
    return <img src={overlayImages[i]['url']}
                id={`overlayImg_${i}`}
                style={{
                    top: overlayImages[i]['y'] * cellSize + 'px',
                    left: overlayImages[i]['x'] * cellSize + 'px',
                    width: overlayImages[i]['width'] * cellSize + 'px',
                    height: overlayImages[i]['height'] * cellSize + 'px'
                }}
                className={"overlay-image"}
                onClick={onImageClick}
                onMouseDownCapture={mouseDownCapture}
                onClickCapture={handleClickCapture}
                alt={"Overlay-Image"}
    />
}