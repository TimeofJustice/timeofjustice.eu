export default function Switch({callback}: {callback: Function}) {
    return <div className="switch" onClick={() => {callback()}}>
        <div className="handle">
            <i className="fa-solid fa-lightbulb"></i>
        </div>
    </div>
}