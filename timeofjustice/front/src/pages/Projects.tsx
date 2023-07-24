import {ProjectList} from "../components/projects/ProjectList.tsx";
import Rondell from "../components/projects/Rondell.tsx";

export default function Projects({ callback, current_index }: { callback: (index: number) => void; current_index: number }) {
    document.title = "Projects - TimeofJustice";

    return <>
        <ProjectList callback={(index: number) => {callback(index)}}/>
        <Rondell index={current_index}/>
    </>
}