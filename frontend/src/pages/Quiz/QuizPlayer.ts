export class QuizPlayer {
  id: number;
  name: string;
  image: string;
  score: number;

  constructor(id: number, name: string, image: string) {
    this.id = id;
    this.name = name;
    this.image = image;
    this.score = 0;
  }

  addScore(score: number) {
    this.score += score;
  }
}
