import { color } from "d3";
import React, {
  Component,
  FC,
  useEffect,
  useState,
  useDeferredValue,
} from "react";
import * as d3 from "d3";
import * as bootstrap from "bootstrap/dist/js/bootstrap";

const HeapFlow: React.FC = () => {
  const [data, setData] = useState<any[]>();
  const [legends, setLegends] = useState<any[]>();
  const [eventsSize, setEventsSize] = useState<any>();
  const [currTimestamp, setCurrTimestamp] = useState(0);
  const [documentWidth, setDocumentWidth] = useState(window.innerWidth * 0.8);
  const [documentHeight, setDocumentHeight] = useState(0.0);
  const deferredcurrTimestamp = useDeferredValue(currTimestamp);
  const deferreddocumentWidth = useDeferredValue(documentWidth);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    window.bootstrap = require("bootstrap/dist/js/bootstrap.bundle.js");

    fetch("http://localhost:5000/api/events")
      .then((res) => res.json())
      .then((data) => setData(data["events"]))
      .catch((error) => console.error(error));

    fetch("http://localhost:5000/api/legends")
      .then((res) => res.json())
      .then((data) => setLegends(data["legends"]))
      .catch((error) => console.error(error));

    fetch("http://localhost:5000/api/events/size")
      .then((res) => res.json())
      .then((data) => {
        setEventsSize(data["size"]);
      })
      .catch((error) => console.error(error));

    setTimeout(() => {
      setCurrTimestamp(deferredcurrTimestamp + 1);
    }, 500);
  }, []);

  useEffect(() => {
    window.addEventListener("resize", () => {
      setDocumentWidth(window.innerWidth * 0.8);
    });
  }, []);

  useEffect(() => {
    setIsReady(false);
    update();
    addPopover();
    setIsReady(true);
  }, [deferredcurrTimestamp, deferreddocumentWidth]);


  const addPopover = () => {
    const script = document.createElement("script");
    const scriptText = document.createTextNode(
      "popoverTriggerList = document.querySelectorAll('[data-bs-toggle=\"popover\"]');popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))"
    );
    script.appendChild(scriptText);
    document.head.appendChild(script);
  };

  const  find_markers = (legends: any[]) => {
    var markers: any[] = [];
    legends.forEach((legend) => {
      if (legend["type"] == "marker") {
        markers.push(legend);
      }
    });
    return markers;
  }

  const renderVisualization = (
    events_to_draw: any[],
    svg: any,
    markers: any[]
  ) => {
    events_to_draw.forEach((event_to_draw) => {
      let x = event_to_draw["x"];
      let y = event_to_draw["y"];
      let width = event_to_draw["width"];
      let height = event_to_draw["height"];
      let event = event_to_draw["event"];

      svg
        .append("text")
        .attr("x", x)
        .attr("y", y - 5)
        .text(event.ptr)
        .attr("font-family", "sans-serif")
        .attr("font-size", "8px");

      svg
        .append("rect")
        .attr("x", x)
        .attr("y", y)
        .attr("width", width)
        .attr("height", height)
        .attr("class", "square")
        .attr("data-bs-toggle", "popover")
        .attr("data-bs-title", event.ptr)
        .attr("data-bs-html", "true")
        .attr("data-bs-content", () => {
          let content = "";
          for (let key in event) {
            if (key !== "ptr") {
              content += `${key}: ${event[key]}<br>`;
            }
          }
          return content;
        })
        .attr("data-bs-trigger", "hover")
        .attr("fill", () => {
          if (event.type === "free") {
            return "#fffff0";
          }
          if (event.color != null) {
            return event.color;
          }
          if (event.call_site === "alloc") {
            return "#550000";
          } else if (event.call_site === "padding") {
            return "#ffaFF8";
          } else {
            return "#fffff0";
          }
        });

      svg
        .append("text")
        .attr("x", x + 10)
        .attr("y", y + 25)
        .text(event.size)
        .attr("font-family", "sans-serif")
        .attr("font-size", "10px");

      svg
        .append("rect")
        .attr("x", x + width - 8)
        .attr("y", y + height - 8)
        .attr("width", 5)
        .attr("height", 5)
        .attr("fill", () => {
          let color = "#000000";
          for (let marker of markers) {
            if (event.timestamp >= marker.timestamp) {
              color = marker.color;
            }
          }
          return color;
        });
    });
  };

  const calculateBlockLayout = (events_to_draw: any[]) => {
    var x = 0;
    var y = 30;
    var width = 0;
    var height = 50;
    var events_to_draw_with_metadata: any[] = [];
    for (let i = 0; i < events_to_draw.length; i++) {
      var event = events_to_draw[i];
      if (event["type"] == "alloc" || event["type"] == "free") {
        width = Math.log2(event["size"]) * 2 ** 3 + 60;
      } else {
        width = 100;
      }
      if (x + width > documentWidth) {
        x = 0;
        y += height + 25;
      }
      events_to_draw_with_metadata.push({
        x: Math.ceil(x % documentWidth),
        y: Math.floor(y),
        width: Math.floor(width),
        height: Math.floor(height),
        event: event,
      });
      x += width;
    }
    events_to_draw = events_to_draw_with_metadata;
    setDocumentHeight(y + 100);
    return events_to_draw;
  };

  // fonction draw
  const update = () => {
    // check data , legends, sizes are loaded
    if (!data || !legends || !eventsSize) {
      return;
    }

    // remove all previous items before render
    var svg = d3.select("svg");
    svg.selectAll("*").remove();

    // get the correct events to draw
    var events_to_draw: any[] = [];
    const events = data;
    for (let i = 0; i < events.length; i++) {
      var grouped_events = events[i];
      var j = 0;
      var last_event_peraddr: any = null;
      for (j = 0; j < grouped_events.length; j++) {
        var event = grouped_events[j];
        if (event["timestamp_index"] <= currTimestamp) {
          last_event_peraddr = event;
        }
      }
      events_to_draw.push(last_event_peraddr);
    }

    // remove null values
    events_to_draw = events_to_draw.filter(function (el) {
      return el != null;
    });

    // if no events to draw, return
    if (events_to_draw.length == 0) {
      return;
    }

    //compute x, y, width, height of each rect
    events_to_draw = calculateBlockLayout(events_to_draw);
    var markers: any[] = find_markers(legends);
    renderVisualization(events_to_draw, svg, markers);
  };


  let range = (
    <div className="row">
      <div className="col-12">
        <input
          type="range"
          id="range-value"
          className="form-range"
          min="0"
          max={eventsSize}
          defaultValue={currTimestamp}
          onChange={function (val) {
            document.getElementById("value").value = val.target.value;
            setCurrTimestamp(parseInt(val.target.value));
            setIsReady(false);
          }}
        />
        <input type="text" id="value" value={currTimestamp}></input>
      </div>
    </div>
  );

  let svg = (
    <svg
      width="100%"
      height={documentHeight}
      style={{ paddingTop: "30px", overflow: "visible" }}
    ></svg>
  );

  let loading = (
    <div className="row">
      <div className="col-12">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  );

  if (!isReady) {
    return (
        <div className="container" style={{ width: "100%", maxWidth: "10000px" }}>
        {loading}
        {svg}
      </div>
    );
  }

  return (
    <div className="container" style={{ width: "100%", maxWidth: "10000px" }}>
      {range}
      {svg}
    </div>
  );
};


export default HeapFlow;