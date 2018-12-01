import networkx
import plotly

from math import sqrt, cos, sin
from random import random
from itertools import combinations
from functools import reduce


HEAD_ANGLE = 0.5


graph_width = 800
graph_height = 450

node_size = 20
node_color = (255, 255, 255)

edge_width = 2
edge_color = (0, 0, 0)

node_label_position = 'middle center'
edge_label_distance = 10


def _normalize_positions(g):
    xs = []
    ys = []
    for n in g.nodes:
        pos = g.nodes[n]['pos']
        xs.append(pos[0])
        ys.append(pos[1])

    xmin = min(xs)
    ymin = min(ys)
    xmax = max(xs) - xmin
    ymax = max(ys) - ymin

    for n in g.nodes:
        pos = g.nodes[n]['pos']
        x = (pos[0] - xmin) / xmax
        y = (pos[1] - ymin) / ymax
        g.nodes[n]['pos'] = (x, y)


def _set_layout(g, layout):
    for n, value in layout.items():
        g.nodes[n]['pos'] = (value[0], value[1])

    _normalize_positions(g)


def _scale(dx, dy, width, height, size):
    s2 = size**2

    x2 = (dx * width)**2
    y2 = (dy * height)**2

    return sqrt(s2 / (x2 + y2))


def _rotate(dx, dy, width, height, counter):
    dx *= width
    dy *= height

    if counter:
        a = HEAD_ANGLE
    else:
        a = -HEAD_ANGLE

    rx = dx * cos(a) - dy * sin(a)
    ry = dx * sin(a) + dy * cos(a)

    return rx / width, ry / height


def _convert(color):
    return 'rgb({}, {}, {})'.format(color[0], color[1], color[2])


def _build_node_trace(color):
    if node_label_position == 'hover':
        hoverinfo = 'text'
        mode = 'markers'
    else:
        hoverinfo = 'none'
        mode = 'markers+text'

    fontcolor = (0, 0, 0)

    if node_label_position == 'middle center':
        if 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2] < 128:
            fontcolor = (255, 255, 255)

    return {
        'x': [],
        'y': [],
        'text': [],
        'textposition': 'middle center' if node_label_position == 'hover' else node_label_position,
        'hoverinfo': hoverinfo,
        'mode': mode,
        'marker': {
            'size': node_size,
            'color': _convert(color),
            'line': {
                'width': edge_width,
                'color': 'rgb(0, 0, 0)',
            },
        },
        'textfont': {
            'color': _convert(fontcolor),
        },
    }


def _build_edge_trace(color):
    return {
        'x': [],
        'y': [],
        'hoverinfo': 'none',
        'mode': 'lines',
        'line': {
            'width': edge_width,
            'color': _convert(color),
        },
    }


def _build_label_trace():
    return {
        'x': [],
        'y': [],
        'text': [],
        'textposition': 'middle center',
        'hoverinfo': 'none',
        'mode': 'text',
        'textfont': {
            'color': 'rgb(0, 0, 0)',
        },
    }


def _build_layout(width, height):
    return {
        'showlegend': False,
        'width': width,
        'height': height,
        'margin': {
            'b': 0,
            'l': 0,
            'r': 0,
            't': 0,
        },
        'xaxis': {
            'showgrid': False,
            'zeroline': False,
            'showticklabels': False,
        },
        'yaxis': {
            'showgrid': False,
            'zeroline': False,
            'showticklabels': False,
        },
    }


def _add_node(g, n, node_trace):
    x, y = g.nodes[n]['pos']

    node_trace['x'].append(x)
    node_trace['y'].append(y)


