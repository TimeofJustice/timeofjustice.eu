import {useEffect, useRef, useState} from "react";

export default function Place() {
    document.title = "Place - TimeofJustice";

    const [color, set_color] = useState("#FF0000");
    const colorRef = useRef(color);
    colorRef.current = color;
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

    useEffect(() => {
        const dataFetch = async () => {
            const data = await (
                await fetch("/api/place/get")
            ).json();

            set_cellColors(data);
            draw();
        };

        setInterval(() => {
            dataFetch().then(() => {
            });
        }, 2000)
        dataFetch().then(() => {
        });
    }, []);

    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [activeCell, set_activeCell] = useState<number[]>([0, 0]);
    const currentScale = useRef(0.0);

    useEffect(() => {
        const canvas = canvasRef.current;

        if (canvas) {
            draw();
        }
    }, [canvasRef])

    function draw() {
        const canvas = canvasRef.current!;
        const ctx = canvas.getContext("2d")!;
        const cellList = cellColorsRef.current

        for (let i = 0; i < 100; i++) {
            for (let j = 0; j < 100; j++) {
                if (cellList != undefined && i in cellList && cellList[i] != undefined && j in cellList[i]) {
                    ctx.fillStyle = cellList[i][j];
                } else {
                    ctx.fillStyle = "#FFF";
                }
                ctx.fillRect(i, j, 1, 1);
            }
        }
    }

    const canvasClick = (e: any) => {
        const parent = canvasRef.current!.parentElement!;
        const scale = parent.clientWidth / canvasRef.current!.width;
        currentScale.current = scale;

        var bounds = e.target.getBoundingClientRect();

        const x = Math.floor((e.clientX - bounds.left) / scale);
        const y = Math.floor((e.clientY - bounds.top) / scale);

        set_activeCell([x, y]);

        fetch(
            `/api/place/set?x=${x}&y=${y}&color=${colorRef.current.replace("#", "")}`,
        ).then((response) => {
            if (response.status !== 200) {
                alert("Error: " + response.statusText);
                return;
            }

            if (cellColorsRef.current[x] === undefined) {
                cellColorsRef.current[x] = {};
            }
            cellColorsRef.current[x][y] = colorRef.current;
            draw();
        })
    }

    return <>
        <div className={"place-field"}>
            <div className={"place-content"}>
                <canvas
                    width={"100"} height={"100"} ref={canvasRef} className={"field"}
                    onClick={canvasClick}
                ></canvas>
                <div className={"active-cell"} style={{
                    position: "absolute",
                    left: activeCell && canvasRef.current ? activeCell[0] * currentScale.current + "px" : "0",
                    top: activeCell && canvasRef.current ? activeCell[1] * currentScale.current + "px" : "0",
                    border: "1px solid #000",
                    width: currentScale.current + "px",
                    height: currentScale.current + "px",
                }}>
                </div>
            </div>
            <div className={"colors"}>
                {colors.map((c, i) => {
                    return <div
                        className={"color" + (color === c ? " active" : "")}
                        style={{backgroundColor: c}}
                        key={i}
                        onClick={() => {
                            set_color(c);
                        }}
                    ></div>
                })}
            </div>
        </div>
    </>
}