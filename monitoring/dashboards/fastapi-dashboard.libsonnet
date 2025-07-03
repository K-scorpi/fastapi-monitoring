local g = import 'vendor/grafonnet/grafana.libsonnet';
local dashboard = g.dashboard;
local row = g.row;
local graph = g.graph;
local prometheus = g.datasource.prometheus;

{
  fastapiDashboard:: dashboard.new("FastAPI Metrics")
    .add_row(
      row.new("HTTP Requests")
        .add_panel(
          graph.new(
            title="Requests by Method",
            dataSource=prometheus,
            targets=[{expr: "http_requests_total{job=\"fastapi\"}"}]  // ← здесь заменён `=` на `:`
          )
        )
    )
    .add_row(
      row.new("Latency")
        .add_panel(
          graph.new(
            title="Request Latency (seconds)",
            dataSource=prometheus,
            targets=[{expr: "rate(http_request_latency_seconds_sum[5m]) / rate(http_request_latency_seconds_count[5m])"}]  // ← тоже заменён `=`
          )
        )
    ),
}