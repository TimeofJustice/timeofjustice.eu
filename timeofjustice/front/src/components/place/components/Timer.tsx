export default function Timer({drawTimeout}: { drawTimeout: number }) {
    return <div className={'timer'} style={
        {display: drawTimeout > 0 ? 'block' : 'none'}
    }>
        {drawTimeout > 0 ? drawTimeout + ' seconds' : ''}
    </div>
}