import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";

class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

vi.stubGlobal("ResizeObserver", ResizeObserverMock);

Object.defineProperty(HTMLElement.prototype, "clientWidth", {
  configurable: true,
  value: 960,
});

Object.defineProperty(HTMLElement.prototype, "clientHeight", {
  configurable: true,
  value: 480,
});

HTMLElement.prototype.getBoundingClientRect = function getBoundingClientRect() {
  return {
    width: 960,
    height: 480,
    top: 0,
    left: 0,
    right: 960,
    bottom: 480,
    x: 0,
    y: 0,
    toJSON() {
      return {};
    },
  };
};
