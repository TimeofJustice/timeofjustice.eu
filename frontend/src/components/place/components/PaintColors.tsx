import {Colors} from "../../../data/Colors.tsx";

export default function PaintColors({colors, onColorClick}: { colors: Colors, onColorClick: (color: string) => void }) {
    return <div className={'colors'}>
        {Object.keys(colors).map((key) => {
            return <div
                className={'color'}
                style={{backgroundColor: colors[key]}}
                key={key}
                onClick={() => onColorClick(colors[key])}
            >
                <div>
                    {key}
                </div>
            </div>
        })}
    </div>
}