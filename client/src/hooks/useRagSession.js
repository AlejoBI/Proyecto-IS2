import { useEffect, useState } from "react";
import { createSessionRequest } from "../api/auth";

export const useRagSession = () => {
  const [sessionInfo, setSessionInfo] = useState(null);
  const [sessionError, setSessionError] = useState(null);

  useEffect(() => {
    createSessionRequest()
      .then(setSessionInfo)
      .catch(() => setSessionError("The API session could not be created."));
  }, []);

  return { sessionInfo, sessionError };
};
