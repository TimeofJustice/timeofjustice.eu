export default function Loading({isLoading}: { isLoading: boolean }) {
    return isLoading ?
        <div className={"loading"}>
            <i className="fa-solid fa-spinner fa-spin-pulse"></i>
            Loading...
        </div>
        :
        <></>
}