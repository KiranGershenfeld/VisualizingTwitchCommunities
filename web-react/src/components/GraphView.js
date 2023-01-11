import React from 'react';
import Sigma from "sigma";
import Graph from "graphology";
import { parse } from "graphology-gexf/browser";
import { UndirectedGraph } from 'graphology';
import RawGraph from './webdata.gexf'
import { SigmaContainer } from "@react-sigma/core";
import "@react-sigma/core/lib/react-sigma.min.css";


class GraphView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {};
        this.LoadGexfToSigma = this.LoadGexfToSigma.bind(this)
      }
    
    LoadGexfToSigma(RawGraph)
    {
        const sigmaGraph = new UndirectedGraph();

        // Load external GEXF file:
        fetch(RawGraph)
        .then((res) => res.text())
        .then((gexf) => {
          // Parse GEXF string:
          const graphObj = parse(Graph, gexf);    
          
          graphObj.forEachNode(function(key, attrs){

            sigmaGraph.addNode(key, 
            { 
              x: attrs.x, 
              y: attrs.y, 
              label: attrs.label, 
              size: attrs.size / 10,
              color: attrs.color
            });

          });

          graphObj.forEachUndirectedEdge(function(key, attrs, source, target, sourceAttrs){
            // console.log(sourceAttrs.color)
            const colorVals = sourceAttrs.color.slice(4, -1)
            
            const newCol = `rgba(${colorVals},0.1)`
            if(source == 'speedgaming' || target == 'speedgaming')
            {
              console.log(newCol)
            }

            sigmaGraph.addEdgeWithKey(key, source, target,
            { 
              weight: attrs.weight / 10, 
              size: 0.1,
              color: newCol,
              width: 1,
            });
          });
        })

      return sigmaGraph;
    }

    componentDidMount() {

      const graph = this.LoadGexfToSigma(RawGraph)

      this.setState({graph: graph})

      this.setState({sigmaSettings: {
          // maxNodeSize: maxNodeSize,
          // maxEdgeSize: maxEdgeSize,
          autoRescale: false,
          minEdgeSize: 0.1,
          maxEdgeSize: 1,
          drawEdges: false,
      }})

        // Retrieve some useful DOM elements:
        // const container = document.getElementById("sigma-container") 
        // const zoomInBtn = document.getElementById("zoom-in") 
        // const zoomOutBtn = document.getElementById("zoom-out") 
        // const zoomResetBtn = document.getElementById("zoom-reset") 
        // const labelsThresholdRange = document.getElementById("labels-threshold") 

        // // Instanciate sigma:
        // const renderer = new Sigma(graph, container, {
        //   minCameraRatio: 0.1,
        //   maxCameraRatio: 10,
        // });
        // const camera = renderer.getCamera();

        // Bind zoom manipulation buttons
        // zoomInBtn.addEventListener("click", () => {
        //   camera.animatedZoom({ duration: 600 });
        // });
        // zoomOutBtn.addEventListener("click", () => {
        //   camera.animatedUnzoom({ duration: 600 });
        // });
        // zoomResetBtn.addEventListener("click", () => {
        //   camera.animatedReset({ duration: 600 });
        // });

        // Bind labels threshold to range input
        // labelsThresholdRange.addEventListener("input", () => {
        //   renderer.setSetting("labelRenderedSizeThreshold", +labelsThresholdRange.value);
        // });

        // Set proper range initial value:
        // labelsThresholdRange.value = renderer.getSetting("labelRenderedSizeThreshold") + "";
    }
  
    componentWillUnmount() {
    }

    render() {
      return (
          <SigmaContainer id='SigmaCanvas' style={{ height: "100vh", width: '100vw'}} graph={this.state.graph} renderer='canvas' settings={{ drawEdges: false    }} />
      )
    }}
export default GraphView;