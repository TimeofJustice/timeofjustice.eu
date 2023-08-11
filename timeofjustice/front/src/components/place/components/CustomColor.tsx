import {ChromePicker, ColorResult} from "react-color";
import React from 'react'

export default function CustomColor(
    {customColor, customColorKey, displayColorPicker, onCustomColorClick, onCustomColorPickerClick, onPickerChange}:
        {
            customColor: string,
            customColorKey: string,
            displayColorPicker: boolean,
            onCustomColorClick: (e: React.MouseEvent<HTMLDivElement>) => void,
            onCustomColorPickerClick: (e: React.MouseEvent<HTMLDivElement>) => void,
            onPickerChange: (e: ColorResult) => void
        }) {
    return <div className={'color-picker-container'}>
        <div className={'color-picker'}
             style={{backgroundColor: customColor}}
             onClick={onCustomColorClick}
             id={'color_picker'}
        >
            <div className={'hotkey'}>
                {customColorKey}
            </div>

            <div className={'color-picker-button'} onClick={onCustomColorPickerClick}>
                <i className="fa-solid fa-palette"></i>
            </div>
        </div>

        {displayColorPicker ? <div className={"custom-color-picker"}>
            <div className={"outer"} onClick={onCustomColorPickerClick}/>

            <ChromePicker
                color={customColor}
                onChange={onPickerChange}
                disableAlpha={true}
            />
        </div> : null}
    </div>
}