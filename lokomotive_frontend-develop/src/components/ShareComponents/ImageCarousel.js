import React, { useState } from "react";
import Lightbox from "react-image-lightbox";
import "react-image-lightbox/style.css";
import FitImage from "./FitImage";
import "./ImageCarousel.css";

/**
 * Show simple image carousel (using bootstrap imageCarousel).
 *
 * @param {Array} slides array of slides to show {image_url, title, description}
 * @param {Integer} height height of the component
 * @param {string} imageFitMode image fit mode fit or fill
 */

const ImageCarousel = ({ slides, height = "400px", imageFitMode = "fit", withLightBox = true }) => {
  let [isOpen, setIsOpen] = useState(false);
  let [imageIndex, setImageIndex] = useState(0);
  let [isHovering, setIsHovering] = useState(false);

  return (
    <>
      <div
        id="imageCarousel"
        className="carousel slide"
        data-ride="carousel"
        data-interval={false}
        onMouseOver={() => setIsHovering(true)}
        onMouseEnter={() => setIsHovering(!isHovering)}
        onMouseLeave={() => setIsHovering(!isHovering)}
      >
        {slides.length > 1 && (
          <ol className="carousel-indicators">
            {slides.length > 1 &&
              slides.map((slide, index) => (
                <li
                  key={index}
                  data-target="#imageCarousel"
                  data-slide-to={index}
                  className={index === 0 ? "active" : ""}
                />
              ))}
          </ol>
        )}
        <div className="carousel-inner">
          {slides.map((slide, index) => (
            <div
              key={index}
              className={`carousel-item ${index === 0 ? "active" : ""} 
                ${slides.length > 1 ? "with-indicator" : ""}`}
            >
              <a className="d-flex" href="#lightBox">
                <FitImage
                  mode={imageFitMode}
                  src={slide.image_url}
                  height={height}
                  onClick={() => {
                    setIsOpen(true);
                    setImageIndex(index);
                  }}
                />
              </a>
              {!!slide.title && (
                <div className="carousel-caption d-none d-md-block">
                  <h1>{slide.title}</h1>
                  <p>{slide.description}</p>
                </div>
              )}
            </div>
          ))}
        </div>
        {isHovering && slides.length > 1 && (
          <>
            <a
              className="carousel-control-prev bg-grey"
              href="#imageCarousel"
              role="button"
              data-slide="prev"
            >
              <span className="carousel-control-prev-icon" aria-hidden="true" />
              <span className="sr-only">Previous</span>
            </a>
            <a
              className="carousel-control-next bg-grey"
              href="#imageCarousel"
              role="button"
              data-slide="next"
            >
              <span className="carousel-control-next-icon" aria-hidden="true" />
              <span className="sr-only">Next</span>
            </a>
          </>
        )}
      </div>

      {withLightBox && isOpen && (
        <Lightbox
          mainSrc={slides[imageIndex].image_url}
          nextSrc={slides.length > 1 ? slides[(imageIndex + 1) % slides.length] : null}
          prevSrc={
            slides.length > 1 ? slides[(imageIndex + slides.length - 1) % slides.length] : null
          }
          onCloseRequest={() => setIsOpen(false)}
          onMovePrevRequest={() => setImageIndex((imageIndex + slides.length - 1) % slides.length)}
          onMoveNextRequest={() => setImageIndex((imageIndex + 1) % slides.length)}
        />
      )}
    </>
  );
};

export default ImageCarousel;
