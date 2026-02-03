import React, {useState} from "react";

/**
 * Show More component with text and limit. WORKS ONLY WITH STRINGS
 *
 * @param {String} text table column header title array (REQUIRED)
 * @param {Integer} limit amount of chars before showMore buttons appear
 * @param {Integer} excerpt amount of chars to show when showMore is closed
 */

const ShowMore = ({ text, limit = 200, excerpt = 50 }) => {

  const [open, setOpen] = useState(false);

  const ShowMoreButton = ({ title }) => {
    return (
      <a
        href="/#"
        onClick={(e) => {
          e.preventDefault();
          setOpen(!open);
        }}
      >
        {`[ ${title} ]`}
      </a>
    );
  };

  if (text.length > limit) {
    if (open) {
      return (
        <div style={{overflow: "hidden", wordBreak: "break-all", whiteSpace: "normal"}}>
          {`${text} `}
          <ShowMoreButton title={"Show less"} />
        </div>
      )
    } else {
      return (
        <div>
          {`${text.slice(0, excerpt)}... `}
          <ShowMoreButton title={"Show more"} />
        </div>
      )
    }
  }
  return text
}

export default ShowMore;
