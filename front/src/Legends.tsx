
import { color } from 'd3';
import React, {Component, FC, useEffect, useState} from 'react';
import * as bootstrap from "react-bootstrap"; 




const Legends: React.FC = () => {
  const [legends, setLegends] = useState<any[]>();

  useEffect(() => {
      fetch("http://localhost:5000/api/legends")
          .then((res) => res.json())
          .then((data) => setLegends(data["legends"]))
          .catch((error) => console.error(error));
  }, []);

  if (!legends) {
      return <div>Loading...</div>;
  }

  return (

      <ul className="list-group col-12">
          {legends.map((legend) => (
              // set background color of the legend
              <li key={legend.id} className="list-group-item" style={{ backgroundColor: "rgb(181, 195, 248)", fontSize: "0.8vw", "overflow": "hidden" }}>
                  <div className="row">
                      <div className="circle" style={{ backgroundColor: legend.color, width: "15px", height: "15px" }}></div>
                      <div className="col-8">{legend.name} </div>
                  </div>
              </li>
          ))}
      </ul>
  );
};

export default Legends;

