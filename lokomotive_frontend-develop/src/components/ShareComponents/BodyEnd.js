import { useEffect } from "react";
import ReactDOM from "react-dom";

const BodyEnd = ({ children }) => {
  let endDiv = document.createElement("div");
  useEffect(() => {
    document.body.appendChild(endDiv);
    return () => {
      document.body.removeChild(endDiv);
    };
  });

  return ReactDOM.createPortal(children, endDiv);
};

export default BodyEnd;
