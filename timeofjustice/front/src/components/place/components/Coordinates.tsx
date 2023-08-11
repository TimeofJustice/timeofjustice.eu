import {CellData} from "../../../data/CellData.tsx";

export default function Coordinates({activeCell, cellColor, onClick}: {
    activeCell: number[],
    cellColor: CellData,
    onClick: () => void
}) {
    return <div className={'cords'}>
        <span>x: {activeCell ? activeCell[0] : 0}, </span>
        <span>y: {activeCell ? activeCell[1] : 0}</span><br/>
        {cellColor ?
            <div
                className={"cell-color"}
                onClick={onClick}
            >{cellColor.color}
                <div style={{
                    backgroundColor: cellColor.color
                }}></div>
            </div> : <div>Loading...</div>}
    </div>
}