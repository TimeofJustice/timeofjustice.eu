export default function Loading({isLoading, progress}: { isLoading: boolean, progress: number }) {
    return isLoading ?
        <div className={"loading"}>
            <i className="fa-solid fa-spinner fa-spin-pulse"></i>
            Loading...
            <div className={"loading-bar"}>
                <div className={"bar"} style={
                    {
                        width: progress + "%"
                    }
                }></div>
            </div>
        </div>
        :
        <></>
}