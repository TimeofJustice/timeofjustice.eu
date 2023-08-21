import {useState} from "react";

export default function LayoutColors({colors, onClick}: {colors: string[], onClick: (color: string) => void}) {
    const [selectedColor, set_selectedColor] = useState("")

    return <div>
        {Array.from({length: colors.length}, (_, i) => {
                const color = colors[i]

                return <div onClick={() => {
                    onClick(color)
                    set_selectedColor(color)
                }}>
                    <div className={"layout-color"} style={{
                        backgroundColor: color
                    }}></div>
                    <div
                        className={"layout-color-text"}
                        style={color == selectedColor ? {textDecoration: "underline"}: {}}
                    >
                        {color.toUpperCase()}
                    </div>
                    <i className="fa-solid fa-eye-dropper"></i>
                </div>
            }
        )}
    </div>
}