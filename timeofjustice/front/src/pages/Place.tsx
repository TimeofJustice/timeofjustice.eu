import {useEffect, useRef, useState} from "react";
import {ReactZoomPanPinchRef, TransformComponent, TransformWrapper} from "react-zoom-pan-pinch"
import {isMobile} from 'react-device-detect'

export default function Place() {
    document.title = "Place - TimeofJustice";

    if (isMobile)
        return <div className={"place-field"}>
            Mobile devices are not supported. Due to performance issues.
            </div>

    const colors = [
        "#FF0000",
        "#FF7F00",
        "#FFFF00",
        "#00FF00",
        "#0000FF",
        "#4B0082",
        "#9400D3",
        "#FFFFFF",
        "#000000"
    ];
    const [cellColors, set_cellColors] = useState({} as { [key: string]: { [key: string]: string } })
    const cellColorsRef = useRef(cellColors);
    cellColorsRef.current = cellColors;
    const [knownColors] = useState({} as { [key: string]: { [key: string]: string } })
    const knownColorsRef = useRef(knownColors);
    knownColorsRef.current = knownColors;
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [activeCell, set_activeCell] = useState<number[]>([0, 0]);
    const activeCellRef = useRef(activeCell);
    activeCellRef.current = activeCell;
    const currentScale = useRef(0.0);
    const size = 1000;
    const cellSize = 10;
    const wrapperRef = useRef<ReactZoomPanPinchRef | null>(null);
    const [wrapperScale, set_wrapperScale] = useState(1.0);
    let currentScaleRef = useRef(wrapperScale);
    currentScaleRef.current = wrapperScale;

    const canvasClick = (e: any) => {
        const parent = canvasRef.current!.parentElement!;
        currentScale.current = parent.clientWidth / canvasRef.current!.width;

        const bounds = e.target.getBoundingClientRect();

        const x = Math.floor((e.clientX - bounds.left) / cellSize / currentScaleRef.current);
        const y = Math.floor((e.clientY - bounds.top) / cellSize / currentScaleRef.current);

        set_activeCell([x, y]);
    }

    const drawCell = (color: string) => {
        const x = activeCellRef.current[0];
        const y = activeCellRef.current[1];

        fetch(
            `/api/place/set?x=${x}&y=${y}&color=${color.replace("#", "")}`,
        ).then((response) => {
            if (response.status !== 200) {
                alert("Error: " + response.statusText);
                return;
            }

            const ctx = canvasRef.current!.getContext("2d");
            if (ctx) {
                ctx.fillStyle = color;
                ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
            }

            if (cellColorsRef.current[x] === undefined) {
                cellColorsRef.current[x] = {};
            }
            cellColorsRef.current[x][y] = color;

            // Check if we know this cell
            if (knownColorsRef.current[x] === undefined) {
                knownColorsRef.current[x] = {};
            }

            knownColorsRef.current[x][y] = color;
        })
    }

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

            set_cellColors(data);
            await draw(cellColorsRef.current);
        };

        const intervalId = setInterval(() => {
            dataFetch().then(async () => {});
        }, 5000)

        dataFetch().then(async () => {});

        return () => {
            clearInterval(intervalId);
        }
    }, []);

    useEffect(() => {
        const canvas = canvasRef.current;

        if (canvas) {
            canvas.width = size * cellSize;
            canvas.height = size * cellSize;
            draw(cellColorsRef.current);
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
            <div className={"colors"}>
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
        </div>
    </>

    function draw(cellList: { [key: string]: { [key: string]: string } }) {
        const canvas = canvasRef.current;

        if (!canvas || !cellList) {
            return;
        }

        const ctx = canvas.getContext("2d");

        if (!ctx) {
            return;
        }

        const widthInCells = canvas.width / cellSize;
        const heightInCells = canvas.height / cellSize;

        for (let i = 0; i < widthInCells; i++) {
            const cellRow = cellList[i];

            for (let j = 0; j < heightInCells; j++) {
                const cellColor = cellRow && cellRow[j];

                if (!cellColor) {
                    continue;
                }

                ctx.fillStyle = cellColor;
                ctx.fillRect(i * cellSize, j * cellSize, cellSize, cellSize);

                // Check if we know this cell
                if (knownColorsRef.current[i] === undefined) {
                    knownColorsRef.current[i] = {};
                }

                knownColorsRef.current[i][j] = cellColor;
            }
        }
    }
}