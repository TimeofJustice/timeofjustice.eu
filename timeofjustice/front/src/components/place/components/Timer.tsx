export default function Timer({drawTimeout}: { drawTimeout: number }) {
    return <div className={'timer'} style={
        {display: drawTimeout > 0 ? 'flex' : 'none'}
    }>
        <span>{drawTimeout > 0 ? drawTimeout + 's' : ''}</span>
    </div>
}