export default function ResetButton({onClick}: { onClick: () => void }) {
    return <div className={'reset-transform'}
                onClick={onClick}>
        <i className="fa-solid fa-arrows-to-dot"></i>
    </div>
}