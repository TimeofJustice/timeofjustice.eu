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
    const [cellColors, set_cellColors] = useState([])

    useEffect(() => {
        const dataFetch = async () => {
            const data = await (
                await fetch("/api/place/get")
            ).json();

            set_cellColors(data);
        };

        setInterval(() => {
            dataFetch().then(() => {
            });
        }, 2000)
        dataFetch().then(() => {
        });
    }, []);

    return <>
        <div className={"place-field"}>
            <div className={"place-content"}>
                <div
                    className="field"
                    style={{
                        gridTemplateColumns: "repeat(100, 1%)",
                        gridTemplateRows: "repeat(100, auto)"
                    }}
                >
                    {Array.from(Array(100 * 100).keys()).map((_, i) => {
                        return <div
                            className="place-cell"
                            key={i}
                            style={cellColors[i] ? {backgroundColor: cellColors[i]} : {backgroundColor: "#FFFFFF"}}
                            onClick={(e) => {
                                (e.target as HTMLDivElement).style.backgroundColor = colorRef.current;

                                fetch(
                                    `/api/place/set?id=${i}&color=${colorRef.current.replace("#", "")}`,
                                ).then((response) => {
                                    console.log(response);
                                })
                            }}>
                        </div>
                    })}
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