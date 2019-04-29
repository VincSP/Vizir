import base64
from collections import OrderedDict

import plotly.graph_objs as go
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
from dash.dependencies import Input, Output, State

from app import app, default_columns, logic_manager


class Images():
    @classmethod
    def load_data(cls, db_name, selected_ids, tag):
        images = logic_manager.images_from_tag(db_name, selected_ids, tag)
        data = {}
        for id_exp, ims_exp in images.items():
            for im_id, im_name in ims_exp.items():
                step = cls.get_image_step_from_name(im_name)
                if step not in data:
                    data[step] = {id_exp: im_id}
                else:
                    data[step].update({id_exp: im_id})
        data = OrderedDict(sorted(data.items()))
        return data
    
    @classmethod
    def load_images_from_step(cls, db_name, data, step):
        if step not in data:
            raise Error()
        imgs = {}
        for id_exp, id_im in data[step].items():
            im = logic_manager.file(db_name, id_im)
            im = base64.b64encode(im)
            im = 'data:image/png;base64,{}'.format(im.decode())
            img = html.Div(html.Img(id="image", src=im))
            imgs[id_exp] = img
        return imgs

    @classmethod
    def load_images_from_index(cls, db_name, data, index):
        step = list(data.keys())[index]
        imgs = cls.load_images_from_step(db_name, data, step)
        return imgs

    @classmethod
    def get_steps(cls, data):
        return list(data.keys())

    @classmethod
    def get_len(cls, data):
        return len(data)

    @classmethod
    def get_image_tag_from_name(cls, name):
        return name.rsplit('_', 1)[0]

    @classmethod
    def get_image_step_from_name(cls, name):
        return int(name.rsplit('_', 1)[1])



layout = html.Div([
    html.H3('Images'),
    html.Div(id='tab-data', style={'display': 'none'}),
    html.Div(id='image-storage', style={'display': 'none'}),
    html.Div(dcc.Dropdown(id='image-dropdown')),
    html.Div(children=[
        html.Div(children=[
            dcc.Slider(
                id='image-slider',
                min=0,
                max=0,
                value=0,
                dots=True,
                disabled=False,
                updatemode='drag',
                # handleLabel={"showCurrentValue": True,}
            )], style={'width': '100%', 'float': 'left', 'display': 'inline-block'}),
        html.Div(id='range_value', style={'width': '15%', 'float': 'right', 'display': 'inline-block'})
    ]),
    html.Div(id="image-container"),
])


@app.callback(Output('image-dropdown', 'options'),
              [Input('tab-data', 'data')])
def populate_image_dropdown(data_args):
    if data_args is None:
        return []
    selected_ids = data_args.get('selected_ids', [])
    db_name = data_args['db']
    image_tags = logic_manager.image_tags_from_ids(db_name, selected_ids)
    return [{'label': name, 'value': name} for name in image_tags]


@app.callback(Output('image-storage', 'data'),
              [Input('image-dropdown', 'value')],
              [State('tab-data', 'data')])
def get_image_data(tag, data_args):
    if data_args is None:
        return
    selected_ids = data_args.get('selected_ids', [])
    db_name = data_args['db']
    return Images().load_data(db_name, selected_ids, tag)


@app.callback(Output('image-container', 'children'),
              [Input('image-slider', 'value'),
               Input('image-storage', 'data')],
              [State('tab-data', 'data')])
def plot_images(slider_val, images, data_args):
    if data_args is None:
        return
    db_name = data_args['db']
    return list(Images().load_images_from_index(db_name, images, slider_val).values())


@app.callback(
    Output('image-slider', 'max'),
    [Input('image-storage', 'data')])
def set_max_image_slider(images):
    if images is None:
        return
    return Images().get_len(images) - 1


@app.callback(
    Output('image-slider', 'marks'),
    [Input('image-storage', 'data')])
def set_marks_image_slider(images):
    marks = {}
    i = 0
    for step in Images().get_steps(images):
        marks[i] = step
        i += 1
    return marks