"use client";

import React from "react";
import type { ChartDefinition } from "@shared/analysis";
import { formatValue } from "@shared/analysis";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function ChartCard({ chart }: { chart: ChartDefinition }) {
  const commonProps = {
    data: chart.series,
    margin: { top: 12, right: 12, left: -10, bottom: 0 },
  };

  return (
    <article className="panel p-5">
      <p className="eyebrow">{chart.kind === "paired_bar" ? "Snapshot" : "Trend"}</p>
      <div className="mt-2 flex items-start justify-between gap-4">
        <div>
          <h3 className="font-display text-2xl text-ink">{chart.title}</h3>
          <p className="mt-2 max-w-md text-sm leading-6 text-ink/65">
            {chart.subtitle}
          </p>
        </div>
      </div>

      <div className="mt-6 h-72 rounded-[1.5rem] bg-sand/50 p-3">
        <ResponsiveContainer width="100%" height="100%">
          {chart.kind === "line" ? (
            <LineChart {...commonProps}>
              <CartesianGrid stroke="rgba(20, 35, 27, 0.08)" vertical={false} />
              <XAxis dataKey="fiscal_year" stroke="#5b665f" />
              <YAxis
                stroke="#5b665f"
                tickFormatter={(value) => formatValue(value, chart.formatter)}
              />
              <Tooltip
                formatter={(value: number) => formatValue(value, chart.formatter)}
                labelStyle={{ color: "#14231b" }}
                contentStyle={{
                  borderRadius: 18,
                  borderColor: "rgba(20, 35, 27, 0.1)",
                  background: "#fffdf9",
                }}
              />
              <Line
                type="monotone"
                dataKey="primary"
                stroke="#2e5b47"
                strokeWidth={3}
                dot={{ r: 4, fill: "#2e5b47" }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          ) : (
            <BarChart {...commonProps}>
              <CartesianGrid stroke="rgba(20, 35, 27, 0.08)" vertical={false} />
              <XAxis dataKey="fiscal_year" stroke="#5b665f" />
              <YAxis
                stroke="#5b665f"
                tickFormatter={(value) => formatValue(value, chart.formatter)}
              />
              <Tooltip
                formatter={(value: number) => formatValue(value, chart.formatter)}
                labelStyle={{ color: "#14231b" }}
                contentStyle={{
                  borderRadius: 18,
                  borderColor: "rgba(20, 35, 27, 0.1)",
                  background: "#fffdf9",
                }}
              />
              {chart.kind === "paired_bar" && <Legend />}
              <Bar
                dataKey="primary"
                fill="#2e5b47"
                radius={[10, 10, 0, 0]}
                name={chart.primary_label}
              />
              {chart.kind === "paired_bar" ? (
                <Bar
                  dataKey="secondary"
                  fill="#8f4c36"
                  radius={[10, 10, 0, 0]}
                  name={chart.secondary_label ?? "Secondary"}
                />
              ) : null}
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </article>
  );
}
