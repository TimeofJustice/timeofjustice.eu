import { Technology } from "./Technology.js";
import { ProjectImage } from "./ProjectImage.ts";
import { LazyImage } from "./LazyImage.ts";

interface Status {
  name: string;
  color: "aquamarin" | "blue-grey" | "brown" | "dark-green" | "dark-red";
}

export interface Project {
  id: number;
  title: string;
  status: Status;
  short_description: string;
  description: string;
  title_image: LazyImage;
  images: ProjectImage[];
  technologies: Technology[];
  github: string;
  website: string;
}
