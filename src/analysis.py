import csv
import json
import logging

logger = logging.getLogger('analysis')


def compute_overlaps(named_lists, threshold):
    """
    Computes a graph from a dict of lists where weights are the number of overlapping values.

    The graph is filtered by `threshold` meaning that overlaps below that number would not be recorded.
    """

    logger.info("Computing an overlap graph...")

    graph = {}
    visited = set()

    # Convert lists to sets prematurely to avoid doing that multiple times when calculating overlap
    for k, v in named_lists.items():
        named_lists[k] = set(v)

    size = len(named_lists)
    current = 0

    for key_a, value_a in named_lists.items():
        connections = {}

        current += 1
        logger.debug('Computing overlaps for %s (%d/%d)...', key_a, current, size)

        for key_b, value_b in named_lists.items():
            # Skip the node if already processed or if looking at itself
            if key_a == key_b or key_b in visited:
                continue

            # Calculate the overlap by set intersection
            overlap = len(value_a & value_b)

            if overlap > threshold:
                connections[key_b] = overlap

        logger.debug('%s had %d overlaps', key_a, len(connections))

        graph[key_a] = connections
        visited.add(key_a)

    logger.info("Finished computing overlaps")

    return graph


def update_data(current_user_data, filename):
    """
    Merges `current_user_data` with the data from the file `filename` and writes the result to that file.

    This operation is idempotent.
    """

    try:
        stored_data = read_data(filename)
        logger.info("Merging new data into stored")

        for k, v in current_user_data.items():
            if existing := stored_data.get(k):
                stored_data[k] = list(set(existing) | set(v))
            else:
                stored_data[k] = v
    except:
        logger.info("No stored data found")
        stored_data = current_user_data

    logger.info("Writing new data to file %s", filename)

    with open(filename, 'w') as f:
        json.dump(stored_data, f)


def read_data(filename):
    """
    Just reads json viewer data from file `filename` into a Python structure
    """

    logger.info("Reading stored viewer data from %s", filename)

    with open(filename) as f:
        return json.load(f)


def write_gephi_edges(graph, filename):
    """
    Writes a weighted undirected graph into a Gephi-compatible CSV edge-list file
    """

    logger.info("Exporting graph as a Gephi CSV edge list file %s", filename)

    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Source", "Target", "Weight"])
        for node_a, connections in graph.items():
            for node_b, weight in connections.items():
                writer.writerow([node_a, node_b, weight])


def write_gephi_labels(named_lists, filename):
    """
    Writes a dict of lists into a Gephi-compatible CSV node-list file
    """

    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Label", "Count"])
        for key, values in named_lists.items():
            writer.writerow([key, key, len(values)])


def generate_gephi_graph(filename, gephi_graph_name, gephi_labels_name, overlap_threshold=300):
    """
    Exports data from file `filename` into Gephi CSV graph and label files
    """

    viewer_data = read_data(filename)

    overlap_graph = compute_overlaps(viewer_data, overlap_threshold)

    logger.info("Exporting overlap graph as a Gephi CSV edges file %s", filename)
    write_gephi_edges(overlap_graph, gephi_graph_name)

    logger.info("Exporting viewer data as a Gephi CSV labels file %s", filename)
    write_gephi_labels(viewer_data, gephi_labels_name)
