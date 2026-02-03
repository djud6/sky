import React from "react";
import "../../styles/ShareComponents/WarningMsg.scss";

const WarningMsg = ({ message, sm }) => {
  return (
    <div className="custom-warning-msg" >
      <div className="p-message p-component p-message-warn p-message-enter-done">
        <div className="p-message-wrapper">
          { sm ? 
            <React.Fragment>
              <p className="p-message-icon pi pi-exclamation-triangle p-mb-0 p-mr-3">{""}</p>
              <p className="p-message-summary text-break">
                {
                  message instanceof Array? 
                    message.map((m, index) => 
                      <React.Fragment key={index}> {m} <br /></React.Fragment>
                    )
                  : message
                }
              </p>
            </React.Fragment>
            :
            <React.Fragment>
              <h5 className="p-message-icon pi pi-exclamation-triangle p-m-0">{""}</h5>
              <h5 className="p-message-summary p-mb-0 p-ml-2">
                {message}
              </h5>
            </React.Fragment>
          }
        </div>
      </div>
    </div>
  )
}

export default WarningMsg;