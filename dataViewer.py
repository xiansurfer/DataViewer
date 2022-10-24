# @Time     :2022/9/20 14:29
# @Author   :LuXin
# @Function :

import pandas as pd
from dash import Dash,dcc,callback_context
import dash_uploader as du
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State
import  os
import plotly.graph_objs as go
import webbrowser
import sys
app = Dash(__name__)

# 配置上传文件夹
foldername = 'temp'
# if os.path.exists(foldername):
#     os.system(f"rd/s/q  {foldername}")
du.configure_upload(app, folder=foldername)

def single_plot(data,x,y_list):
    data_list = [
        {'x': data[x],
         'y': data[col],
         'name': col
         }
        for col in y_list
    ]
    data_dic = dict(
        data=data_list,
        layout=go.Layout(
            # title='%s井液面数据' % (wellname),
            xaxis=dict(title=x,tickmode='auto',nticks=10),
            # yaxis=dict(title='Depth'),
        )
    )

    layout = dcc.Graph(
        figure=data_dic
    )

    return layout

def multi_plot(data,x,y_list):
    color_list = [
        'cornflowerblue',
        'seagreen',
        'lightcoral',
        'coral',
        'cadetblue',
        'mediumslateblue',
        'teal',
        'tan',
    ]

    layout = []
    color_index = 0

    for col in y_list:
        data_list = [
            {'x': data[x],
             'y': data[col],
             'name': col
             }
        ]
        data_dic = dict(
            data=data_list,
            layout=go.Layout(
                # title='%s井液面数据' % (wellname),
                xaxis=dict(title=x,tickmode='auto',nticks=10),
                yaxis=dict(title=col),
                colorway=[color_list[color_index]],



            )
        )
        title = html.H5(col,
                           style={
                               'font-size':'25px',
                               'text-align':'center'
                           })

        fig = dcc.Graph(figure=data_dic)
        layout.append(title)
        layout.append(fig)
        layout.append(html.Hr())
        color_index += 1
        if color_index == len(color_list):
            color_index = 0
    return html.Div(children=layout)

app.layout = html.Div([
    dbc.Container(
        [
            du.Upload(
                id='uploader',
                text='点击或拖动文件到此进行上传！',
                text_completed='已完成上传文件：',
                default_style={
                    'font-size':'28px',
                    "font-family":"黑体",
                    "font-weight":"bold"},
            ),
        ]
    ),
    html.Div([
        html.H5(
            '',
            id='upload_status',
            style={
                'font-size': '28px',
                'display':'inline-block'
                # 'margin-top': '70px',
            }
        ),
        html.Button(
            '重置',
            id='reset_button',
            n_clicks=0,
            style={

                # 'margin-top': '-50px',
                'margin-left': '45px',
                'width': '5rem',
                'height': '2rem',
                'display':'inline-block'
            }
        )

    ]),
    dbc.Container(
        id='continar',
    ),
    html.H5(
        '请选择x轴(单选)',
        id='x_label',
        style={
            'font-size': '28px',
            'margin-top': '-30px',
        }
    ),
    dcc.Dropdown(id="choosen_x",
                 options=[],
                 style={
                     'margin-top': '-30px'
                 }),
    html.H5(
        '请选择y轴(多选)',
        id='y_label',
        style={
            'font-size': '28px',
            'margin-top': '20px',
        }
    ),
    dcc.Dropdown(id="choosen_y",
                 options=[],
                 multi=True,
                 style={
                     'margin-top': '-30px'
                 }),
    html.H5(
        '请选择绘图方式',
        id='how_to_drow',
        style={
            'font-size': '28px',
            'margin-top': '20px',
        }
    ),
    dcc.RadioItems(
        [
            {
                'label': '多子图',
                'value': 'multi'
            },
            {
                'label': '单主图',
                'value': 'single'
            }
        ]
        ,
        style={
            'margin-top': '-20px',
            'display': 'inline-block'
        },
        value='multi',
        id='draw_para'
    ),
    dbc.Container(
        id='img_continar',
    ),
    dcc.Store('data',data=None)

]
)

@app.callback(
    Output('upload_status', 'children'),
    Output('data', 'data'),
    Output('choosen_x', 'options'),
    Output('choosen_y', 'options'),
    Output('choosen_x', 'value'),
    Output('choosen_y', 'value'),
    Input('uploader', 'isCompleted'),
    State('uploader', 'fileNames'),
    Input('reset_button', 'n_clicks'),
)
def data_upload(isCompleted, fileNames,reset_btn):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    reset = 'reset_button' in changed_id
    if reset:
        os.system(f"rd/s/q  {foldername}")
        return '没有文件被加载',None,[],[],None,None
    elif isCompleted:
        load_path = ''
        for roots,dirs,files in os.walk('temp'):
            for file in files:
                if file == fileNames[0]:
                    load_path = os.path.join(roots,file)
                    break

        file_type = load_path.split('.')[-1]

        if file_type == 'csv':
            data = pd.read_csv(load_path,
                               error_bad_lines=False)
        else:
            data = pd.read_excel(load_path)

        columns = list(data.columns)
        os.system(f"rd/s/q  {foldername}")
        return f"{fileNames[0]}加载完毕",data.to_dict(),columns,columns,None,None
    else:
        os.system(f"rd/s/q  {foldername}")
        return '没有文件被加载',None,[],[],None,None

@app.callback(
    Output('img_continar', 'children'),
    Input('data', 'data'),
    Input('choosen_x', 'value'),
    Input('choosen_y', 'value'),
    Input('draw_para', 'value'),

)
def data_show(data,x,y_list,draw_para):
    data = pd.DataFrame(data)

    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    if not data.empty and x and y_list:
        if draw_para == 'multi':
            layout = multi_plot(data,x,y_list)
            return layout
        else:
            layout = single_plot(data,x,y_list)
            return layout
    else:
        return ''

if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:8051")
    app.run_server(debug=False, port=8051)



