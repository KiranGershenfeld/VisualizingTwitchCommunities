import py4j.GatewayServer;
import org.openide.util.Lookup;
import org.gephi.project.api.*;
import org.gephi.statistics.api.StatisticsController;
import org.gephi.statistics.api.StatisticsModel;
import org.gephi.statistics.plugin.Degree;
import org.gephi.statistics.plugin.GraphDistance;
import org.gephi.statistics.plugin.Modularity;
import org.gephi.statistics.plugin.WeightedDegree;
import org.gephi.appearance.api.AppearanceController;
import org.gephi.appearance.api.AppearanceModel;
import org.gephi.appearance.api.AttributeFunction;
import org.gephi.appearance.api.Function;
import org.gephi.appearance.api.Partition;
import org.gephi.appearance.api.PartitionFunction;
import org.gephi.appearance.plugin.PartitionElementColorTransformer;
import org.gephi.appearance.plugin.RankingLabelSizeTransformer;
import org.gephi.appearance.plugin.RankingNodeSizeTransformer;
import org.gephi.appearance.plugin.palette.Palette;
import org.gephi.appearance.plugin.palette.PaletteManager;
import org.gephi.datalab.api.AttributeColumnsController;
import org.gephi.filters.api.FilterController;
import org.gephi.filters.api.Query;
import org.gephi.filters.api.Range;
import org.gephi.filters.plugin.edge.EdgeWeightBuilder.EdgeWeightFilter;
import org.gephi.filters.plugin.graph.DegreeRangeBuilder.DegreeRangeFilter;
import org.gephi.graph.api.*;
import org.gephi.graph.api.Graph;
import org.gephi.io.importer.api.*;
import org.gephi.io.importer.plugin.database.EdgeListDatabaseImpl;
import org.gephi.io.importer.plugin.database.ImporterEdgeList;
import org.gephi.layout.api.*;
import org.gephi.layout.plugin.*;
import org.gephi.layout.plugin.forceAtlas2.*;
import org.gephi.layout.plugin.fruchterman.FruchtermanReingold;
import org.gephi.layout.plugin.labelAdjust.LabelAdjust;
import org.gephi.layout.plugin.openord.OpenOrdLayout;
import org.gephi.layout.plugin.scale.ExpandLayout;
import org.gephi.layout.plugin.scale.ContractLayout;

import org.gephi.layout.spi.Layout;
import org.gephi.layout.plugin.force.Displacement;
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
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import javax.imageio.ImageIO;

import org.gephi.io.processor.plugin.DefaultProcessor;
import org.gephi.io.processor.spi.*;
import org.gephi.io.database.drivers.PostgreSQLDriver;
import org.gephi.io.exporter.api.*;
import org.gephi.io.exporter.preview.PNGExporter;

import java.awt.image.BufferedImage;

import java.awt.Color;
import java.awt.Font;

public class App 
{   
    public static void main(String[] args)
    {
        // GatewayServer gatewayServer = new GatewayServer(new App());
        // gatewayServer.start();
        // System.out.println("Gateway Server Started");
        Run(7);
    }

    public static void Run(int batch_id)
    {
        System.out.println("Atlas Generation Started");
        // Init a project - and therefore a workspace
        ProjectController pc = Lookup.getDefault().lookup(ProjectController.class);
        pc.newProject();
        Workspace workspace = pc.getCurrentWorkspace();

        ImportController importController = Lookup.getDefault().lookup(ImportController.class);

        GraphModel graphModel = LoadGraph(importController, workspace, batch_id);

        LayoutGraph(graphModel);
        SetGraphPreview();
    
        UndirectedGraph graph = graphModel.getUndirectedGraph();
        ExportGraph(graph);

        System.exit(0);
    }

    public static void SetGraphPreview()
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
        model.getProperties().putValue(PreviewProperty.EDGE_OPACITY, 20);


        //Image Properties
        model.getProperties().putValue(PreviewProperty.BACKGROUND_COLOR, Color.BLACK);

