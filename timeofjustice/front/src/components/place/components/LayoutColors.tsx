export default function LayoutColors({colors, onClick}: {colors: string[], onClick: (color: string) => void}) {
    return <div className={"overlay-colors"}>
        {Array.from({length: colors.length}, (_, i) => {
                const color = colors[i]

                return <div onClick={() => onClick(color)}>
                    {color.toUpperCase()}
                    <div style={{backgroundColor: color}}></div>
                </div>
            }
        )}
    </div>
}