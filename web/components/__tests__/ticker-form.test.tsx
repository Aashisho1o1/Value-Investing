import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { TickerForm } from "@/components/ticker-form";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push,
  }),
}));

describe("TickerForm", () => {
  it("routes to the analysis page with an uppercase ticker", async () => {
    const user = userEvent.setup();
    render(<TickerForm />);

    const input = screen.getByLabelText("Ticker");
    await user.clear(input);
    await user.type(input, "msft");
    await user.click(screen.getByRole("button", { name: "Analyze" }));

    expect(push).toHaveBeenCalledWith("/analysis/MSFT");
  });
});