def _add_edge(g, e, edge_trace, label_trace):
    x0, y0 = g.nodes[e[0]]['pos']
    x1, y1 = g.nodes[e[1]]['pos']

    dx = y0 - y1
    dy = x1 - x0

    # parameters estimated from screenshots
    width = 0.9 * graph_width - 24
    height = 0.9 * graph_height - 24

    if isinstance(g, networkx.DiGraph) and g.has_edge(e[1], e[0]):
        scale = _scale(dx, dy, width, height, edge_width)
        x0 += dx * scale
        y0 += dy * scale
        x1 += dx * scale
        y1 += dy * scale

    edge_trace['x'].extend([x0, x1, None])
    edge_trace['y'].extend([y0, y1, None])

    if label_trace is not None:
        scale = _scale(dx, dy, width, height, edge_label_distance)
        label_trace['x'].append((x0 + x1) / 2 + dx * scale)
        label_trace['y'].append((y0 + y1) / 2 + dy * scale)
        label_trace['text'].append(g.edges[e[0], e[1]]['label'])

    if isinstance(g, networkx.DiGraph):
        dx = x0 - x1
        dy = y0 - y1

        radius = node_size / 2

        scale = _scale(dx, dy, width, height, radius)
        x0 = x1 + dx * scale
        y0 = y1 + dy * scale

        if not g.has_edge(e[1], e[0]):
            rx, ry = _rotate(dx, dy, width, height, True)
            scale = _scale(rx, ry, width, height, radius)
            x1 = x0 + rx * scale
            y1 = y0 + ry * scale
            edge_trace['x'].extend([x0, x1, None])
            edge_trace['y'].extend([y0, y1, None])

        rx, ry = _rotate(dx, dy, width, height, False)
        scale = _scale(rx, ry, width, height, radius)
        x1 = x0 + rx * scale
        y1 = y0 + ry * scale
        edge_trace['x'].extend([x0, x1, None])
        edge_trace['y'].extend([y0, y1, None])


def reset_node_colors(g):
    for n in g.nodes:
        g.nodes[n]['color'] = node_color


def reset_edge_colors(g):
    for e in g.edges:
        g.edges[e[0], e[1]]['color'] = edge_color


def set_circle_positions(g):
    layout = networkx.circular_layout(g)

    _set_layout(g, layout)


def set_spring_positions(g):
    layout = networkx.spring_layout(g)

    _set_layout(g, layout)


def reset_positions(g):
    layout = networkx.spring_layout(g)

    _set_layout(g, layout)


def load_graph(path, has_pos=False):
    g = networkx.read_gml(path, label='id')

    reset_node_colors(g)
    reset_edge_colors(g)

    if has_pos:
        for n in g.nodes:
            g.nodes[n]['pos'] = (g.nodes[n]['x'], g.nodes[n]['y'])
            del g.nodes[n]['x']
            del g.nodes[n]['y']

        _normalize_positions(g)
    else:
        reset_positions(g)

    return g


def show_graph(g, nlab=False, elab=False):
    node_traces = {}

    for n in g.nodes:
        color = g.nodes[n]['color']
        if color not in node_traces:
            node_traces[color] = _build_node_trace(color)
        _add_node(g, n, node_traces[color])
        if nlab:
            node_traces[color]['text'].append(g.nodes[n]['label'])

    edge_traces = {}

    if elab:
        label_trace = _build_label_trace()
    else:
        label_trace = None

    for e in g.edges:
        color = g.edges[e[0], e[1]]['color']
        if color not in edge_traces:
            edge_traces[color] = _build_edge_trace(color)
        _add_edge(g, e, edge_traces[color], label_trace)

    data = list(edge_traces.values()) + list(node_traces.values())
    if elab:
        data.append(label_trace)

    figure = {
        'data': data,
        'layout': _build_layout(graph_width, graph_height),
    }

    plotly.offline.iplot(figure, config={'displayModeBar': False}, show_link=False)


def generate_frame(g, nlab=False, elab=False):
    node_traces = []

    for n in g.nodes:
        trace = _build_node_trace(g.nodes[n]['color'])
        node_traces.append(trace)
        _add_node(g, n, trace)
        if nlab:
            trace['text'].append(g.nodes[n]['label'])

    edge_traces = []

    if elab:
        label_trace = _build_label_trace()
    else:
        label_trace = None

    for e in g.edges:
        trace = _build_edge_trace(g.edges[e[0], e[1]]['color'])
        edge_traces.append(trace)
        _add_edge(g, e, trace, label_trace)

    data = edge_traces + node_traces
    if elab:
        data.append(label_trace)

    return {
        'data': data,
    }


