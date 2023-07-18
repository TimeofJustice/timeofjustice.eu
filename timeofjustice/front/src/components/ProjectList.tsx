import {useEffect, useState} from "react";
import {Project} from "../data/Project.tsx";

export const ProjectList = ({callback}: {callback: Function}) => {
    const [data, setData] = useState<Project[]>([]);

    useEffect(() => {
        const dataFetch = async () => {
            const data = await (
                await fetch('http://localhost:8000/api/projects')
            ).json();

            setData(data);
        };

        dataFetch().then(() => {});
    }, []);

    let listItems;

    if (!data) return <h1>Loading...</h1>;
    else {
        listItems = data.map((project, index) =>
            <div className="project" onClick={() => callback(index)} key={project.name}>
                <div className="mark"></div>
                <div className="inner">
                    {project.git &&
                        <a className="git" href={project.git} target="_blank">
                            <i className="fab fa-github"></i>
                        </a>
                    }
                    <div className="status">{project.status}</div>
                    <div className="title">{project.name}</div>
                    <div className="languages">
                        {0 < project.languages.length ? (
                                project.languages.map((language: string, index: number, arr: Array<String>) =>
                                <span key={language}>
                                    <span>
                                        {language}
                                        {index != arr.length - 1 &&
                                            <span>, </span>
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
            </div>
        );
    }

    // @ts-ignore
    return <div className="project-container">
        <div className="title">/Projects</div>

        <div className="projects">
            {listItems}
        </div>
    </div>
}
