import React, {forwardRef} from "react";
import LayoutColors from "./LayoutColors.tsx";


export const LayoutOverlay = forwardRef(function Cursor(props: {
    onFocus: () => void,
    onBlur: () => void,
    onClick: (color: string) => void,
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void,
    activeOverlay: string,
    colors: string[]
}, ref: React.ForwardedRef<HTMLInputElement>) {
    const {onFocus, onBlur, activeOverlay, onChange, colors, onClick} = props;

    return <div className={"layout-container"}>
        {colors.length != 0 ?
            <div className={"layout-colors"}>
                <LayoutColors colors={colors} onClick={onClick}/>
            </div> :
            <></>
        }

        <div className={"layout-input"}>
            <input type={"text"}
                   onFocus={onFocus}
                   onBlur={onBlur}
                   value={activeOverlay}
                   onChange={onChange}
                   placeholder={"Overlay..."}
                   ref={ref}
            />
        </div>
    </div>
});