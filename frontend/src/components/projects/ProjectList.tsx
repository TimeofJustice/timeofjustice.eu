import {useEffect, useState} from "react";
import {ProjectData} from "../../data/ProjectData.tsx";
import {Project} from "./Project.tsx";

export const ProjectList = ({onProjectSelect, index}: {
    onProjectSelect: (projectIndex: number) => void,
    index: number
}) => {

    const [data, setData] = useState<ProjectData[]>([]);
    const [selected, setSelected] = useState<number>(index);

    useEffect(() => {
        fetch('/api/projects').then(
            res => res.json()
        ).then(
            data => setData(data)
        )
    }, []);

    return !data ? <h1>Loading...</h1> : (
        <div className="project-container">
            <div className="title">/Projects</div>

            <div className="projects">
                {
                    data.map((project, index) =>
                        <div className={selected == index ? "project active" : "project"} onClick={() => {
                            onProjectSelect(index);
                            setSelected(index);
                        }} key={index}>
                            <Project data={project}/>
                        </div>
                    )
                }
            </div>
        </div>
    )
}
