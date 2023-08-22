import React, {useEffect, useRef, useState} from 'react'
import {
    ReactZoomPanPinchRef,
    TransformComponent,
    TransformWrapper
} from 'react-zoom-pan-pinch'
import {getCookie} from '../../helper/Cookie.tsx'
import {ColorResult} from 'react-color'
import {Cursor, ExportField} from "./components/Cursor.tsx"
import ResetButton from "./components/ResetButton.tsx"
import {Colors} from "../../data/Colors.tsx"
import {TimeoutResponse} from "../../data/TimeoutResponse.tsx"
import {LastPlacedResponse} from "../../data/LastPlacedResponse.tsx"
import {OverlayImage} from "../../data/OverlayImage.tsx"
import {CellData} from "../../data/CellData.tsx"
import {TileImage} from "../../data/TileImage.tsx"
import Coordinates from "./components/Coordinates.tsx"
import Timer from "./components/Timer.tsx"
import {LayoutOverlay} from "./components/LayoutOverlay.tsx"
import Loading from "./components/Loading.tsx"
import CustomColor from "./components/CustomColor.tsx"
import PaintColors from "./components/PaintColors.tsx"
import LayoutImg from "./components/LayoutImg.tsx"
import {handleClickCapture, mouseDownCapture} from "../../helper/MouseHelper.tsx"
import ErrorMessage from "./components/ErrorMessage.tsx";
import StartButton from "./components/StartButton.tsx";
import CloseButton from "./components/CloseButton.tsx";