def show_animation(frames):
    steps = []

    for index, frame in enumerate(frames):
        frame['name'] = index
        steps.append({
            'args': [[index], {'frame': {'redraw': False}, 'mode': 'immediate'}],
            'label': '',
            'method': 'animate',
        })

    # parameters estimated from screenshots
    width = 1.05 * graph_width + 72
    height = 1.00 * graph_height + 76

    layout = _build_layout(width, height)

    layout.update({
        'updatemenus': [
            {
                'buttons': [
                    {
                        'args': [None, {'frame': {'redraw': False}, 'fromcurrent': True}],
                        'label': 'Play',
                        'method': 'animate',
                    },
                    {
                        'args': [[None], {'frame': {'redraw': False}, 'mode': 'immediate'}],
                        'label': 'Pause',
                        'method': 'animate',
                    },
                ],
                'showactive': True,
                'type': 'buttons',
            },
        ],
        'sliders': [
            {
                'currentvalue': {'visible': False},
                'steps': steps,
            },
        ],
    })

    figure = {
        'data': frames[0]['data'],
        'layout': layout,
        'frames': frames,
    }

    plotly.offline.iplot(figure, config={'displayModeBar': False}, show_link=False)


def build_matrix(g):
    return networkx.to_numpy_matrix(g)


def build_closeness(g):
    closeness = networkx.closeness_centrality(g)

    for n in closeness:
        g.nodes[n]['theoretical_closeness'] = closeness[n]


def build_betweenness(g):
    betweenness = networkx.betweenness_centrality(g)

    for n in betweenness:
        g.nodes[n]['theoretical_betweenness'] = betweenness[n]


def build_shortest_paths(g, s, t):
    for n in g.nodes:
        g.nodes[n]['shortest_neighbors'] = set()

    for path in networkx.all_shortest_paths(g, s, t):
        for i in range(len(path) - 1):
            g.nodes[path[i]]['shortest_neighbors'].add(path[i + 1])

    for n in g.nodes:
        g.nodes[n]['shortest_neighbors'] = list(g.nodes[n]['shortest_neighbors'])
        g.nodes[n]['shortest_neighbors'].sort()


def randomize_positions(g):
    for n in g.nodes:
        x = random()
        y = random()
        g.nodes[n]['pos'] = (x, y)


def generate_empty_graph(num_nodes):
    g = networkx.empty_graph(num_nodes)

    reset_node_colors(g)

    randomize_positions(g)

    return g


def generate_complete_graph(num_nodes):
    g = networkx.complete_graph(num_nodes)

    reset_node_colors(g)
    reset_edge_colors(g)

    randomize_positions(g)

    return g


def update_positions(g, weight=None):
    pos = {n: g.nodes[n]['pos'] for n in g.nodes}

    layout = networkx.spring_layout(g, pos=pos, iterations=1, weight=weight)

    _set_layout(g, layout)


def largest_component(g):
    return max(networkx.algorithms.components.connected_component_subgraphs(g), key=len)


def average_distance(g):
    return networkx.algorithms.shortest_paths.generic.average_shortest_path_length(g)


def average_clustering_coefficient(g):
    return networkx.algorithms.cluster.average_clustering(g)


def global_clustering_coefficient(g):
    num_nodes = g.number_of_nodes()

    nodes = list(g.nodes)

    has_cache = [
        [
            int(g.has_edge(nodes[i], nodes[j])) if i < j else None
            for j in range(num_nodes)
        ]
        for i in range(num_nodes)
    ]

    num_cache = [(0, 0), (0, 0), (0, 1), (3, 3)]

    def _mapping(x):
        return num_cache[has_cache[x[0]][x[1]] + has_cache[x[0]][x[2]] + has_cache[x[1]][x[2]]]

    def _reduction(x, y):
        return (x[0] + y[0], x[1] + y[1])

    num_closed, num_connected = reduce(_reduction, map(_mapping, combinations(range(num_nodes), 3)))

    return num_closed / num_connected


plotly.offline.init_notebook_mode(connected=True)
