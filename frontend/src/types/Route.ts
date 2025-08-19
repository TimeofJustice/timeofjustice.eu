export interface Route {
  name: string;
  path: string;
  icon: string;
  activeComponents: string[];
  isHighlighted?: boolean;
}
