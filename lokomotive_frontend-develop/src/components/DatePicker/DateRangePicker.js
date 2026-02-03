import React, { useEffect, useState } from "react";
import { DateRangePicker, DateRange } from "react-date-range";
import "bootstrap/dist/css/bootstrap.min.css";
import { Button, Popover, OverlayTrigger } from "react-bootstrap";
import "react-date-range/dist/styles.css";
import "react-date-range/dist/theme/default.css";
import "../../styles/datePicker/DateRangePicker.scss";

const DatePicker = ({ startDate, endDate, onRangeChanged, text }) => {
  const initialStartDate = startDate || new Date();
  const initialEndDate = endDate || new Date();
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(true);
    };

    // Check if window is defined before adding the event listener
    if (typeof window !== "undefined") {
      setIsMobile(window.innerWidth <= 768);
      window.addEventListener("resize", handleResize);

      // Clean up the event listener when the component unmounts
      return () => {
        window.removeEventListener("resize", handleResize);
      };
    }
  }, []); // Empty dependency array ensures the effect runs only once

  const [state, setState] = useState([
    {
      startDate: initialStartDate,
      endDate: initialEndDate,
      key: "selection",
    },
  ]);

  const [isOpen, setIsOpen] = useState(false);

  const handleRangeChange = (item) => {
    setState([item?.selection]);
  };

  const RenderedPicker = isMobile ? DateRange : DateRangePicker;

  const popover = (
    <Popover id="popover-basic" style={{ maxWidth: "95%" }}>
      <Popover.Content
        style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column" }}
      >
        <RenderedPicker
          id="picker"
          onChange={handleRangeChange}
          showSelectionPreview
          months={isMobile ? 1 : 2}
          ranges={state && state}
          direction="vertical"
          scroll={{
            enabled: true,
            // monthHeight: 250,
            // longMonthHeight: ,
            //monthWidth: 150,
            //calendarWidth: 150,
            //calendarHeight: window?.innerWidth <= 576 ? 200 : 200,
          }}
          className="date-picker-container"
          renderStaticRanges={() => null}
          renderCustomArrow={({ direction, onClick }) => (
            <div className="rdrCustomArrowContainer">
              <button
                type="button"
                className={`rdrCustomArrow rdrCustomArrow-${direction}`}
                onClick={onClick}
              >
                {direction === "left" ? "<" : ">"}
              </button>
            </div>
          )}
        />
        <div>
          <Button variant="" className="mt-3" onClick={() => setIsOpen(false)}>
            Close
          </Button>
          <Button
            variant="secondary"
            className="mt-3"
            onClick={() => {
              onRangeChanged(state);
              setIsOpen(false);
            }}
          >
            Confirm
          </Button>
        </div>
      </Popover.Content>
    </Popover>
  );

  const toggleDatePicker = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div
      style={{
        display: "flex",
        alignSelf: "end",
        width: "155px",
        justifyContent: "end",
      }}
    >
      <OverlayTrigger
        trigger="click"
        placement={isMobile ? "bottom" : "left"}
        overlay={popover}
        show={isOpen}
        onHide={() => setIsOpen(false)}
      >
        <Button onClick={toggleDatePicker}>{text || "Seelect Date Range"}</Button>
      </OverlayTrigger>
    </div>
  );
};

export default DatePicker;