        return;
    }

    public static void LayoutGraph(GraphModel graphModel)
    {
        Graph undirectedGraph = graphModel.getUndirectedGraph();
        //Apply graph filters 
        //Filter, remove degree < 10
        // Range range = new Range((int) 10, Integer.MAX_VALUE, 0, Integer.MAX_VALUE);
    
        System.out.println("Edge removal");
        int edgeWeightLowerBound = 1000;
        List<Edge> edgesToRemove = new ArrayList<>();
        for (Edge e : undirectedGraph.getEdges().toArray()) {
            if((double) e.getAttribute("Weight") < edgeWeightLowerBound)
            {
                edgesToRemove.add(e);
            }
        }
        if (!edgesToRemove.isEmpty()) {

            undirectedGraph.removeAllEdges(edgesToRemove);
        }

        System.out.println("before node removal graph contains node count: ");
        System.out.println(undirectedGraph.getNodeCount());

        int nodeCountLowerBound = 1 ;
        List<Node> nodesToRemove = new ArrayList<>();
        for (Node n : undirectedGraph.getNodes().toArray()) {
            
            Object count = n.getAttribute("count");
            if(count == null)
            {
                nodesToRemove.add(n);
            }
            else
            {
                if((long) count < nodeCountLowerBound)
                {
                    nodesToRemove.add(n);
                }
            }
        }
        if (!nodesToRemove.isEmpty()) {
            undirectedGraph.removeAllNodes(nodesToRemove);
        }
        System.out.println("After node removal graph contains node count: ");
        System.out.println(undirectedGraph.getNodeCount());

        //Filter, remove degree < 10
        FilterController filterController = Lookup.getDefault().lookup(FilterController.class);
        DegreeRangeFilter degreeFilter = new DegreeRangeFilter();
        degreeFilter.setRange(new Range(1, Integer.MAX_VALUE)); //Remove nodes with degree < 10
        Query query = filterController.createQuery(degreeFilter);
        GraphView view = filterController.filter(query);
        graphModel.setVisibleView(view); //Set the filter result as the visible view


        Modularity modularity = new Modularity();
        modularity.setResolution(0.4);
        modularity.setUseWeight(true);
        modularity.execute(graphModel);

        //Partition with ‘modularity_class’, just created by Modularity algorithm
        AppearanceController appearanceController = Lookup.getDefault().lookup(AppearanceController.class);
        AppearanceModel appearanceModel = appearanceController.getModel();

        Column modColumn = graphModel.getNodeTable().getColumn(Modularity.MODULARITY_CLASS);
        
        Function func2 = appearanceModel.getNodeFunction(modColumn, PartitionElementColorTransformer.class);
        Partition partition2 = ((PartitionFunction) func2).getPartition();

        Palette palette2 = PaletteManager.getInstance().randomPalette(partition2.size(undirectedGraph));

        int i =0;
        for (Object o: partition2.getValues(undirectedGraph)){
            partition2.setColor(o,palette2.getColors()[i]);
            i++;
        }
        appearanceController.transform(func2);

        Column rankingCol = graphModel.getNodeTable().getColumn("count");

        Function rankingNodeSize = appearanceModel.getNodeFunction(rankingCol, RankingNodeSizeTransformer.class);
        Function rankingLabelSize = appearanceModel.getNodeFunction(rankingCol, RankingLabelSizeTransformer.class);

        RankingNodeSizeTransformer rankingNodeSizeTransformer = rankingNodeSize.getTransformer();
        RankingLabelSizeTransformer rankingLabelSizeTransformer = rankingLabelSize.getTransformer();

        rankingNodeSizeTransformer.setMinSize(10f);
        rankingNodeSizeTransformer.setMaxSize(40f);

        rankingLabelSizeTransformer.setMinSize(0.3f);
        rankingLabelSizeTransformer.setMaxSize(0.4f);

        appearanceController.transform(rankingNodeSize);
        appearanceController.transform(rankingLabelSize);

        // Unused layouts
        // LabelAdjust labelAdjustStep = new LabelAdjust(null);
        // labelAdjustStep.setGraphModel(graphModel);
        // labelAdjustStep.setAdjustBySize(true);
        // labelAdjustStep.setSpeed(10.0);

        
        // YifanHuLayout yifanHuStep = new YifanHuLayout(null, new StepDisplacement(1f));
        // yifanHuStep.setGraphModel(graphModel);
        // yifanHuStep.setOptimalDistance(1000f);

        // OpenOrdLayout openOrdLayout = new OpenOrdLayout(null);

        // ExpandLayout expandLayout = new ExpandLayout(null, 1.05);

        // FruchtermanReingold fruchtermanReingoldStep = new FruchtermanReingold(null);


        //FORCE ATLAS INITIALIZATION
        ForceAtlas2 forceAtlasStep = new ForceAtlas2(null);
        forceAtlasStep.resetPropertiesValues();
        forceAtlasStep.setGraphModel(graphModel);
        // forceAtlasStep.setBarnesHutOptimize(true);
        // forceAtlasStep.setBarnesHutTheta(-100d);
        forceAtlasStep.setAdjustSizes(true);
        forceAtlasStep.setLinLogMode(true);
        forceAtlasStep.setOutboundAttractionDistribution(false);
        forceAtlasStep.setScalingRatio(5d);
        forceAtlasStep.setGravity(1d);
        forceAtlasStep.setEdgeWeightInfluence(0.45d);

        //RUN FIRST PHASE
        Layout firstAlgo = forceAtlasStep;
        int firstAlgoSteps = 2000;

        firstAlgo.initAlgo();
        
        System.out.println("FIRST PHASE EXECUTION");
        for (int k = 0; k < firstAlgoSteps; k++)
        {
            firstAlgo.goAlgo();
        }

        //CHANGE PARAMETERS AND RUN SECOND PHASE
        forceAtlasStep.setScalingRatio(1d);
        forceAtlasStep.setLinLogMode(false);
        forceAtlasStep.setEdgeWeightInfluence(0.28d);
        int secondAlgoSteps = 350;
        
        System.out.println("SECOND PHASE EXECUTION");
        for (int k = 0; k < secondAlgoSteps; k++)
        {
            firstAlgo.goAlgo();
        }

        //CHANGE PARAMETERS AND RUN THIRD PHASE
        forceAtlasStep.setScalingRatio(1.1d);
        forceAtlasStep.setLinLogMode(true);
        forceAtlasStep.setEdgeWeightInfluence(0.4d);
        int thirdAlgoSteps = 1000;
        
        System.out.println("THIRD PHASE EXECUTION");
        for (int k = 0; k < thirdAlgoSteps; k++)
        {
            firstAlgo.goAlgo();
        }

        System.out.println("ENDING LAYOUT EXECUTION");
        return;
    }

    public static GraphModel LoadGraph(ImportController importController, Workspace workspace, int batch_id)
    {
        System.out.println("STARTING LOAD GRAPH");
        // System.out.println(System.getenv("DB_PASSWORD"));

        //Load gephi from rdbms
        //Get controllers and models
        GraphModel graphModel = Lookup.getDefault().lookup(GraphController.class).getGraphModel();
        
        //Import database
        EdgeListDatabaseImpl db = new EdgeListDatabaseImpl();
        db.setDBName("wobbly-herder-2498.twitchatlas");
        db.setHost("free-tier4.aws-us-west-2.cockroachlabs.cloud");
        db.setUsername("kiran");
        db.setPasswd(System.getenv("DB_PASSWORD"));
        db.setPort(26257);
        db.setSQLDriver(new PostgreSQLDriver());

        db.setNodeQuery("SELECT c.url_name as id, c.url_name as label, c.view_minutes as count from channels c");
        db.setEdgeQuery("SELECT source, target, weight FROM channel_overlaps where batch_id=" + String.valueOf(batch_id));
    
        System.out.println("IMPORTING DATABASE");
        ImporterEdgeList edgeListImporter = new ImporterEdgeList();
        Container container = importController.importDatabase(db, edgeListImporter);
        container.getLoader().setEdgeDefault(EdgeDirectionDefault.UNDIRECTED);   //Force UNDIRECTED
        
        System.out.println("PROCESSING DATABASE");
        //Append imported data to GraphAPI
        importController.process(container, new DefaultProcessor(), workspace);

        System.out.println("ENDING LOAD GRAPH");
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
        //Export only visible graph
        PNGExporter exporter = (PNGExporter) ec.getExporter("png"); //Get GEXF exporter
        // exporter.setExportVisible(true); //Only exports the visible (filtered) graph

        //Set png options
        exporter.setHeight(5500);
        exporter.setWidth(5500);

        try {
            ec.exportFile(new File("../Images/GeneratedAtlas.png"), exporter);
        } catch (IOException ex) {
            ex.printStackTrace();
        }
        System.out.println("ENDING");
        return;
    }   
}

