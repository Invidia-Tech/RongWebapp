import { page } from '../modules/common';

page('clan_box_summary', function () {

const stylesheet = `
.unit-selector-icon {
    transition: opacity 200ms ease;
}
#unitSelectorBody.highlighting .unit-selector-icon:not(.highlight) {
    opacity: 0.15;
}
.unit-selector-icon.highlight {
    outline: 2px solid #f0f;
    box-shadow: 0 0 0 1px #f0f inset;
}
`;

// insertStylesheet The bread and butter insert CSS
const insertStylesheet = () => {
  const stylesheetEl = document.createElement('style');
  stylesheetEl.innerHTML = stylesheet;
  document.body.appendChild(stylesheetEl);
};

// filterUnits takes a filterText and returns array of elements matching the rules
const filterUnits = filterText => {
  // If last character is `$` we use `$=` instead of `*=`
  const mode = (filterText.substr(-1) === "$") ? "$" : "*";
  filterText = (filterText.substr(-1) === "$") ? filterText.slice(0, -1) : filterText;

  return Array.from(document.querySelectorAll(`.unit-selector-icon[title${mode}="${filterText}"i]`));
}

// highlightUnits highlights all units matching `filterText`
const highlightUnits = filterText => {
  // If it's empty do not highlight anything
  const parent = document.querySelector("#unitSelectorBody");
  if (filterText === "") {
    parent.classList.remove("highlighting");
  } else {
    parent.classList.add("highlighting");
  }

  // Remove previous highlights
  const highlighted = Array.from(document.querySelectorAll(".unit-selector-icon.highlight"));
  highlighted.forEach(el => el.classList.remove("highlight"));

  // Add new
  filterUnits(filterText).forEach(el => el.classList.add("highlight"));
}

// toggleUnits toggles all unit matching `filterText`
const toggleUnits = filterText => {
  filterUnits(filterText).forEach(el => el.click());
}

// insertFilterElements inserts all the filtering stuff when modal is opened
const insertFilterElements = () => {
  const hook = document.querySelector("#unitSelectorBody");

  // Insert HTML Element
  const htmlElement = `
<div class="text-filter form-group">
    <input class="form-control" type="text" placeholder="Miyako" autofocus=autofocus/>
</div>
`;
  hook.insertAdjacentHTML("afterbegin", htmlElement);

  // Add Event Listeners
  const element = document.querySelector(".text-filter > input");
  element.addEventListener("keyup", e => {
    if (e.keyCode == "13") {
      toggleUnits(e.target.value);
      e.target.value = "";
    }
    highlightUnits(e.target.value);
  });

  // Focus
  window.setTimeout(() => { element.focus(); }, 0)
}

// insertModalOpenMutationObserver fires whenever unit filter modal is opened
const insertModalOpenMutationObserver = (callback) => {
  const modal = document.querySelector("#unitSelectorModal");
  const config = { attributes: true };

  const observer = new MutationObserver(callback);
  observer.observe(modal, config);
}

// insertSearchKeyboardShortcut just adds `/` shortcut to open unit filter
const insertSearchKeyboardShortcut = () => {
  document.addEventListener('keydown', e => {
    // Wrong key
    if (event.key !== '/') return;

    // Already open
    const modal = document.querySelector("#unitSelectorModal.show");
    if (modal) return;

    e.preventDefault();
    document.querySelector("#selectUnitsBtn").click();
  });
}

const main = () => {
  insertStylesheet()
  insertModalOpenMutationObserver(insertFilterElements);
  insertSearchKeyboardShortcut();
}

document.addEventListener("DOMContentLoaded", main);

});