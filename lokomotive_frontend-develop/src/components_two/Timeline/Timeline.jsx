import React from "react";
import './Timeline.css'

const Timeline = ({ value, align, marker, content, className }) => {
  return (
    <div className={`custom-timeline ${className || ""}`}>
      {value.map((item, index) => (
        <div key={index} className={`timeline-event timeline-event-${align}`}>
          <div className="timeline-marker">{marker(item)}</div>
          <div className="timeline-content">{content(item)}</div>
        </div>
      ))}
    </div>
  );
};

export default Timeline;
