import React, {forwardRef} from "react";


export const Cursor = forwardRef(function Cursor(props: {
    activeCell: number[],
    cellSize: number
}, ref: React.ForwardedRef<HTMLImageElement>) {
    const {activeCell, cellSize} = props;

    return <img src={"/images/Cursor.png"}
                className={'active-cell'}
                ref={ref}
                style={{
                    left: activeCell[0] * cellSize - 1 + 'px',
                    top: activeCell[1] * cellSize - 1 + 'px',
                    width: cellSize + 2 + 'px',
                    height: cellSize + 2 + 'px',
                    imageRendering: "pixelated"
                }}
    />
});

export function ExportField({exportCorners, cellSize}: {
    exportCorners: [number[], number[]],
    cellSize: number
}) {
    return <>
        {exportCorners[0].length != 0 && exportCorners[1].length != 0 ?
            <div
                style={{
                    left: exportCorners[0][0] * cellSize - 1 + 'px',
                    top: exportCorners[0][1] * cellSize - 1 + 'px',
                    width: cellSize * (exportCorners[1][0] - exportCorners[0][0] + 1) + 2 + 'px',
                    height: cellSize * (exportCorners[1][1] - exportCorners[0][1] + 1) + 2 + 'px'
                }}
                className={"export-area"}
            >
                <a
                    href={`/api/place/export/${exportCorners[0][0]}/${exportCorners[0][1]}/${exportCorners[1][0]}/${exportCorners[1][1]}/10`}
                    target={"_blank"}
                >
                    Export...
                </a>
            </div>
            : <></>
        }

        {exportCorners[0].length != 0 ?
            <img src={"/images/ExportLeft.png"}
                 className={'active-cell'}
                 style={{
                     left: exportCorners[0][0] * cellSize - 1 + 'px',
                     top: exportCorners[0][1] * cellSize - 1 + 'px',
                     width: cellSize + 2 + 'px',
                     height: cellSize + 2 + 'px',
                     imageRendering: "pixelated"
                 }}
            /> : <></>
        }

        {exportCorners[1].length != 0 ?
            <img src={"/images/ExportRight.png"}
                 className={'active-cell'}
                 style={{
                     left: exportCorners[1][0] * cellSize - 1 + 'px',
                     top: exportCorners[1][1] * cellSize - 1 + 'px',
                     width: cellSize + 2 + 'px',
                     height: cellSize + 2 + 'px',
                     imageRendering: "pixelated"
                 }}
            /> : <></>
        }
    </>
}