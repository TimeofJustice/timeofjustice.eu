export default function StartButton({onClick}: {onClick: () => void}) {
    return <div className={"start-button"}
                onClick={onClick}>
        Start
    </div>
}