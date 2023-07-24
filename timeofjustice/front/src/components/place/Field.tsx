import {useEffect, useRef, useState} from "react";
import {ReactZoomPanPinchRef, TransformComponent, TransformWrapper} from "react-zoom-pan-pinch";
import {getCookie} from "../../helper/Cookie.tsx";
import {timeout} from "../../helper/Timeout.tsx";

export default function Field() {
    const colors = [
        "#FF4500",
        "#FFA800",
        "#FFD635",
        "#00A368",
        "#7EED56",
        "#2450A4",
        "#3690EA",
        "#51E9F4",
        "#811E9F",
        "#B44AC0",
        "#FF99AA",
        "#9C6926",
        "#000000",
        "#898D90",
        "#D4D7D9",
        "#FFFFFF",
    ]

    const [activeCell, set_activeCell] = useState<number[]>([0, 0]);
    const activeCellRef = useRef(activeCell);
    activeCellRef.current = activeCell;

    const [wrapperScale, set_wrapperScale] = useState(1.0);
    let currentScaleRef = useRef(wrapperScale);
    currentScaleRef.current = wrapperScale;

    const [drawTimeout, set_drawTimeout] = useState(0);
    const drawTimeoutRef = useRef(drawTimeout);
    drawTimeoutRef.current = drawTimeout;

    const canvasRef = useRef<HTMLDivElement>(null);
    const wrapperRef = useRef<ReactZoomPanPinchRef | null>(null);

    const currentScale = useRef(0.0);
    const cellSize = 10;

    useEffect(() => {
        const intervalId = setInterval(async () => {
            const images = canvasRef.current!.getElementsByTagName("img");

            for (let i = 0; i < images.length; i++) {
                const img = images[i];
                img.src = img.src;

                await timeout(100)
            }
        }, 10000)

        const timeOutInterval = setInterval(() => {
            set_drawTimeout(drawTimeoutRef.current - 1)
        }, 1000);

        return () => {
            clearInterval(intervalId);
            clearInterval(timeOutInterval);
        }
    }, []);

    useEffect(() => {
        const wrapper = wrapperRef.current;
        if (wrapper && wrapper.state) {
            set_wrapperScale(wrapper.state.scale);
        }
    }, [wrapperRef])


    return <>
        <div className={"place-field"}>
            <div className={"place-content"}>
                <TransformWrapper ref={wrapperRef}
                                  onZoom={(e) => {
                                      set_wrapperScale(e.state.scale);
                                  }}
                                  limitToBounds={false}
                                  doubleClick={{disabled: true}}
                                  centerOnInit={true}
                                  minScale={0.1}
                >
                    <TransformComponent
                        wrapperStyle={{
                            width: "100%",
                            height: "100%",
                        }}
                        contentStyle={{
                            width: "100%",
                            height: "100%",
                        }}
                        wrapperClass={"field-wrapper"}
                    >
                        <div className={"field"}
                             ref={canvasRef}
                             onClick={canvasClick}
                             style={{
                                 minWidth: 10000 + "px",
                                 minHeight: 10000 + "px",
                                 display: "grid",
                                 gridTemplateColumns: "repeat(10, 1000px)",
                                    gridTemplateRows: "repeat(10, 1000px)",
                             }}>

                            {Array.from({ length: 4 }, (_, i) =>
                                Array.from({ length: 4 }, (_, j) =>
                                <img src={`http://localhost/api/place/generate/${j * 250}/${i * 250}`}
                                     style={{
                                         width: 2500 + "px",
                                         height: 2500 + "px",
                                         imageRendering: "pixelated"
                                     }}
                                     key={`${j * 250}-${i * 250}`}
                                     id={`${j * 250}-${i * 250}`}
                                />))
                            }
                        </div>

                        <div className={"active-cell"} style={{
                            position: "absolute",
                            left: activeCell && canvasRef.current ? activeCell[0] * cellSize + "px" : "0",
                            top: activeCell && canvasRef.current ? activeCell[1] * cellSize + "px" : "0",
                            width: cellSize + "px",
                            height: cellSize + "px",
                        }}>
                            <div style={{
                                position: "absolute",
                                borderLeft: "1px solid #FFF",
                                borderTop: "1px solid #FFF",
                                width: cellSize / 2 + "px",
                                height: cellSize / 2 + "px",
                                left: -1 + "px",
                                top: -1 + "px",
                            }}></div>
                            <div style={{
                                position: "absolute",
                                borderRight: "1px solid #FFF",
                                borderTop: "1px solid #FFF",
                                width: cellSize / 2 + "px",
                                height: cellSize / 2 + "px",
                                right: -1 + "px",
                                top: -1 + "px",
                            }}></div>
                            <div style={{
                                position: "absolute",
                                borderLeft: "1px solid #FFF",
                                borderBottom: "1px solid #FFF",
                                width: cellSize / 2 + "px",
                                height: cellSize / 2 + "px",
                                left: -1 + "px",
                                bottom: -1 + "px",
                            }}></div>
                            <div style={{
                                position: "absolute",
                                borderRight: "1px solid #FFF",
                                borderBottom: "1px solid #FFF",
                                width: cellSize / 2 + "px",
                                height: cellSize / 2 + "px",
                                right: -1 + "px",
                                bottom: -1 + "px",
                            }}></div>
                            <div style={{
                                    position: "absolute",
                                    borderLeft: "1px solid #000",
                                    borderTop: "1px solid #000",
                                    width: cellSize / 2 - 2 + "px",
                                    height: cellSize / 2 - 2 + "px",
                                    left: 0 + "px",
                                    top: 0 + "px",
                                }}></div>
                            <div style={{
                                position: "absolute",
                                borderRight: "1px solid #000",
                                borderTop: "1px solid #000",
                                width: cellSize / 2 - 2 + "px",
                                height: cellSize / 2 - 2 + "px",
                                right: 0 + "px",
                                top: 0 + "px",
                            }}></div>
                            <div style={{
                                position: "absolute",
                                borderLeft: "1px solid #000",
                                borderBottom: "1px solid #000",
                                width: cellSize / 2 - 2 + "px",
                                height: cellSize / 2 - 2 + "px",
                                left: 0 + "px",
                                bottom: 0 + "px",
                            }}></div>
                            <div style={{
                                position: "absolute",
                                borderRight: "1px solid #000",
                                borderBottom: "1px solid #000",
                                width: cellSize / 2 - 2 + "px",
                                height: cellSize / 2 - 2 + "px",
                                right: 0 + "px",
                                bottom: 0 + "px",
                            }}></div>
                        </div>
                    </TransformComponent>
                </TransformWrapper>
            </div>
            <div className={
                "colors" + (drawTimeout > 0 ? "" : " ready")
            }>
                {colors.map((c, i) => {
                    return <div
                        className={"color"}
                        style={{backgroundColor: c}}
                        key={i}
                        onClick={() => {
                            drawCell(c);
                        }}
                    ></div>
                })}
            </div>
            <div className={"cords"}>
                <span>x: {activeCell && canvasRef.current ? activeCell[0] : 0}, </span>
                <span>y: {activeCell && canvasRef.current ? activeCell[1] : 0}</span>
            </div>
            <div className={"timer"} style={
                {display: drawTimeout > 0 ? "block" : "none"}
            }>
                {drawTimeout > 0 ? drawTimeout + " seconds" : ""}
            </div>
        </div>
    </>


    function canvasClick(e: any) {
        const parent = canvasRef.current!.parentElement!;
        currentScale.current = parent.clientWidth / canvasRef.current!.clientWidth;

        const bounds = e.target.getBoundingClientRect();

        const x = Math.floor((e.clientX - bounds.left) / cellSize / currentScaleRef.current);
        const y = Math.floor((e.clientY - bounds.top) / cellSize / currentScaleRef.current);

        set_activeCell([x, y]);
    }

    function drawCell(color: string) {
        const x = activeCellRef.current[0];
        const y = activeCellRef.current[1];

        drawTimeoutRef.current = 3;

        fetch(
            `/api/place/set`,
            {
                method: "POST",
                headers: {
                    'X-CSRFToken': getCookie("csrftoken")
                },
                body: JSON.stringify({
                    color: color.replace("#", ""),
                    x: x,
                    y: y
                })
            }
        ).then((response) => {
            if (response.status !== 200) {
                return;
            }

            const xArea = Math.floor(x / 250) * 250;
            const yArea = Math.floor(y / 250) * 250;

            const img = document.getElementById(`${xArea}-${yArea}`) as HTMLImageElement;

            if (img) {
                img.src = img.src;
            }
        })
    }
}