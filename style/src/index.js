import "./scss/main.scss";
import { Dropdown } from "bootstrap";
import "@popperjs/core";
import imagesLoaded from "imagesloaded";
import Masonry from "masonry-layout";

window.addEventListener("load", () => {
  let dropdownElementList = [].slice.call(
    document.querySelectorAll(".dropdown-toggle")
  );

  let dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
    let X = new Dropdown(dropdownToggleEl);
    console.log(X);
    return X;
  });

  let overview = document.querySelector(".grid");
  let msnry;

  if (overview) {
    imagesLoaded(overview, () => {
      msnry = new Masonry(overview, {
        itemSelector: ".grid-item",
        columnWidth: ".grid-item",
        percentPosition: true,
      });
      msnry.layout();
    });
  }
});
