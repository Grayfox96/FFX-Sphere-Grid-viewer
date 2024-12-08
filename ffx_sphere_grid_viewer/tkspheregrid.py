import copy
import tkinter as tk
from dataclasses import dataclass
from enum import StrEnum
from itertools import chain, islice, product
from logging import getLogger
from math import cos, dist, radians, sin
from tkinter import font

from .data.layout import Layout
from .data.node import Node
from .data.node_types import NODE_TYPES, AppearanceType


class Tag(StrEnum):
    LINK = 'link'
    HIGHLIGHTED_LINK = 'highlighted_link'
    NODE_CIRCLE = 'node_circle'
    NODE_TEXT = 'node_text'
    NODE_BIG_CIRCLE = 'node_big_circle'
    NODE_LINE = 'node_line'
    FLAG_TEXT = 'flag_text'
    FLAG_LINE = 'flag_line'


@dataclass
class TkNode:
    node: Node
    circle: int
    polygon: int | None
    text: int
    big_circle: int | None = None
    line: int | None = None

    def __str__(self) -> None:
        return f'Tk{self.node}'


@dataclass
class TkCharacterFlag:
    rectangle: int
    text: int
    line: int | None = None


class TkSphereGrid(tk.Canvas):
    def __init__(self, parent: tk.Widget, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.nodes: dict[int, TkNode] = {}
        self.character_flags: dict[int, TkCharacterFlag] = {}
        self.current_zoom = 1.0
        self.off_color = '#888888'
        default_font = font.nametofont('TkDefaultFont')
        self.font_family = default_font.cget('family')
        self.font_size = 10
        self.logger = getLogger(__name__)

    def resize_scrollregion(self) -> None:
        bbox = self.bbox('all')
        if bbox is None:
            return
        min_x, min_y, max_x, max_y = bbox
        min_x -= 100
        min_y -= 100
        max_x += 100
        max_y += 100
        self.configure(scrollregion=(min_x, min_y, max_x, max_y))

    def reset(self) -> None:
        self.delete('all')
        self.current_zoom = 1.0
        self.nodes.clear()
        self.character_flags.clear()

    def get_bbox_centre(self, item: int) -> tuple[float, float]:
        x0, y0, x1, y1 = self.bbox(item)
        return (x0 + x1) / 2, (y0 + y1) / 2

    def draw_layout(self, layout: Layout) -> None:
        layout = copy.deepcopy(layout)
        self.reset()
        for link in layout.links:
            if link.centre_node is None:
                self.create_line(link.node_1.x, link.node_1.y,
                                 link.node_2.x, link.node_2.y,
                                 width=LINK_WIDTH, tags=Tag.LINK)
                continue
            r = dist((link.node_1.x, link.node_1.y),
                     (link.centre_node.x, link.centre_node.y))
            angle_1 = round(link.angle_1)
            angle_2 = round(link.angle_2)
            start = min(angle_1, angle_2)
            extent = max(angle_1, angle_2) - start
            if extent >= 180:
                start = max(angle_1, angle_2)
                extent = 360 - extent
            self.create_arc(
                link.centre_node.x - r, link.centre_node.y - r,
                link.centre_node.x + r, link.centre_node.y + r,
                style='arc', start=start, extent=extent, width=LINK_WIDTH,
                tags=Tag.LINK)

        tk_nodes = []
        tk_nodes_actions = []
        for node in layout.nodes:
            if node.content is None:
                continue
            if node.content.appearance_type is AppearanceType.EMPTY_NODE:
                r = CIRCLE_RADIUS * EMPTY_NODE_CIRCLE_SCALE
            else:
                r = CIRCLE_RADIUS
            circle_tag = self.create_oval(
                node.x - r, node.y - r, node.x + r, node.y + r,
                width=CIRCLE_OUTLINE_WIDTH, fill=self.off_color,
                tags=Tag.NODE_CIRCLE)
            if node.content.appearance:
                coords = [(x + node.x - r, y + node.y - r)
                          for x, y in node.content.appearance]
                polygon_tag = self.create_polygon(*coords, fill='#ffffff')
            else:
                polygon_tag = None
            text_tag = self.create_text(
                node.x, node.y, text=node.content.display_name,
                fill=self.off_color, tags=Tag.NODE_TEXT,
                font=(self.font_family, self.font_size, 'bold'))
            tk_node = TkNode(node, circle_tag, polygon_tag, text_tag)
            if node.content.appearance_type in ACTIONS:
                tk_nodes_actions.append(tk_node)
            else:
                tk_nodes.append(tk_node)
            self.nodes[circle_tag] = tk_node
            self.nodes[polygon_tag] = tk_node
            self.nodes[text_tag] = tk_node

        # raise all the texts above the last polygon drawn
        self.tag_raise(Tag.NODE_TEXT, polygon_tag)

        for node in tk_nodes_actions:
            self.reposition_text(node)
        for node in tk_nodes:
            self.reposition_text(node)

        self.resize_scrollregion()
        self.logger.info('Changed Layout')

    def reposition_text(self, node: TkNode) -> None:
        if node.line is not None:
            self.delete(node.line)
            self.nodes.pop(node.line)
            node.line = None
        if node.node.content.display_name == '':
            return
        items_to_ignore = {node.text}
        centre_x, centre_y = self.get_bbox_centre(node.circle)
        text_centre_x, text_centre_y = self.get_bbox_centre(node.text)
        self.move(node.text, centre_x - text_centre_x, centre_y - text_centre_y)
        x0, y0, x1, y1 = self.bbox(node.text)
        # bounding box size is not the actual visual size of the text
        # removing a couple of units from each side as a workaround
        e = 2 * self.current_zoom
        for r, angle in product(range(20, 1000, 2), range(45, 360 + 45, 45)):
            x = r * self.current_zoom * cos(radians(angle))
            y = r * self.current_zoom * sin(radians(angle))
            items_overlapping = self.find_overlapping(x0 + x + e, y0 + y + e,
                                                      x1 + x - e, y1 + y - e)
            if set(items_overlapping) <= items_to_ignore:
                self.move(node.text, x, y)
                break
        if node.node.content.appearance_type not in ACTIONS:
            return
        if r < CIRCLE_RADIUS * 2 * self.current_zoom:
            return
        text_centre = self.get_bbox_centre(node.text)
        color = self.itemcget(node.text, 'fill')
        line_tag = self.create_line(
            centre_x, centre_y, *text_centre, fill=color,
            tags=Tag.NODE_LINE)
        if node.big_circle is not None:
            self.tag_lower(line_tag, node.big_circle)
        else:
            self.tag_lower(line_tag, node.circle)
        node.line = line_tag
        self.nodes[line_tag] = node

    def edit_node(self, event: tk.Event) -> None:
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        item_tag = self.find_closest(x, y)[0]  # returns a tuple with 1 item
        if item_tag not in self.nodes:
            self.logger.info(f'No Node found near ({x},{y})')
            return
        node = self.nodes[item_tag]
        if event.keysym not in KEY_TO_APPEARANCE_TYPE:
            self.logger.info(f'No Node Type found for key {event.keysym}')
            return
        appearance_type = KEY_TO_APPEARANCE_TYPE[event.keysym]
        if appearance_type is AppearanceType.L_1_LOCK:
            match node.node.content.appearance_type:
                case AppearanceType.L_1_LOCK:
                    appearance_type = AppearanceType.L_2_LOCK
                case AppearanceType.L_2_LOCK:
                    appearance_type = AppearanceType.L_3_LOCK
                case AppearanceType.L_3_LOCK:
                    appearance_type = AppearanceType.L_4_LOCK
                case _:
                    appearance_type = AppearanceType.L_1_LOCK
        if node.node.content.appearance_type is appearance_type:
            index = NODE_TYPES.index(node.node.content) + 1
            node_types = chain(islice(NODE_TYPES, index, None), NODE_TYPES)
        else:
            node_types = NODE_TYPES
        for node_type in node_types:
            if node_type.appearance_type is appearance_type:
                new_content = node_type
                break
        if node.node.content is node_type:
            return
        if (node.node.content.appearance_type == AppearanceType.EMPTY_NODE
                or new_content.appearance_type == AppearanceType.EMPTY_NODE):
            if node.node.content.appearance_type == AppearanceType.EMPTY_NODE:
                scale = 1 / EMPTY_NODE_CIRCLE_SCALE
            else:
                scale = EMPTY_NODE_CIRCLE_SCALE
            centre = self.get_bbox_centre(node.circle)
            self.scale(node.circle, *centre, scale, scale)
            if node.big_circle is not None:
                self.scale(node.big_circle, *centre, scale, scale)
        self.itemconfigure(node.text, text=new_content.display_name)
        if self.itemcget(node.circle, 'fill') != self.off_color:
            self.itemconfigure(node.circle, fill=new_content.color)
            self.itemconfigure(node.text, fill=new_content.color)
            if node.line is not None:
                self.itemconfigure(node.line, fill=new_content.color)
        if node.polygon is not None:
            self.delete(node.polygon)
            self.nodes.pop(node.polygon)
        if new_content.appearance:
            x0, y0, *_ = self.coords(node.circle)
            coords = [(x * self.current_zoom + x0,
                       y * self.current_zoom + y0)
                      for x, y in new_content.appearance]
            polygon = self.create_polygon(*coords, fill='#ffffff')
            self.tag_lower(polygon, node.text)
            node.polygon = polygon
            self.nodes[polygon] = node
        else:
            node.polygon = None
        node.node.content = new_content
        self.reposition_text(node)
        self.logger.info(f'Edited {node.node}')

    def on_scrollwheel(self, event: tk.Event) -> None:
        if event.delta > 0:
            zoom_level = self.current_zoom + ZOOM_STEP
        else:
            zoom_level = max(self.current_zoom - ZOOM_STEP, ZOOM_MIN, 0.1)
        self.set_zoom(zoom_level, event)

    def set_zoom(self,
                 zoom_level: float,
                 event: tk.Event | None = None,
                 ) -> None:
        scale_factor = zoom_level / self.current_zoom
        if event is not None:
            x, y = self.canvasx(event.x), self.canvasy(event.y)
            self.scale('all', x, y, scale_factor, scale_factor)
        else:
            self.scale('all', 0, 0, scale_factor, scale_factor)
        self.resize_scrollregion()
        self.current_zoom *= scale_factor
        self.itemconfigure(
            Tag.LINK, width=LINK_WIDTH * self.current_zoom
        )
        self.itemconfigure(
            Tag.HIGHLIGHTED_LINK, width=LINK_WIDTH * 2 * self.current_zoom
        )
        self.itemconfigure(
            Tag.NODE_TEXT,
            font=(self.font_family, int(self.font_size * self.current_zoom)))
        self.itemconfigure(
            Tag.FLAG_TEXT,
            font=(self.font_family, int(self.font_size * 2 * self.current_zoom)))
        self.itemconfigure(
            Tag.FLAG_LINE, width=LINK_WIDTH * self.current_zoom
        )
        self.logger.info(f'Set zoom to {self.current_zoom:.0%}')

    def highlight_all(self, _: tk.Event | None = None) -> None:
        for node in self.nodes.values():
            self.itemconfigure(node.circle, fill=node.node.content.color)
            self.itemconfigure(node.text, fill=node.node.content.color)
            if node.line is not None:
                self.itemconfigure(node.line, fill=node.node.content.color)
        self.logger.info('Highlighted all Nodes')

    def turn_off_all(self, _: tk.Event | None = None) -> None:
        self.itemconfigure(Tag.NODE_CIRCLE, fill=self.off_color)
        self.itemconfigure(Tag.NODE_TEXT, fill=self.off_color)
        self.itemconfigure(Tag.NODE_LINE, fill=self.off_color)
        self.logger.info('Turned off all Nodes')

    def highlight_nearest(self, event: tk.Event):
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        item_tag = self.find_closest(x, y)[0]  # returns a tuple with 1 item
        color = KEY_TO_CHAR_COLOR[event.keysym]
        if item_tag in self.nodes:
            node = self.nodes[item_tag]
            if self.itemcget(node.circle, 'fill') == self.off_color:
                self.itemconfigure(node.circle, fill=node.node.content.color)
                self.itemconfigure(node.text, fill=node.node.content.color)
                if node.line is not None:
                    self.itemconfigure(node.line, fill=node.node.content.color)
                self.logger.info(f'Highlighted {node.node}')
            else:
                self.itemconfigure(node.circle, fill=self.off_color)
                self.itemconfigure(node.text, fill=self.off_color)
                if node.line is not None:
                    self.itemconfigure(node.line, fill=self.off_color)
                self.logger.info(f'Turned off {node.node}')
            return
        elif self.type(item_tag) == 'arc':  # noqa: E721
            link_width = LINK_WIDTH * self.current_zoom
            if self.itemcget(item_tag, 'outline') == color:
                self.itemconfigure(
                    item_tag, outline='black', width=link_width, tags=Tag.LINK
                    )
                self.logger.info(f'Turned off Link near ({x},{y})')
            else:
                self.itemconfigure(
                    item_tag, outline=color, width=link_width * 2,
                    tags=Tag.HIGHLIGHTED_LINK
                    )
                self.logger.info(f'Highlighted Link near ({x},{y})')
        elif self.type(item_tag) == 'line':  # noqa: E721
            link_width = LINK_WIDTH * self.current_zoom
            if self.itemcget(item_tag, 'fill') == color:
                self.itemconfigure(
                    item_tag, fill='black', width=link_width, tags=Tag.LINK
                    )
                self.logger.info(f'Turned off Link near ({x},{y})')
            else:
                self.itemconfigure(
                    item_tag, fill=color, width=link_width * 2,
                    tags=Tag.HIGHLIGHTED_LINK
                    )
                self.logger.info(f'Highlighted Link near ({x},{y})')
        else:
            self.logger.info(f'No item found near ({x},{y})')

    def add_character_flag(self, event: tk.Event) -> None:
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        item_tags = self.find_withtag('current')
        if item_tags and item_tags[0] in self.character_flags:
            tk_character_flag = self.character_flags[item_tags[0]]
            self.character_flags.pop(tk_character_flag.rectangle)
            self.character_flags.pop(tk_character_flag.text)
            self.delete(tk_character_flag.rectangle)
            self.delete(tk_character_flag.text)
            if tk_character_flag.line is not None:
                self.character_flags.pop(tk_character_flag.line)
                self.delete(tk_character_flag.line)
            self.logger.info(f'Deleted Character Flag @ ({x},{y})')
            return
        color = KEY_TO_CHAR_COLOR[event.keysym]
        name = KEY_TO_CHAR_NAME[event.keysym]
        text_tag = self.create_text(
            x, y, text=name, tags=Tag.FLAG_TEXT,
            font=(self.font_family, int(self.font_size * 2 * self.current_zoom)))
        coords = self.bbox(text_tag)
        rectangle_tag = self.create_rectangle(
            *coords, fill=color, outline=color)
        self.tag_lower(rectangle_tag, text_tag)
        big_circles = self.find_withtag(Tag.NODE_BIG_CIRCLE)
        if big_circles:
            distances = {dist(self.get_bbox_centre(bc), (x, y)): bc
                         for bc in big_circles}
            item_tag = distances[min(distances)]
            node = self.nodes[item_tag]
            centre = self.get_bbox_centre(node.circle)
            rectangle_centre = self.get_bbox_centre(rectangle_tag)
            line_tag = self.create_line(
                *centre, *rectangle_centre, tags=Tag.FLAG_LINE,
                width=LINK_WIDTH * self.current_zoom, fill=color
                )
            if node.big_circle is not None:
                self.tag_lower(line_tag, node.big_circle)
            else:
                self.tag_lower(line_tag, node.circle)
        else:
            line_tag = None
        tk_character_flag = TkCharacterFlag(rectangle_tag, text_tag, line_tag)
        self.character_flags[rectangle_tag] = tk_character_flag
        self.character_flags[text_tag] = tk_character_flag
        msg = f'Created Character Flag @ ({x}, {y})'
        if line_tag is not None:
            self.character_flags[line_tag] = tk_character_flag
            msg += f' connected to {node}'
        self.logger.info(msg)

    def add_character_circle(self, event: tk.Event) -> None:
        x, y = self.canvasx(event.x), self.canvasy(event.y)
        item_tag = self.find_closest(x, y)[0]  # returns a tuple with 1 item
        if item_tag not in self.nodes:
            self.logger.info(f'No Node found near ({x},{y})')
            return
        node = self.nodes[item_tag]
        if node.big_circle is not None:
            self.delete(node.big_circle)
            self.nodes.pop(node.big_circle)
            node.big_circle = None
            self.logger.info(f'Removed Character Ring from {node.node}')
            return
        color = KEY_TO_CHAR_COLOR[event.keysym.lower()]
        name = KEY_TO_CHAR_NAME[event.keysym.lower()]
        d = (BIG_CIRCLE_RADIUS - CIRCLE_RADIUS) * self.current_zoom
        if node.node.content.appearance_type is AppearanceType.EMPTY_NODE:
            d *= EMPTY_NODE_CIRCLE_SCALE
        x0, y0, x1, y1 = self.coords(node.circle)
        big_circle = self.create_oval(
            x0 - d, y0 - d, x1 + d, y1 + d, fill=color, outline=color,
            tags=Tag.NODE_BIG_CIRCLE)
        self.tag_lower(big_circle, node.circle)
        self.nodes[big_circle] = node
        node.big_circle = big_circle
        self.logger.info(f'Added Character Ring ({name}) to {node.node}')


CIRCLE_RADIUS = 20
CIRCLE_OUTLINE_WIDTH = 2
BIG_CIRCLE_RADIUS = CIRCLE_RADIUS + 4
EMPTY_NODE_CIRCLE_SCALE = 0.5
LINK_WIDTH = 4
ZOOM_STEP = 0.1
ZOOM_MIN = 0.1

KEY_TO_CHAR_COLOR = {
    'a': '#45b6ff',
    's': '#a5a5ff',
    'd': '#c50000',
    'f': '#4242ff',
    'g': '#dfa21a',
    'h': '#c021c0',
    'j': '#30be30',
}
KEY_TO_CHAR_NAME = {
    'a': 'Tidus',
    's': 'Yuna',
    'd': 'Auron',
    'f': 'Kimahri',
    'g': 'Wakka',
    'h': 'Lulu',
    'j': 'Rikku',
}
KEY_TO_APPEARANCE_TYPE = {
    '1': AppearanceType.HP,
    '2': AppearanceType.MP,
    '3': AppearanceType.STRENGTH,
    '4': AppearanceType.DEFENSE,
    '5': AppearanceType.MAGIC,
    '6': AppearanceType.MAGIC_DEFENSE,
    '7': AppearanceType.AGILITY,
    '8': AppearanceType.LUCK,
    '9': AppearanceType.EVASION,
    '0': AppearanceType.ACCURACY,
    'q': AppearanceType.WHITE_MAGIC,
    'w': AppearanceType.BLACK_MAGIC,
    'e': AppearanceType.SKILL,
    'r': AppearanceType.SPECIAL,
    't': AppearanceType.EMPTY_NODE,
    'y': AppearanceType.L_1_LOCK,
    # 'y': AppearanceType.L_2_LOCK,
    # 'y': AppearanceType.L_3_LOCK,
    # 'y': AppearanceType.L_4_LOCK,
}
ACTIONS = {
    AppearanceType.WHITE_MAGIC,
    AppearanceType.BLACK_MAGIC,
    AppearanceType.SKILL,
    AppearanceType.SPECIAL,
}
