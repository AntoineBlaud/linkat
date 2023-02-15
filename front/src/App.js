import { style } from 'd3';
import HeapFlow from './HeapFlow.tsx';
import Legends from './Legends.tsx';

function App() {
  return (
    <div className="container-fluid" style={{"overflow": "visible"}}>
      <div className={"row"}>
        <div className={"col-12 text-bg-light text-muted"}>
          Linux kernel allocation tracer
        </div>
      </div>
      <div className={"row"}>
        <div className={"col-sm-3 col-lg-2"}>
          <Legends />
          </div>
        <div className={"col-sm-9 col-lg-10"}>
          <HeapFlow />
        </div>
      </div>
    </div>
  )
}

export default App;
