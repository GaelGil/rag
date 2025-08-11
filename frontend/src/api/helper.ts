import DEFAULT_PHOTO from "../assets/default-pfp.jpg";

export const checkResponse = (
  res: Response
): { res: Response | null; error: Error | null } => {
  if (!res.ok) {
    return {
      res: res,
      error: new Error(`HTTP error! Status: ${res.status}`),
    };
  }
  return {
    res: res,
    error: null,
  };
};

export const getDefaultPhoto = (): string => {
  return DEFAULT_PHOTO;
};
