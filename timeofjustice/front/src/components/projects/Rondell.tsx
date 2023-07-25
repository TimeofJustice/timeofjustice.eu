import {useEffect, useRef, useState} from "react";
import {ProjectData} from "../../data/ProjectData.tsx";
import {useSwipeable} from "react-swipeable";
import {timeout} from "../../helper/Timeout.tsx";

export default function Rondell({index}: { index: number }) {
    const [data, setData] = useState<ProjectData>();
    const [current_image_index, set_current_image_index] = useState(0);
    const current_image_indexRef = useRef<number>();
    current_image_indexRef.current = current_image_index;
    const [prev_image_index, set_prev_image_index] = useState(1);
    const [maxImg, set_maxImg] = useState(0);
    const maxImgRef = useRef<number>();
    maxImgRef.current = maxImg;
    const [isRondellReady, set_isRondellReady] = useState<number>(0);
    const isRondellReadyRef = useRef<number>();
    isRondellReadyRef.current = isRondellReady;
    const [lastTouchX, set_lastTouchX] = useState(0);
    const lastTouchXRef = useRef<number>();
    lastTouchXRef.current = lastTouchX;
    const [styles, setStyle] = useState<{}[]>([{left: "0"}, {}])
    const [isInFullview, set_isInFullview] = useState(false)
    const isInFullviewRef = useRef<boolean>();
    isInFullviewRef.current = isInFullview;

    const handlers = useSwipeable(
        {
            onSwipedLeft: async () => {
                await change_active_image(1)
            },
            onSwipedRight: async () => {
                await change_active_image(-1)
            },
            delta: 10,
            trackTouch: true,
            trackMouse: true,
        }
    )

    let mouseDownX = 0;
    let mouseDownY = 0;

    const mouseDownCapture = (e: any) => {
        mouseDownX = e.clientX;
        mouseDownY = e.clientY;
    };

    const handleClickCapture = (e: any) => {
        if (
            Math.abs(mouseDownX - e.clientX) >= 30 ||
            Math.abs(mouseDownY - e.clientY) >= 30
        ) {
            e.stopPropagation();
        }
    };

    useEffect(() => {
        const dataFetch = async () => {
            const data = await (
                await fetch('/api/project/' + index)
            ).json();

            setData(data)
            set_maxImg(data.images.length)
            set_current_image_index(0)
        }

        dataFetch().then(() => {
        })
    }, [index]);

    useEffect(() => {
        const interval = setInterval(async () => {
            if (30000 < new Date().getTime() - lastTouchXRef.current! && document.visibilityState === "visible" && !isInFullviewRef.current!) {
                await change_active_image(1, false)
            }
        }, 5000);
        return () => clearInterval(interval);
    }, []);

    if (data === undefined) {
        return <div  className="rondel-container" style={{
            padding: "20px",
        }}>
            <h1>Loading...</h1>
        </div>
    } else {
        return <div className="rondel-container">
            <div
                className="images"
                id="images"
                onClick={() => {
                    document.getElementById("fullview")!.classList.add("active")
                    set_isInFullview(true)
                }}
                onMouseDownCapture={mouseDownCapture}
                onClickCapture={handleClickCapture}
                {...handlers}>
                {data.images.map((content: string[], _index: number) =>
                    <div
                        className={"blur-load blur image-container"}
                        key={_index}
                        style={Object.assign(
                            _index === current_image_index ? styles[0] : _index === prev_image_index ? styles[1] : {display: "none"},
                            {backgroundImage: `url(${content[0][1]})`}
                        )
                        }
                    >
                        <img
                            src={content[0][0]}
                            className={"image"}
                            alt={content[1]}
                            loading={"lazy"}
                            onLoad={() => {
                                const imagesContainer = document.getElementById("images")!
                                const images = imagesContainer.getElementsByClassName("image")
                                images[_index].classList.add("loaded")
                                images[_index].parentElement!.classList.add("loaded")
                            }}
                        />
                    </div>
                )}
            </div>

            <div className="description">
                <div id="description">
                    {data.description}
                </div>
            </div>

            <div className="dots" id="dots">
                {data.images.map((_, _index: number) =>
                    <i
                        className={`fa fa-circle ${_index === current_image_index ? "active" : ""}`}
                        onClick={() => change_active_image_to(_index)}
                        key={_index}
                    />
                )}
            </div>

            <div className="arrow-left" onClick={async () => {
                await change_active_image(-1)
            }}>
                <i className="fa fa-arrow-circle-left"></i>
            </div>
            <div className="arrow-right" onClick={async () => {
                await change_active_image(1)
            }}>
                <i className="fa fa-arrow-circle-right"></i>
            </div>

            <div id={"fullview"} onClick={
                () => {
                    document.getElementById("fullview")!.classList.remove("active")
                    set_isInFullview(false)
                }
            }>
                {data.images.map((content: string[], _index: number) =>
                    <div
                        className={"blur-load blur"}
                        key={_index}
                        style={current_image_index === _index ? {display: "block"} : {display: "none"}}
                    >
                        <img
                            src={content[0][0]}
                            alt={content[1]}
                            loading={"lazy"}
                            onLoad={() => {
                                const fullview = document.getElementById("fullview")!
                                const images = fullview.getElementsByTagName("img")
                                images[_index].classList.add("loaded")
                                images[_index].parentElement!.classList.add("loaded")
                            }}
                        />
                    </div>
                )}
            </div>
        </div>
    }

    async function change_active_image(changer: number, isTouch: boolean = true) {
        if (maxImgRef.current === 0 || !(500 < new Date().getTime() - isRondellReadyRef.current!)) return;

        let newImg = (current_image_indexRef.current! + changer + maxImgRef.current!) % maxImgRef.current!;

        if (newImg === current_image_indexRef.current) return;

        set_current_image_index(newImg)
        set_prev_image_index(current_image_indexRef.current!)

        if (changer < 0) {
            await setStyleForMovement(false)
        } else {
            await setStyleForMovement(true)
        }

        if (isTouch) set_lastTouchX(new Date().getTime())

        set_isRondellReady(new Date().getTime())
    }

    async function setStyleForMovement(isRight: Boolean) {
        let directions = ["-", ""]
        if (isRight) directions = ["", "-"]

        setStyle([{left: `${directions[0]}100%`, transition: "none"}, {left: "0"}])

        await timeout(100)

        setStyle([{left: "0"}, {left: `${directions[1]}100%`}])
    }

    async function change_active_image_to(_index: number) {
        await change_active_image(_index - current_image_index)
    }
}