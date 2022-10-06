package com.example;
import org.openide.util.Lookup;
import org.gephi.project.api.*;
import org.gephi.graph.api.*;
import org.gephi.io.importer.api.*;
import org.gephi.layout.api.*;
import org.gephi.layout.plugin.*;
import org.gephi.layout.plugin.forceAtlas2.*;
import org.gephi.layout.plugin.labelAdjust.LabelAdjust;
import org.gephi.layout.plugin.force.StepDisplacement;
import org.gephi.layout.plugin.force.yifanHu.*;
import org.gephi.preview.api.PreviewController;
import org.gephi.preview.api.PreviewModel;
import org.gephi.preview.api.PreviewProperty;
import org.gephi.preview.types.DependantColor;
import org.gephi.preview.types.DependantOriginalColor;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.lang.Object.*;
import java.util.concurrent.TimeUnit;

import javax.imageio.ImageIO;

import org.gephi.io.processor.spi.*;
import org.gephi.io.exporter.api.*;
import org.gephi.io.exporter.preview.PNGExporter;

import java.awt.image.BufferedImage;

import java.awt.Color;
import java.awt.Font;



public class App 
{   
    public static void main(String[] args)
    {
        GraphModel graphModel = LoadGraph("C:/Code/AutoGephi/Demo/VaccineData.gexf");

        LayoutGraph(graphModel, 60);
        SetGraphPreview(graphModel);
    
        UndirectedGraph graph = graphModel.getUndirectedGraph();
        ExportGraph(graph);


        System.exit(0);
    }

    public static void SetGraphPreview(GraphModel graphModel)
    {
        //Preview
        PreviewModel model = Lookup.getDefault().lookup(PreviewController.class).getModel();
        //Node Label Properties
        model.getProperties().putValue(PreviewProperty.SHOW_NODE_LABELS, Boolean.TRUE);
        model.getProperties().putValue(PreviewProperty.NODE_LABEL_PROPORTIONAL_SIZE, Boolean.TRUE);
        model.getProperties().putValue(PreviewProperty.NODE_LABEL_FONT, new Font("Arial", Font.PLAIN, 18));

        model.getProperties().putValue(PreviewProperty.NODE_LABEL_COLOR, new DependantOriginalColor(Color.WHITE));

        model.getProperties().putValue(PreviewProperty.NODE_LABEL_OUTLINE_SIZE, 4.0f);
        model.getProperties().putValue(PreviewProperty.NODE_LABEL_OUTLINE_OPACITY, 40);
        model.getProperties().putValue(PreviewProperty.NODE_LABEL_OUTLINE_COLOR, new DependantColor (Color.BLACK));

        //Edge Properties
        model.getProperties().putValue(PreviewProperty.SHOW_EDGES, Boolean.TRUE);
        model.getProperties().putValue(PreviewProperty.EDGE_THICKNESS, 1.0);
        model.getProperties().putValue(PreviewProperty.EDGE_RESCALE_WEIGHT, Boolean.TRUE);
        model.getProperties().putValue(PreviewProperty.EDGE_RESCALE_WEIGHT_MIN, 0.1);
        model.getProperties().putValue(PreviewProperty.EDGE_RESCALE_WEIGHT_MIN, 1);

        //Image Properties
        model.getProperties().putValue(PreviewProperty.BACKGROUND_COLOR, Color.BLACK);

        return;
    }

    public static void LayoutGraph(GraphModel graphModel, int executionTime)
    {
        //Perform layout
        //Layout for 1 minute
        AutoLayout autoLayout = new AutoLayout(executionTime, TimeUnit.SECONDS);
        autoLayout.setGraphModel(graphModel);
        ForceAtlas2 firstStep = new ForceAtlas2(null);
        LabelAdjust secondStep = new LabelAdjust(null);
        // AutoLayout.DynamicProperty adjustBySizeProperty = AutoLayout.createDynamicProperty("Adjust by Sizes", Boolean.TRUE, 0.1f);//True after 10% of layout time
        // AutoLayout.DynamicProperty repulsionProperty = AutoLayout.createDynamicProperty("Repulsion strength", 500f, 0f);//500 for the complete period
        autoLayout.addLayout(firstStep, 0.5f);
        autoLayout.addLayout(
            secondStep, 
            0.5f
        );
        System.out.println("STARTING LAYOUT EXECUTION");
        autoLayout.execute();
        System.out.println("ENDING LAYOUT EXECUTION");
        return;
    }

    public static GraphModel LoadGraph(String filename)
    {
        //Init a project - and therefore a workspace
        ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
        pc.newProject();
        Workspace workspace = pc.getCurrentWorkspace();

        ImportController importController = Lookup.getDefault().lookup(ImportController.class);
        Container container;
        try {
            File file = new File(filename);
            container = importController.importFile(file);
            container.getLoader().setEdgeDefault(EdgeDirectionDefault.DIRECTED); //Force DIRECTED
            container.getLoader().setAllowAutoNode(false); //Don’t create missing nodes
            
        } catch (Exception ex) {
            ex.printStackTrace();
            return null;
        }
        //Append imported data to GraphAPI
        importController.process(container);

        GraphModel graphModel = Lookup.getDefault().lookup(GraphController.class).getGraphModel();

        return graphModel;
        
    }

    public static void ExportGraph(Graph graph)
    {
        // ExportController ec = Lookup.getDefault().lookup(ExportController.class);
        // PNGExporter exporter = (PNGExporter) ec.getExporter("png");
        // ByteArrayOutputStream baos = new ByteArrayOutputStream();
        // ec.exportStream(baos, exporter);
        // byte[] png = baos.toByteArray();
        // BufferedImage final_img = ImageIO.read(new ByteArrayInputStream(png));
        // File output_file = new File("NEW2.png");
        // ImageIO.write(final_img, "png", output_file);
        // return;
        //Export full graph
        ExportController ec = Lookup.getDefault().lookup(ExportController.class);
        System.out.println("CREATING EXPORTER");
        //Export only visible graph
        PNGExporter exporter = (PNGExporter) ec.getExporter("png"); //Get GEXF exporter
        // exporter.setExportVisible(true); //Only exports the visible (filtered) graph
        System.out.println("EXPORTING");

        try {
            ec.exportFile(new File("NEW.png"), exporter);
        } catch (IOException ex) {
            ex.printStackTrace();
        }
        System.out.println("ENDING");
        return;
    }   
}

