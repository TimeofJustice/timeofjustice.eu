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

    return <div className={'overlay-input'}>
        <input type={"text"}
               onFocus={onFocus}
               onBlur={onBlur}
               value={activeOverlay}
               onChange={onChange}
               placeholder={"Overlay..."}
               ref={ref}
        />

        <LayoutColors colors={colors} onClick={onClick}/>
    </div>
});