export default function Field({size}: { size: number }) {
    const colors: Colors = {
        '1': '#6D001A',
        '2': '#FF4500',
        '3': '#FFD635',
        '4': '#00A368',
        '5': '#7EED56',
        '6': '#009EAA',
        '7': '#2450A4',
        '8': '#51E9F4',
        '9': '#6A5CFF',
        'Q': '#811E9F',
        'W': '#E4ABFF',
        'E': '#FF3881',
        'R': '#6D482F',
        'T': '#FFB470',
        'Z': '#515252',
        'U': '#D4D7D9',
        'I': '#BE0039',
        'O': '#FFA800',
        'P': '#FFF8B8',
        'A': '#00CC78',
        'S': '#00756F',
        'D': '#00CCC0',
        'F': '#3690EA',
        'G': '#493AC1',
        'H': '#94B3FF',
        'J': '#B44AC0',
        'K': '#DE107F',
        'L': '#FF99AA',
        'Y': '#9C6926',
        'X': '#000000',
        'C': '#898D90',
        'V': '#FFFFFF'
    }

    const [customColor, set_customColor] = useState<string>('#FFFFFF')
    const customColorRef = useRef(customColor)
    customColorRef.current = customColor
    const customColorKey = 'B'

    const queryParameters = new URLSearchParams(window.location.search)
    const getX = queryParameters.get('x') ? parseInt(queryParameters.get('x')!) : 500
    const getY = queryParameters.get('y') ? parseInt(queryParameters.get('y')!) : 500
    const initialScale = queryParameters.get('x') || queryParameters.get('y') ? 2 : 0.08

    const initOverlay = queryParameters.get('overlay') ? queryParameters.get('overlay')! : ''
    const [activeOverlay, set_activeOverlay] = useState<string>(initOverlay)

    const [currentTimeout, set_currentTimeout] = useState(0)
    const currentTimeoutRef = useRef(currentTimeout)
    currentTimeoutRef.current = currentTimeout

    const [activeCell, set_activeCell] = useState<number[]>([getX, getY])
    const activeCellRef = useRef(activeCell)
    activeCellRef.current = activeCell

    const [exportCornerLeft, set_exportCornerLeft] = useState<number[]>([])
    const exportCornerLeftRef = useRef(exportCornerLeft)
    exportCornerLeftRef.current = exportCornerLeft

    const [exportCornerRight, set_exportCornerRight] = useState<number[]>([])
    const exportCornerRightRef = useRef(exportCornerRight)
    exportCornerRightRef.current = exportCornerRight

    const [wrapperScale, set_wrapperScale] = useState(initialScale)
    const currentScaleRef = useRef(wrapperScale)
    currentScaleRef.current = wrapperScale

    const [drawTimeout, set_drawTimeout] = useState(0)
    const drawTimeoutRef = useRef(drawTimeout)
    drawTimeoutRef.current = drawTimeout

    const [overlayImages, set_overlayImages] = useState<OverlayImage[]>([])

    const [isInInput, set_isInInput] = useState(false)
    const isInInputRef = useRef(isInInput)
    isInInputRef.current = isInInput

    const [cellColor, set_cellColor] = useState<CellData | null>()

    const canvasRef = useRef<HTMLCanvasElement>(null)
    const cursorRef = useRef<HTMLImageElement>(null)
    const wrapperRef = useRef<ReactZoomPanPinchRef>(null)
    const inputRef = useRef<HTMLInputElement>(null)

    const [overlayColors, set_overlayColors] = useState<string[]>([])
    const [selectedLayout, set_selectedLayout] = useState<number | null>()
    const selectedLayoutRef = useRef(selectedLayout)
    selectedLayoutRef.current = selectedLayout

    const lastUpdated = useRef(Date.now())

    const cellSize = 10

    const [displayColorPicker, set_displayColorPicker] = useState(false)

    const [loadedTiles, set_loadedTiles] = useState(0)
    const [isLoaded, set_isLoaded] = useState(false)
    const isLoadedRef = useRef(isLoaded)
    isLoadedRef.current = isLoaded

    const [isStarted, set_isStarted] = useState(false)
    const isStartedRef = useRef(isStarted)
    isStartedRef.current = isStarted

    useEffect(() => {
        if (!isLoaded) {
            drawImages()
        } else {
            fetchTimeoutData()

            const intervalId = setInterval(() => {
                fetch('/api/place/discover?t=' + lastUpdated.current).then(
                    res => res.json()
                ).then(
                    (data: TileImage[]) => {
                        data.forEach(tile => {
                            drawImage(tile.x, tile.y, "changes")
                        })

                        lastUpdated.current = Date.now()
                    }
                )
            }, 2000)

            const timeOutInterval = setInterval(() => {
                set_drawTimeout(t => t - 1)
            }, 1000)

            document.addEventListener('keydown', onKeyPressed)

            return () => {
                clearInterval(intervalId)
                clearInterval(timeOutInterval)
                document.removeEventListener('keydown', onKeyPressed)
            }
        }
    }, [isLoaded])

    useEffect(() => {
        onActiveCellUpdate(activeCell)
    }, [activeCell])

    useEffect(() => {
        onActiveOverlayUpdate(activeOverlay)
    }, [activeOverlay])

    useEffect(() => {
        if (16 <= loadedTiles) set_isLoaded(true)
    }, [loadedTiles])

    return <div className={'place-field'}>
        <Loading isLoading={!isLoaded} progress={(100 / 16) * loadedTiles}></Loading>

        <div className={'place-content'}>
            <TransformWrapper ref={wrapperRef}
                              onZoom={(e) => set_wrapperScale(e.state.scale)}
                              limitToBounds={false}
                              doubleClick={{disabled: true}}
                              minScale={0.05}
                              maxScale={10}
                              initialScale={currentScaleRef.current}
            >
                <TransformComponent
                    wrapperClass={"wrapper"}
                >
                    <canvas className={'field'}
                            ref={canvasRef}
                            width={size} height={size}
                            onClick={onCanvasClick}
                            onMouseDownCapture={mouseDownCapture}
                            onClickCapture={handleClickCapture}
                            style={{
                                minWidth: size * cellSize + 'px',
                                minHeight: size * cellSize + 'px'
                            }}
                            onContextMenu={onCanvasContextMenu}>
                    </canvas>

                    {isStarted ?
                        <>{Array.from({length: overlayImages.length}, (_, i) => {
                                    return <LayoutImg
                                        overlayImages={overlayImages}
                                        i={i}
                                        cellSize={cellSize}
                                        onImageClick={(e) => onOverlayImageClick(e, i)}
                                    />
                                }
                            )}</>
                        : <></>
                    }

                    <div style={!isStarted ? {opacity: "0"}:{}}>
                        <Cursor activeCell={activeCell} cellSize={cellSize} ref={cursorRef}/>
                    </div>

                    <div style={isStarted ? {display: "none"}:{}}>
                        <ExportField exportCorners={[exportCornerLeft, exportCornerRight]} cellSize={cellSize}/>
                    </div>
                </TransformComponent>
            </TransformWrapper>
        </div>

        <div className={isStarted ? "controls started" : "controls"}>
            <StartButton onClick={() => {
                set_isStarted(true)
            }}/>

            <ErrorMessage/>

            <div className={"top"}>
                <div className={"control-container"}>
                    <ResetButton onClick={() => {
                        wrapperRef.current!.zoomToElement(
                            cursorRef.current!,
                            currentScaleRef.current,
                        )
                    }}/>

                    <Timer drawTimeout={drawTimeout}/>

                    <Coordinates activeCell={activeCell} cellColor={cellColor!}
                                 onClick={() => set_customColor(cellColor!.color)}/>

                    <CloseButton onClick={() => {
                        set_isStarted(false)
                    }}/>
                </div>

                <LayoutOverlay
                    onFocus={() => set_isInInput(true)}
                    onBlur={() => set_isInInput(false)}
                    onClick={(color: string) => onLayoutOverlayClick(color)}
                    onChange={(e) => set_activeOverlay(e.target.value)}
                    activeOverlay={activeOverlay}
                    colors={overlayColors}
                    ref={inputRef}
                />
            </div>

            <div className={"colors-container" + (drawTimeout > 0 ? "" : " ready")}>
                <div>
                    <PaintColors colors={colors} onColorClick={drawCell}/>

                    <CustomColor customColor={customColor}
                                 customColorKey={customColorKey}
                                 displayColorPicker={displayColorPicker}
                                 onCustomColorClick={onCustomColorClick}
                                 onCustomColorPickerClick={onCustomColorPickerClick}
                                 onPickerChange={(e: ColorResult) => set_customColor(e.hex)}/>
                </div>
            </div>
        </div>
    </div>

    function fetchTimeoutData() {
        fetch('/api/place/timeout').then(
            res => res.json()
        ).then(
            (data: TimeoutResponse) => set_currentTimeout(data['seconds'])
        )

        fetch('/api/place/lastplaced').then(
            res => res.json()
        ).then(
            (data: LastPlacedResponse) => set_drawTimeout(Math.ceil(data['seconds']))
        )
    }

    function onActiveCellUpdate(currentValue: number[]) {
        wrapperRef.current!.zoomToElement(
            cursorRef.current!,
            currentScaleRef.current,
        )

        const queries = new URLSearchParams(window.location.search)
        queries.set('x', currentValue[0].toString())
        queries.set('y', currentValue[1].toString())
        window.history.replaceState({}, '', window.location.pathname + '?' + queries.toString())

        set_cellColor(null)

        setTimeout(() => {
            if (currentValue === activeCellRef.current) {
                fetch(`/api/place/color/${currentValue[0]}/${currentValue[1]}`).then(
                    res => res.json()
                ).then(
                    (data: CellData) => set_cellColor(data)
                )
            }
        }, 1000)
    }

    function onActiveOverlayUpdate(currentValue: string) {
        const queries = new URLSearchParams(window.location.search)

        if (currentValue != "") {
            setTimeout(() => {
                if (currentValue === inputRef.current!.value) {
                    fetch('/api/place/overlay/' + currentValue).then(
                        res => res.json()
                    ).then(
                        (data: OverlayImage[]) => set_overlayImages(data)
                    )
                }
            }, 1000)

            queries.set('overlay', currentValue)
        } else {
            queries.delete('overlay')
        }

        set_overlayImages([])
        window.history.replaceState({}, '', window.location.pathname + '?' + queries.toString())
    }

    function drawImages() {
        for (let j = 0; j < 4; j++) {
            for (let i = 0; i < 4; i++) {
                drawImage(250 * i, 250 * j)
            }
        }
    }

    function drawImage(x: number, y: number, method: string = "generate") {
        const image = new Image(250, 250)
        image.src = `/api/place/${method}/${x}/${y}?t=${lastUpdated.current}`

        image.onload = () => {
            const canvas = canvasRef.current!
            const ctx = canvas.getContext("2d")!

            ctx.drawImage(image, x, y, 250, 250)

            if (method == "generate") set_loadedTiles(current => current + 1)
        }
    }

    function drawCell(color: string) {
        if (drawTimeoutRef.current > 0 || !isLoadedRef.current || !isStartedRef.current)
            return

        const x = activeCellRef.current[0]
        const y = activeCellRef.current[1]

        set_drawTimeout(currentTimeoutRef.current)

        fetch(
            '/api/place/set',
            {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    color: color.replace('#', ''),
                    x: x,
                    y: y
                })
            }
        ).then((response) => {
            if (response.status !== 200) {
                set_drawTimeout(0)
                return
            }

            const canvas = canvasRef.current!
            const ctx = canvas.getContext("2d")!

            ctx.fillStyle = color
            ctx.fillRect(x, y, 1, 1)
        })
    }

    function calculateClickPos(event: React.MouseEvent, bounds: DOMRect) {
        return {
            x: Math.floor((event.clientX - bounds.left) / cellSize / currentScaleRef.current),
            y: Math.floor((event.clientY - bounds.top) / cellSize / currentScaleRef.current)
        }
    }

    function moveActiveCell(dX = 0, dY = 0) {
        const x = activeCellRef.current[0] + dX
        const y = activeCellRef.current[1] + dY

        if (x < 0 || x > 999 || y < 0 || y > 999) return

        set_activeCell([x, y])
    }

    function onCanvasClick(e: React.MouseEvent<HTMLCanvasElement>) {
        if (!isStartedRef.current) return;

        const bounds = (e.target as HTMLCanvasElement).getBoundingClientRect()
        const pos = calculateClickPos(e, bounds)

        const x = pos.x
        const y = pos.y

        if (x < 0 || x > 999 || y < 0 || y > 999) return

        inputRef.current!.blur()

        set_activeCell([x, y])
        set_overlayColors([])

        if (selectedLayoutRef.current != null) {
            const layoutImg =
                document.getElementById(`overlayImg_${selectedLayout}`) as HTMLImageElement
            layoutImg!.src = overlayImages[selectedLayoutRef.current].url

            set_selectedLayout(null)
        }
    }

    function onCanvasContextMenu(e: React.MouseEvent<HTMLCanvasElement>) {
        e.preventDefault()

        if (isStartedRef.current) return;

        const bounds = (e.target as HTMLCanvasElement).getBoundingClientRect()
        const pos = calculateClickPos(e, bounds)

        const x = pos.x
        const y = pos.y

        if (x < 0 || x > 999 || y < 0 || y > 999) return

        const exportCorner_ = [exportCornerLeftRef.current, exportCornerRightRef.current];

        if (exportCorner_[0].length == 0) {
            exportCorner_[0] = [x, y]
        } else if (exportCorner_[1].length == 0) {
            exportCorner_[1] = [x, y]

            const min_x = Math.min.apply(null, [
                exportCorner_[0][0],
                exportCorner_[1][0]
            ].filter(function(n) { return !isNaN(n); }))
            const min_y = Math.min.apply(null, [
                exportCorner_[0][1],
                exportCorner_[1][1]
            ].filter(function(n) { return !isNaN(n); }))

            const max_x = Math.max.apply(null, [
                exportCorner_[0][0],
                exportCorner_[1][0]
            ].filter(function(n) { return !isNaN(n); }))
            const max_y = Math.max.apply(null, [
                exportCorner_[0][1],
                exportCorner_[1][1]
            ].filter(function(n) { return !isNaN(n); }))

            exportCorner_[0] = [min_x, min_y]
            exportCorner_[1] = [max_x, max_y]
        } else {
            exportCorner_[0] = [x, y]
            exportCorner_[1] = []
        }

        set_exportCornerLeft(exportCorner_[0])
        set_exportCornerRight(exportCorner_[1])
    }

    function onKeyPressed(e: KeyboardEvent) {
        if (isInInputRef.current || !isLoadedRef.current || !isStartedRef.current) return

        const key = e.key.toString().toUpperCase()

        if (key === 'ARROWLEFT') {
            e.preventDefault()
            moveActiveCell(-1)
        } else if (key === 'ARROWRIGHT') {
            e.preventDefault()
            moveActiveCell(1)
        } else if (key === 'ARROWUP') {
            e.preventDefault()
            moveActiveCell(0, -1)
        } else if (key === 'ARROWDOWN') {
            e.preventDefault()
            moveActiveCell(0, 1)
        }

        if (e.repeat) return

        if (colors[key])
            drawCell(colors[key])
        else if (key === customColorKey)
            drawCell(customColorRef.current)
    }

    function onLayoutOverlayClick(color: string) {
        set_customColor(color)

        const layoutImg =
            document.getElementById(`overlayImg_${selectedLayout}`) as HTMLImageElement
        layoutImg!.src =
            `/api/place/overlay/${activeOverlay}/${selectedLayout}/${color.replace("#", "")}`
    }

    function onCustomColorPickerClick() {
        set_displayColorPicker(c => !c)
        set_isInInput(c => !c)
    }

    function onCustomColorClick(e: React.MouseEvent<HTMLDivElement>) {
        const element = e.target as Element

        if (element.id == 'color_picker')
            drawCell(customColor)
    }

    function onOverlayImageClick(e: React.MouseEvent<HTMLImageElement>, i: number) {
        if (!isStartedRef.current) return;

        const bounds = (e.target as HTMLImageElement).getBoundingClientRect()
        const pos = calculateClickPos(e, bounds)
        const x = pos.x + overlayImages[i]['x']
        const y = pos.y + overlayImages[i]['y']

        if (x < 0 || x > 999 || y < 0 || y > 999) return

        inputRef.current!.blur()

        set_activeCell([x, y])
        set_overlayColors(overlayImages[i]['colors'])

        if (selectedLayoutRef.current != null && selectedLayoutRef.current != i) {
            const layoutImg =
                document.getElementById(`overlayImg_${selectedLayout}`) as HTMLImageElement
            layoutImg!.src = overlayImages[selectedLayoutRef.current].url
        }

        set_selectedLayout(i)
    }
}