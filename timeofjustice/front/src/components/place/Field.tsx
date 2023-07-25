import {useEffect, useRef, useState} from "react"
import {ReactZoomPanPinchRef, TransformComponent, TransformWrapper} from "react-zoom-pan-pinch"
import {getCookie} from "../../helper/Cookie.tsx"

interface Colors {
    [key: string]: string
}

export default function Field({size}: { size: number }) {
    const colors: Colors = {
        "1": "#6D001A",
        "2": "#FF4500",
        "3": "#FFD635",
        "4": "#00A368",
        "5": "#7EED56",
        "6": "#009EAA",
        "7": "#2450A4",
        "8": "#51E9F4",
        "9": "#6A5CFF",
        "Q": "#811E9F",
        "W": "#E4ABFF",
        "E": "#FF3881",
        "R": "#6D482F",
        "T": "#FFB470",
        "Z": "#515252",
        "U": "#D4D7D9",
        "I": "#BE0039",
        "O": "#FFA800",
        "P": "#FFF8B8",
        "A": "#00CC78",
        "S": "#00756F",
        "D": "#00CCC0",
        "F": "#3690EA",
        "G": "#493AC1",
        "H": "#94B3FF",
        "J": "#B44AC0",
        "K": "#DE107F",
        "L": "#FF99AA",
        "Y": "#9C6926",
        "X": "#000000",
        "C": "#898D90",
        "V": "#FFFFFF"
    }

    const [activeCell, set_activeCell] = useState<number[]>([0, 0])
    const activeCellRef = useRef(activeCell)
    activeCellRef.current = activeCell

    const [wrapperScale, set_wrapperScale] = useState(1.0)
    let currentScaleRef = useRef(wrapperScale)
    currentScaleRef.current = wrapperScale

    const [drawTimeout, set_drawTimeout] = useState(0)
    const drawTimeoutRef = useRef(drawTimeout)
    drawTimeoutRef.current = drawTimeout

    const canvasRef = useRef<HTMLDivElement>(null)
    const wrapperRef = useRef<ReactZoomPanPinchRef>(null)

    const cellSize = 10

    useEffect(() => {
        const intervalId = setInterval(async () => {
            const images = canvasRef.current!.getElementsByTagName("img")

            for (let i = 0; i < images.length; i++) {
                const img = images[i]
                img.src = img.src + "?" + new Date().getTime()
            }
        }, 5000)

        const timeOutInterval = setInterval(() => {
            set_drawTimeout(drawTimeoutRef.current - 1)
        }, 1000)

        document.addEventListener("keydown", (e) => {
            handleHotkey(e)
        })

        return () => {
            clearInterval(intervalId)
            clearInterval(timeOutInterval)
        }
    }, [])

    return <>
        <div className={"place-field"}>
            <div className={"place-content"}>
                <TransformWrapper ref={wrapperRef}
                                  onZoom={(e) => {
                                      set_wrapperScale(e.state.scale)
                                  }}
                                  limitToBounds={false}
                                  doubleClick={{disabled: true}}
                                  minScale={0.05}
                                  maxScale={10}
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
                                 minWidth: size * cellSize + "px",
                                 minHeight: size * cellSize + "px",
                                 display: "grid",
                                 gridTemplateColumns: "repeat(10, 1000px)",
                                 gridTemplateRows: "repeat(10, 1000px)",
                             }}>

                            {Array.from({length: 4}, (_, i) =>
                                Array.from({length: 4}, (_, j) =>
                                    <img src={`/api/place/generate/${j * 250}/${i * 250}`}
                                         style={{
                                             width: 250 * cellSize + "px",
                                             height: 250 * cellSize + "px",
                                             imageRendering: "pixelated"
                                         }}
                                         key={`${j * 250}-${i * 250}`}
                                         id={`${j * 250}-${i * 250}`}
                                         alt={"This is a tile"}
                                    />))
                            }
                        </div>

                        <div className={"active-cell"} style={{
                            position: "absolute",
                            left: activeCell && canvasRef.current ? activeCell[0] * cellSize - 1 + "px" : "0",
                            top: activeCell && canvasRef.current ? activeCell[1] * cellSize - 1 + "px" : "0",
                            width: cellSize + 2 + "px",
                            height: cellSize + 2 + "px",
                        }}>
                            <div style={{
                                position: "absolute",
                                borderLeft: "1px solid #FFF",
                                borderTop: "1px solid #FFF",
                                width: cellSize / 2 + "px",
                                height: cellSize / 2 + "px",
                                left: 0 + "px",
                                top: 0 + "px",
                            }}></div>
                            <div style={{
                                position: "absolute",
                                borderRight: "1px solid #FFF",
                                borderTop: "1px solid #FFF",
                                width: cellSize / 2 + "px",
                                height: cellSize / 2 + "px",
                                right: 0 + "px",
                                top: 0 + "px",
                            }}></div>
                            <div style={{
                                position: "absolute",
                                borderLeft: "1px solid #FFF",
                                borderBottom: "1px solid #FFF",
                                width: cellSize / 2 + "px",
                                height: cellSize / 2 + "px",
                                left: 0 + "px",
                                bottom: 0 + "px",
                            }}></div>
                            <div style={{
                                position: "absolute",
                                borderRight: "1px solid #FFF",
                                borderBottom: "1px solid #FFF",
                                width: cellSize / 2 + "px",
                                height: cellSize / 2 + "px",
                                right: 0 + "px",
                                bottom: 0 + "px",
                            }}></div>
                            <div style={{
                                position: "absolute",
                                borderLeft: "1px solid #000",
                                borderTop: "1px solid #000",
                                width: cellSize / 2 - 2 + "px",
                                height: cellSize / 2 - 2 + "px",
                                left: 1 + "px",
                                top: 1 + "px",
                            }}></div>
                            <div style={{
                                position: "absolute",
                                borderRight: "1px solid #000",
                                borderTop: "1px solid #000",
                                width: cellSize / 2 - 2 + "px",
                                height: cellSize / 2 - 2 + "px",
                                right: 1 + "px",
                                top: 1 + "px",
                            }}></div>
                            <div style={{
                                position: "absolute",
                                borderLeft: "1px solid #000",
                                borderBottom: "1px solid #000",
                                width: cellSize / 2 - 2 + "px",
                                height: cellSize / 2 - 2 + "px",
                                left: 1 + "px",
                                bottom: 1 + "px",
                            }}></div>
                            <div style={{
                                position: "absolute",
                                borderRight: "1px solid #000",
                                borderBottom: "1px solid #000",
                                width: cellSize / 2 - 2 + "px",
                                height: cellSize / 2 - 2 + "px",
                                right: 1 + "px",
                                bottom: 1 + "px",
                            }}></div>
                        </div>
                    </TransformComponent>
                </TransformWrapper>
            </div>

            <div className={"reset-transform"}
                 onClick={() => {
                     wrapperRef.current!.resetTransform()
                 }}>
                <i className="fa-solid fa-rotate-left"></i>
            </div>
            <div className={
                "colors" + (drawTimeout > 0 ? "" : " ready")
            }>
                {Object.keys(colors).map((key) => {
                    return <div
                        className={"color"}
                        style={{backgroundColor: colors[key]}}
                        key={key}
                        onClick={() => {
                            drawCell(colors[key])
                        }}
                    >
                        <div>
                            {key}
                        </div>
                    </div>
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
        const bounds = e.target.getBoundingClientRect()

        const x = Math.floor((e.clientX - bounds.left) / cellSize / currentScaleRef.current)
        const y = Math.floor((e.clientY - bounds.top) / cellSize / currentScaleRef.current)

        set_activeCell([x, y])
    }

    function drawCell(color: string) {
        if (drawTimeoutRef.current > 0)
            return

        const x = activeCellRef.current[0]
        const y = activeCellRef.current[1]

        set_drawTimeout(3)

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
                return
            }

            const xArea = Math.floor(x / 250) * 250
            const yArea = Math.floor(y / 250) * 250

            const img = document.getElementById(`${xArea}-${yArea}`) as HTMLImageElement

            if (img) {
                img.src = img.src + "?" + new Date().getTime()
            }
        })
    }

    function handleHotkey(e: any) {
        let key = e.key.toString().toUpperCase()

        if (key === "ARROWLEFT") {
            set_activeCell([activeCellRef.current[0] - 1, activeCellRef.current[1]])
        } else if (key === "ARROWRIGHT") {
            set_activeCell([activeCellRef.current[0] + 1, activeCellRef.current[1]])
        } else if (key === "ARROWUP") {
            set_activeCell([activeCellRef.current[0], activeCellRef.current[1] - 1])
        } else if (key === "ARROWDOWN") {
            set_activeCell([activeCellRef.current[0], activeCellRef.current[1] + 1])
        }

        if (colors[key])
            drawCell(colors[key])
    }
}