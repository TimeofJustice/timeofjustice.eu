import {ProjectList} from "../components/projects/ProjectList.tsx";
import Rondell from "../components/projects/Rondell.tsx";
import "../assets/css/Projects.css"

export default function Projects({ callback, current_index }: { callback: (index: number) => void; current_index: number }) {
    document.title = "Projects - TimeofJustice";

    return <>
        <ProjectList onProjectSelect={(index: number) => {callback(index)}} index={current_index}/>
        <Rondell index={current_index}/>
    </>
}