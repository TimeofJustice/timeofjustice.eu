import {ProjectData} from "../../data/ProjectData.tsx";

export const Project = ({data}: {data: ProjectData}) => {
    return <>
        <div className="mark"></div>
        <div className="inner">
            {data.git &&
                <a className="git" href={data.git} target="_blank">
                    <i className="fab fa-github"></i>
                </a>
            }
            <div className="status">{data.status}</div>
            <div className="title">{data.name}</div>
            <div className="languages">
                {0 < data.tags.length ? (
                    data.tags.map((language: string, index: number, arr: Array<String>) =>
                        <span key={language}>
                                    <span>
                                        {language}
                                        {index != arr.length - 1 &&
                                            <span style={{marginRight: "2px"}}>,</span>
                                        }
                                    </span>
                                </span>
                    )
                ) : (
                    <span>Unknown</span>
                )
                }
            </div>
        </div>
    </>
}