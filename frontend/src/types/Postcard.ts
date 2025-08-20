export interface Design {
  id: number;
  pageColor: string;
  backgroundColor: string;
  stampColor: string;
  accentColor: string;
  textColor: string;
  icon: string;
}

export interface Postcard {
  id: number;
  message: string;
  greetings: string;
  design: Design;
}

export const defaultDesign: Design = {
  id: 0,
  pageColor: "#ffbaba",
  backgroundColor: "#fff",
  stampColor: "#e5b473",
  accentColor: "#e57373",
  textColor: "#333333",
  icon: "twemoji:teddy-bear",
};

export const defaultPostcard: Postcard = {
  id: 0,
  message: "Hier könnte deine Nachricht stehen!",
  greetings: "Dein Name",
  design: defaultDesign,
};
