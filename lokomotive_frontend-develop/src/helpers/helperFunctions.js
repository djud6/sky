export function filterIssue(issues, issueID) {
  let filteredIssues = issues.filter((issue) => issue.issue_id === issueID);
  return filteredIssues.length !== 0 ? filteredIssues[0] : null;
}

export function formatIssueTitle(issue) {
  return (
    issue &&
    `${issue.custom_id} - ${issue.issue_title}, (${issue.is_resolved ? "Resolved" : "Unresolved"})`
  );
}

export function isChrome() {
  return /Chrome/.test(navigator.userAgent) && /Google Inc/.test(navigator.vendor);
}

export function capitalize(s) {
  if (typeof (s)==='string') return s.charAt(0).toUpperCase() + s.slice(1);
  else return;
}

export function isEmptyString(str) {
  return str.trim().length === 0;
}

export function isAndroid() {
  var userAgent = navigator.userAgent.toLowerCase();
  return userAgent.indexOf("android") > -1;
}

export function isMobileDevice() {
  return /Android|webOS|iPhone|iPad|iPod|Opera Mini/i.test(navigator.userAgent);
}

export function persistSetTab(e, history) {
  if ("URLSearchParams" in window) {
    let searchParams = new URLSearchParams(window.location.search);
    searchParams.set("tab", e.index);
    let newRelativePathQuery = window.location.pathname + "?" + searchParams.toString();
    history.replace(newRelativePathQuery);
  }
}

export function persistGetTab(setActiveIndex) {
  if ("URLSearchParams" in window) {
    const urlParams = new URLSearchParams(window.location.search);
    const myParam = urlParams.get("tab");
    if (myParam) setActiveIndex(parseInt(myParam));
  }
}

export function validateEmail(elementValue) {
  var emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailPattern.test(elementValue);
}
