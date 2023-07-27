import React, {useEffect, useRef, useState} from 'react'
import {ReactZoomPanPinchRef, TransformComponent, TransformWrapper} from 'react-zoom-pan-pinch'
import {getCookie} from '../../helper/Cookie.tsx'
import {ChromePicker, ColorResult} from 'react-color';

interface Colors {
    [key: string]: string
}

interface TimeoutResponse {
    seconds: number
}

interface LastPlacedResponse {
    seconds: number
}

interface OverlayImage {
    url: string,
    x: number,
    y: number,
    width: number,
    height: number
}

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
    const [activeOverlay] = useState<string>(initOverlay)

    const [currentTimeout, set_currentTimeout] = useState(0)
    const currentTimeoutRef = useRef(currentTimeout)
    currentTimeoutRef.current = currentTimeout

    const [activeCell, set_activeCell] = useState<number[]>([getX, getY])
    const activeCellRef = useRef(activeCell)
    activeCellRef.current = activeCell

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

    const canvasRef2 = useRef<HTMLCanvasElement>(null)
    const cursorRef = useRef<HTMLDivElement>(null)
    const wrapperRef = useRef<ReactZoomPanPinchRef>(null)

    const cellSize = 10

    useEffect(() => {
        fetch('/api/place/timeout').then(
            res => res.json()
        ).then(
            (data: TimeoutResponse) => set_currentTimeout(data['seconds'])
        )

        if (activeOverlay != '') {
            fetch('/api/place/overlay/' + activeOverlay).then(
                res => res.json()
            ).then(
                (data: OverlayImage[]) => set_overlayImages(data)
            )
        }

        fetch('/api/place/lastplaced').then(
            res => res.json()
        ).then(
            (data: LastPlacedResponse) => set_drawTimeout(Math.ceil(data['seconds']))
        )

        const timeOutInterval = setInterval(() => {
            set_drawTimeout(t => t - 1)
        }, 1000)

        document.addEventListener('keydown', handleHotkey)

        drawImages();

        const intervalId = setInterval(() => {
            drawImages();
        }, 2000)

        return () => {
            clearInterval(intervalId)
            clearInterval(timeOutInterval)
            document.removeEventListener('keydown', handleHotkey)
        }
    }, [])

    useEffect(() => {
        wrapperRef.current!.zoomToElement(
            cursorRef.current!,
            currentScaleRef.current,
        )

        const queries = new URLSearchParams(window.location.search)
        queries.set('x', activeCell[0].toString())
        queries.set('y', activeCell[1].toString())
        window.history.replaceState({}, '', window.location.pathname + '?' + queries.toString())
    }, [activeCell])

    const drawImages = () => {
        for (let j = 0; j < 4; j++) {
            for (let i = 0; i < 4; i++) {
                drawImage(250 * i, 250 * j);
            }
        }
    }

    const drawImage = (x: number, y: number) => {
        const image = new Image(250, 250);
        image.src = `/api/place/generate/${x}/${y}?${(new Date()).getTime()}`;

        image.onload = () => {
            const canvas = canvasRef2.current!
            const ctx = canvas.getContext("2d")!

            ctx.drawImage(image, x, y, 250, 250);
        }
    }

    let mouseDownX = 0;
    let mouseDownY = 0;

    const mouseDownCapture = (e: React.MouseEvent<HTMLCanvasElement>) => {
        mouseDownX = e.clientX;
        mouseDownY = e.clientY;
    };

    const handleClickCapture = (e: React.MouseEvent<HTMLCanvasElement>) => {
        if (
            Math.abs(mouseDownX - e.clientX) >= 30 ||
            Math.abs(mouseDownY - e.clientY) >= 30
        ) {
            e.stopPropagation();
        }
    };

    const [displayColorPicker, set_displayColorPicker] = useState(false)

    return <>
        <div className={'place-field'}>
            <div className={'place-content'}>
                <TransformWrapper ref={wrapperRef}
                                  onZoom={(e) => {
                                      set_wrapperScale(e.state.scale)
                                  }}
                                  limitToBounds={false}
                                  doubleClick={{disabled: true}}
                                  minScale={0.05}
                                  maxScale={10}
                                  initialScale={currentScaleRef.current}
                >
                    <TransformComponent
                        wrapperStyle={{
                            width: '100%',
                            height: '100%',
                        }}
                        contentStyle={{
                            width: '100%',
                            height: '100%',
                        }}
                        wrapperClass={'field-wrapper'}
                    >
                        <canvas className={'field'}
                                ref={canvasRef2}
                                width={size} height={size}
                                onClick={canvasClick}
                                onMouseDownCapture={mouseDownCapture}
                                onClickCapture={handleClickCapture}
                                style={{
                                    minWidth: size * cellSize + 'px',
                                    minHeight: size * cellSize + 'px'
                                }}>

                        </canvas>

                        {Array.from({length: overlayImages.length}, (_, i) =>
                            <img src={overlayImages[i]['url']} style={{
                                imageRendering: 'pixelated',
                                position: 'absolute',
                                top: overlayImages[i]['y'] * cellSize + 'px',
                                left: overlayImages[i]['x'] * cellSize + 'px',
                                width: overlayImages[i]['width'] * cellSize + 'px',
                                height: overlayImages[i]['height'] * cellSize + 'px',
                            }}/>
                        )}

                        <div className={'active-cell'}
                             ref={cursorRef}
                             style={{
                                 position: 'absolute',
                                 left: activeCell[0] * cellSize - 1 + 'px',
                                 top: activeCell[1] * cellSize - 1 + 'px',
                                 width: cellSize + 2 + 'px',
                                 height: cellSize + 2 + 'px',
                             }}>
                            <div style={{
                                position: 'absolute',
                                borderLeft: '1px solid #FFF',
                                borderTop: '1px solid #FFF',
                                width: cellSize / 2 + 'px',
                                height: cellSize / 2 + 'px',
                                left: 0 + 'px',
                                top: 0 + 'px',
                            }}></div>
                            <div style={{
                                position: 'absolute',
                                borderRight: '1px solid #FFF',
                                borderTop: '1px solid #FFF',
                                width: cellSize / 2 + 'px',
                                height: cellSize / 2 + 'px',
                                right: 0 + 'px',
                                top: 0 + 'px',
                            }}></div>
                            <div style={{
                                position: 'absolute',
                                borderLeft: '1px solid #FFF',
                                borderBottom: '1px solid #FFF',
                                width: cellSize / 2 + 'px',
                                height: cellSize / 2 + 'px',
                                left: 0 + 'px',
                                bottom: 0 + 'px',
                            }}></div>
                            <div style={{
                                position: 'absolute',
                                borderRight: '1px solid #FFF',
                                borderBottom: '1px solid #FFF',
                                width: cellSize / 2 + 'px',
                                height: cellSize / 2 + 'px',
                                right: 0 + 'px',
                                bottom: 0 + 'px',
                            }}></div>
                            <div style={{
                                position: 'absolute',
                                borderLeft: '1px solid #000',
                                borderTop: '1px solid #000',
                                width: cellSize / 2 - 2 + 'px',
                                height: cellSize / 2 - 2 + 'px',
                                left: 1 + 'px',
                                top: 1 + 'px',
                            }}></div>
                            <div style={{
                                position: 'absolute',
                                borderRight: '1px solid #000',
                                borderTop: '1px solid #000',
                                width: cellSize / 2 - 2 + 'px',
                                height: cellSize / 2 - 2 + 'px',
                                right: 1 + 'px',
                                top: 1 + 'px',
                            }}></div>
                            <div style={{
                                position: 'absolute',
                                borderLeft: '1px solid #000',
                                borderBottom: '1px solid #000',
                                width: cellSize / 2 - 2 + 'px',
                                height: cellSize / 2 - 2 + 'px',
                                left: 1 + 'px',
                                bottom: 1 + 'px',
                            }}></div>
                            <div style={{
                                position: 'absolute',
                                borderRight: '1px solid #000',
                                borderBottom: '1px solid #000',
                                width: cellSize / 2 - 2 + 'px',
                                height: cellSize / 2 - 2 + 'px',
                                right: 1 + 'px',
                                bottom: 1 + 'px',
                            }}></div>
                        </div>
                    </TransformComponent>
                </TransformWrapper>
            </div>

            <div className={'reset-transform'}
                 onClick={() => {
                     wrapperRef.current!.resetTransform()
                 }}>
                <i className="fa-solid fa-rotate-left"></i>
            </div>

            <div className={
                'colors-container' + (drawTimeout > 0 ? '' : ' ready')
            }>
                <div className={'colors'}>
                    {Object.keys(colors).map((key) => {
                        return <div
                            className={'color'}
                            style={{backgroundColor: colors[key]}}
                            key={key}
                            onClick={() => {
                                drawCell(colors[key])
                            }}
                        >
                            <div>
                                {key}
                            </div>
                        </div>
                    })}
                </div>

                <div className={'color-picker-container'}>
                    <div className={'color-picker'}
                         style={{backgroundColor: customColor}}
                         onClick={(e) => {
                             const element = e.target as Element

                             if (element.id == 'color_picker')
                                 drawCell(customColor)
                         }}
                         id={'color_picker'}
                    >
                        <div className={'hotkey'}>
                            {customColorKey}
                        </div>

                        <div className={'color-picker-button'} onClick={() => {
                            set_displayColorPicker(!displayColorPicker);
                            set_isInInput(!isInInput);
                        }}
                        >
                            <i className={'fa-solid fa-eye-dropper'}></i>
                        </div>
                    </div>

                    {displayColorPicker ? <div style={{
                        position: 'absolute',
                        zIndex: '2',
                        bottom: '0px',
                        right: '0px'
                    }}>
                        <div style={{
                            position: 'fixed',
                            top: '0px',
                            right: '0px',
                            bottom: '0px',
                            left: '0px',
                        }} onClick={() => {
                            set_displayColorPicker(false);
                            set_isInInput(false);
                        }}/>

                        <ChromePicker
                            color={customColor}
                            onChange={(e: ColorResult) => {
                                const newColor: string = e.hex

                                set_customColor(newColor)
                            }}
                            disableAlpha={true}
                        />
                    </div> : null}
                </div>
            </div>
            <div className={'cords'}>
                <span>x: {activeCell ? activeCell[0] : 0}, </span>
                <span>y: {activeCell ? activeCell[1] : 0}</span>
            </div>
            <div className={'timer'} style={
                {display: drawTimeout > 0 ? 'block' : 'none'}
            }>
                {drawTimeout > 0 ? drawTimeout + ' seconds' : ''}
            </div>
        </div>
    </>

    function canvasClick(e: React.MouseEvent<HTMLCanvasElement>) {
        const bounds = (e.target as HTMLCanvasElement).getBoundingClientRect()

        const x = Math.floor((e.clientX - bounds.left) / cellSize / currentScaleRef.current)
        const y = Math.floor((e.clientY - bounds.top) / cellSize / currentScaleRef.current)

        if (x < 0 || x > 999 || y < 0 || y > 999) return

        set_activeCell([x, y])
    }

    function drawCell(color: string) {
        if (drawTimeoutRef.current > 0)
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

            const canvas = canvasRef2.current!
            const ctx = canvas.getContext("2d")!

            ctx.fillStyle = color
            ctx.fillRect(x, y, 1, 1)
        })
    }

    function handleHotkey(e: KeyboardEvent) {
        if (isInInputRef.current) return;

        const key = e.key.toString().toUpperCase()

        if (key === 'ARROWLEFT') {
            const x = activeCellRef.current[0] - 1
            const y = activeCellRef.current[1]

            if (x < 0 || x > 999 || y < 0 || y > 999) return

            set_activeCell([x, y])
        } else if (key === 'ARROWRIGHT') {
            const x = activeCellRef.current[0] + 1
            const y = activeCellRef.current[1]

            if (x < 0 || x > 999 || y < 0 || y > 999) return

            set_activeCell([x, y])
        } else if (key === 'ARROWUP') {
            const x = activeCellRef.current[0]
            const y = activeCellRef.current[1] - 1

            if (x < 0 || x > 999 || y < 0 || y > 999) return

            set_activeCell([x, y])
        } else if (key === 'ARROWDOWN') {
            const x = activeCellRef.current[0]
            const y = activeCellRef.current[1] + 1

            if (x < 0 || x > 999 || y < 0 || y > 999) return

            set_activeCell([x, y])
        }

        if (colors[key])
            drawCell(colors[key])
        else if (key === customColorKey)
            drawCell(customColorRef.current)
    }
}