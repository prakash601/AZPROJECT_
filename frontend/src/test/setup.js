import '@testing-library/jest-dom'

// jsdom does not implement scrollIntoView — add a no-op polyfill
// so components that call el.scrollIntoView() don't throw in tests.
if (!Element.prototype.scrollIntoView) {
  Element.prototype.scrollIntoView = () => {}
}
