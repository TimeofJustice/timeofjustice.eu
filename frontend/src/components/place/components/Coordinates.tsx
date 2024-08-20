import {CellData} from "../../../data/CellData.tsx";

export default function Coordinates({activeCell, cellColor, onClick}: {
    activeCell: number[],
    cellColor: CellData,
    onClick: () => void
}) {
    return <div className={"pixel-stats"}>
        <span>X: {activeCell ? activeCell[0] : 0}, Y: {activeCell ? activeCell[1] : 0}</span>
        {cellColor ?
            <div
                className={"cell-color"}
                onClick={onClick}
            >
                <div style={{
                    backgroundColor: cellColor.color
                }}></div>
                {cellColor.color.toUpperCase()}
                <i className="fa-solid fa-eye-dropper"></i>
            </div> : <div>Loading...</div>}
    </div>
}