import type * as p from "@bokehjs/core/properties";
import type { Dict } from "@bokehjs/core/types";
import type { GestureEvent, UIEvent, TapEvent } from "@bokehjs/core/ui_events";
import type { MultiLine } from "@bokehjs/models/glyphs/multi_line";
import type { Patches } from "@bokehjs/models/glyphs/patches";
import type { GlyphRenderer } from "@bokehjs/models/renderers/glyph_renderer";
import type { HasXYGlyph } from "@bokehjs/models/tools/edit/edit_tool";
import { PolyEditTool, PolyEditToolView } from "@bokehjs/models/tools/edit/poly_edit_tool";
export interface HasPolyGlyph {
    glyph: MultiLine | Patches;
}
export declare class PolyVertexEditToolView extends PolyEditToolView {
    model: PolyVertexEditTool;
    deactivate(): void;
    _pan(ev: GestureEvent): void;
    _pan_end(ev: GestureEvent): void;
    _drag_points(ev: UIEvent, renderers: (GlyphRenderer & HasXYGlyph)[]): number[][];
    _set_vertices(xs: number[] | number, ys: number[] | number, styles?: {
        [key: string]: unknown[];
    }): void;
    _move_linked(points: number[][]): void;
    _tap(ev: TapEvent): void;
    _show_vertices(ev: UIEvent): void;
}
export declare namespace PolyVertexEditTool {
    type Attrs = p.AttrsOf<Props>;
    type Props = PolyEditTool.Props & {
        end_style: p.Property<Dict<unknown>>;
        node_style: p.Property<Dict<unknown>>;
    };
}
export interface PolyVertexEditTool extends PolyVertexEditTool.Attrs {
}
export declare class PolyVertexEditTool extends PolyEditTool {
    properties: PolyVertexEditTool.Props;
    renderers: (GlyphRenderer & HasPolyGlyph)[];
    constructor(attrs?: Partial<PolyVertexEditTool.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=poly_edit.d.ts.map