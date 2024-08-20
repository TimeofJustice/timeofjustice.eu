export default function CloseButton({onClick}: {onClick: () => void}) {
    return <div className={"close-button"}
                onClick={onClick}>
        <i className="fa-solid fa-xmark"></i>
    </div>
}