import {useEffect, useRef, useState} from "react";
import {ReactZoomPanPinchRef, TransformComponent, TransformWrapper} from "react-zoom-pan-pinch";
import {getCookie} from "../../helper/Cookie.tsx";

export default function Field({size}: { size: number }) {
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

    const [currentColors, set_currentColors] = useState({} as { [key: string]: { [key: string]: string } })
    const currentColorsRef = useRef(currentColors);
    currentColorsRef.current = currentColors;

    const [knownColors] = useState({} as { [key: string]: { [key: string]: string } })
    const knownColorsRef = useRef(knownColors);
    knownColorsRef.current = knownColors;

    const [activeCell, set_activeCell] = useState<number[]>([0, 0]);
    const activeCellRef = useRef(activeCell);
    activeCellRef.current = activeCell;

    const [wrapperScale, set_wrapperScale] = useState(1.0);
    let currentScaleRef = useRef(wrapperScale);
    currentScaleRef.current = wrapperScale;

    const [drawTimeout, set_drawTimeout] = useState(0);
    const drawTimeoutRef = useRef(drawTimeout);
    drawTimeoutRef.current = drawTimeout;

    const canvasRef = useRef<HTMLCanvasElement>(null);
    const wrapperRef = useRef<ReactZoomPanPinchRef | null>(null);

    const currentScale = useRef(0.0);
    const cellSize = 10;

    useEffect(() => {
        const dataFetch = async () => {
            const data = await (
                await fetch("/api/place/get", {
                    headers: {'X-CURRENT-CELLS':
                            JSON.stringify({
                                cellColors: knownColorsRef.current,
                            })
                    }
                })
            ).json();

            set_currentColors(data);
        };

        const intervalId = setInterval(() => {
            dataFetch().then(async () => {});
        }, 5000)

        dataFetch().then(async () => {});

        const timeOutInterval = setInterval(() => {
            set_drawTimeout(drawTimeoutRef.current - 1)
        }, 1000);

        return () => {
            clearInterval(intervalId);
            clearInterval(timeOutInterval);
        }
    }, []);

    useEffect(() => {
        draw(currentColorsRef.current)
    }, [currentColors])

    useEffect(() => {
        const canvas = canvasRef.current;

        if (canvas) {
            canvas.width = size * cellSize;
            canvas.height = size * cellSize;
            draw(currentColorsRef.current);
        }
    }, [canvasRef])

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
                        <canvas
                            ref={canvasRef} className={"field"}
                            onClick={canvasClick}
                            style={{
                                width: size * cellSize + "px!important",
                                height: size * cellSize + "px!important",
                            }}
                        ></canvas>

                        <div className={"active-cell"} style={{
                            position: "absolute",
                            left: activeCell && canvasRef.current ? activeCell[0] * cellSize + "px" : "0",
                            top: activeCell && canvasRef.current ? activeCell[1] * cellSize + "px" : "0",
                            border: "0.1px solid #000",
                            width: cellSize + "px",
                            height: cellSize + "px",
                        }}>
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
        currentScale.current = parent.clientWidth / canvasRef.current!.width;

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

            const ctx = canvasRef.current!.getContext("2d");
            if (ctx) {
                ctx.fillStyle = color;
                ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
            }

            if (currentColorsRef.current[x] === undefined) {
                currentColorsRef.current[x] = {};
            }
            currentColorsRef.current[x][y] = color;

            if (knownColorsRef.current[x] === undefined) {
                knownColorsRef.current[x] = {};
            }

            knownColorsRef.current[x][y] = color;
        })
    }

    function draw(cellList: { [key: string]: { [key: string]: string } }) {
        const canvas = canvasRef.current;

        if (!canvas || !cellList) {
            return;
        }

        const ctx = canvas.getContext("2d");

        if (!ctx) {
            return;
        }

        for (let rowIndex in cellList) {
            let row = cellList[rowIndex];

            for (let cellIndex in row) {
                let cellColor = row[cellIndex];

                if (!cellColor) {
                    continue;
                }

                ctx.fillStyle = cellColor;
                ctx.fillRect(parseInt(rowIndex) * cellSize, parseInt(cellIndex) * cellSize, cellSize, cellSize);

                if (knownColorsRef.current[rowIndex] === undefined) {
                    knownColorsRef.current[rowIndex] = {};
                }

                knownColorsRef.current[rowIndex][cellIndex] = cellColor;
            }
        }
    }
}