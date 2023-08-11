import React, {forwardRef} from "react";


export const Cursor = forwardRef(function Cursor(props: {
    activeCell: number[],
    cellSize: number
}, ref: React.ForwardedRef<HTMLDivElement>) {
    const {activeCell, cellSize} = props;

    return <div className={'active-cell'}
                ref={ref}
                style={{
                    left: activeCell[0] * cellSize - 1 + 'px',
                    top: activeCell[1] * cellSize - 1 + 'px',
                    width: cellSize + 2 + 'px',
                    height: cellSize + 2 + 'px',
                }}>
        <div style={{
            width: cellSize / 2 + 'px',
            height: cellSize / 2 + 'px'
        }}></div>
        <div style={{
            width: cellSize / 2 + 'px',
            height: cellSize / 2 + 'px'
        }}></div>
        <div style={{
            width: cellSize / 2 + 'px',
            height: cellSize / 2 + 'px'
        }}></div>
        <div style={{
            width: cellSize / 2 + 'px',
            height: cellSize / 2 + 'px',
        }}></div>
        <div style={{
            width: cellSize / 2 - 2 + 'px',
            height: cellSize / 2 - 2 + 'px'
        }}></div>
        <div style={{
            width: cellSize / 2 - 2 + 'px',
            height: cellSize / 2 - 2 + 'px'
        }}></div>
        <div style={{
            width: cellSize / 2 - 2 + 'px',
            height: cellSize / 2 - 2 + 'px'
        }}></div>
        <div style={{
            width: cellSize / 2 - 2 + 'px',
            height: cellSize / 2 - 2 + 'px',
        }}></div>
    </div>
});