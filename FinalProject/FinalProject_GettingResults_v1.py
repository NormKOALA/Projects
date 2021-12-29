import glob, os, re, math
import pandas as pd

from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()

batch_name = '10-50-50'
models = glob.glob('C:\\DataScience\\Training\\FinalProject\\data\\cfd_models\\'+batch_name+'\\*\\case\\pv.foam')

data = {'description':[]}

for i in range(4):
    for j in ['_min', '_max']:
        data['s'+str(i)+'-P'+j]=[]
        for u in ['Magnitude', 'X', 'Y', 'Z']:
            data['s'+str(i)+'-U'+u+j]=[]

for model in models:
    model_name = re.findall(r"\d+.+?[^\\]*", model)[1]
    data['description'].append(model_name) 

    model_param = model_name.split('-')

    # INLET
    ## Result loading
    openfoam_output = OpenFOAMReader(registrationName=model_name, FileName=model)
    openfoam_output.CaseType = 'Decomposed Case'
    openfoam_output.MeshRegions = ['patch/inlet']

    ## Viewpoint setting
    render_view = GetActiveViewOrCreate('RenderView')
    render_view.CameraParallelProjection = 1
    render_view.OrientationAxesVisibility = 0
    render_view.CameraPosition = [0, 0, -10]
    render_view.CameraFocalPoint = [0, 0, 0]
    render_view.CameraViewUp = [0, 1, 0]

    ## Setting the last increment to render
    increment = GetAnimationScene()
    increment.UpdateAnimationUsingDataTimeSteps()
    increment.AnimationTime = max(GetActiveSource().TimestepValues)

    current_source = GetActiveSource() # openfoam_output

    ## setting the color map
    pLUT = GetColorTransferFunction('p')
    pLUT.ApplyPreset('Viridis (matplotlib)', True)
    uLUT = GetColorTransferFunction('U')
    uLUT.ApplyPreset('Viridis (matplotlib)', True)

    merge_blocks = MergeBlocks(registrationName='merge_blocks', Input=current_source)
    merge_source = GetActiveSource()

    ## Rendering the result
    display = Show(merge_source, render_view, 'UnstructuredGridRepresentation')
    render_view.ResetCamera(True)
    Render()

    save_path = os.path.join('C:\DataScience\Training\FinalProject\data\cfd_results', batch_name)
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    screenshot_path = os.path.join(save_path, model_name)
    if not os.path.exists(screenshot_path):
        os.mkdir(screenshot_path)

    ## Taking screenshots
    ### Pressure distribution
    ColorBy(display, ('POINTS', 'p'))
    display.RescaleTransferFunctionToDataRange(True, False)
    data['s0-P_min'].append(openfoam_output.GetPointDataInformation().GetArray('p').GetRange()[0])
    data['s0-P_max'].append(openfoam_output.GetPointDataInformation().GetArray('p').GetRange()[1])
    SaveScreenshot(os.path.join(screenshot_path, 's0-P.png'),
                   render_view,
                   ImageResolution=[512, 512],
                   OverrideColorPalette='WhiteBackground',
                   TransparentBackground=1)

    ### Flow velocity distribution
    u_values = []
    u_ranges = {'X':0, 'Y':1, 'Z':2}

    for u in ['Magnitude', 'X', 'Y', 'Z']:
        ColorBy(display, ('POINTS', 'U', u))
        display.RescaleTransferFunctionToDataRange(True, False)
        if u != 'Magnitude':
            for i,j in enumerate(['_min', '_max']):
                value = openfoam_output.GetPointDataInformation().GetArray('U').GetRange(u_ranges[u])[i]
                u_values.append(value)
                data['s0-U'+u+j].append(value)
        SaveScreenshot(os.path.join(screenshot_path, 's0-U'+u+'.png'),
                       render_view,
                       ImageResolution=[512, 512],
                       OverrideColorPalette='WhiteBackground',
                       TransparentBackground=1)

    data['s0-UMagnitude_min'].append(min(u_values))
    data['s0-UMagnitude_max'].append(max(u_values))

    Hide(merge_source, render_view)
    Render()

    # SLICES & OUTLET
    current_source.MeshRegions = ['internalMesh']
#    render_view.Update()

    section_count = int((len(model_param)-1)/3)
    if section_count < 3:
        for i in range(3, section_count, -1):
            for j in ['_min', '_max']:
                data['s'+str(i)+'-P'+j].append(0)
                for u in ['Magnitude', 'X', 'Y', 'Z']:
                    data['s'+str(i)+'-U'+u+j].append(0)

#    current_source = GetActiveSource() # initial geom
#    Hide(current_source, render_view)
#    Render()

    for section in range(section_count):
        # rotating view
        rotate_angles = {'arc45':45, 'arc90':90, 'line':0}

        rotate_angle = rotate_angles[model_param[section+1+section_count]]

        rotate_axises = {'left':[0, -rotate_angle, 0],
                         'right':[0, rotate_angle, 0],
                         'top':[rotate_angle, 0, 0],
                         'down':[-rotate_angle, 0, 0]}

        rotate_axis = rotate_axises[model_param[section+1+2*section_count]]

        transform = Transform(registrationName='Rotate'+str(section), Input=current_source)
        transform.Transform = 'RotateAroundOriginTransform'
        transform.Transform.Rotate = rotate_axis

        current_source = GetActiveSource() # rotated geom

        # translating view
        if rotate_angle == 0:
            translate_Z = int(model_param[section+1])*0.001
            translate_XY = 0
        else:
            translate_Z = (math.sin(math.radians(rotate_angle))*int(model_param[section+1]))*0.001
            translate_XY = ((1-math.cos(math.radians(rotate_angle)))*int(model_param[section+1]))*0.001

        translate_axises = {'left':[translate_XY, 0, -translate_Z],
                            'right':[-translate_XY, 0, -translate_Z],
                            'top':[0, translate_XY, -translate_Z],
                            'down':[0, -translate_XY, -translate_Z]}

        translate_axis = translate_axises[model_param[section+1+2*section_count]]

        transform = Transform(registrationName='Translate'+str(section), Input=current_source)
        transform.Transform = 'Transform'
        transform.Transform.Translate = translate_axis

#        Hide3DWidgets(proxy=transform.Transform) # hiding frame
#        display = Show(transform, render_view, 'GeometryRepresentation')

        current_source = GetActiveSource() # translated geom
#        Hide(current_source, render_view)

        if section != section_count-1:
            d = int(model_param[0])*0.001
            l = [[d, 0.0, 0.0], [-d, 0.0, 0.0], [0.0, d, 0.0], [0.0, -d, 0.0]]
            for i,j in enumerate(l):
                if i == 0:
                    input_source = current_source
                else:
                    input_source = clip_source
                clip = Clip(registrationName='Clip'+str(section)+str(i), Input=input_source)
                clip.ClipType.Origin = j
                clip.ClipType.Normal = j
                clip.Invert = 1
                clip_source = GetActiveSource()

            cross_slice = Slice(registrationName='Slice'+str(section), Input=clip_source)
            cross_slice.SliceType = 'Plane'
            cross_slice.HyperTreeGridSlicer = 'Plane'
            cross_slice.SliceOffsetValues = [0.0]
            cross_slice.SliceType.Origin = [0.0, 0.0, 0.0]
            cross_slice.SliceType.Normal = [0.0, 0.0, 1.0]
            Hide3DWidgets(proxy=cross_slice.SliceType) # hiding frame
            slice_source = GetActiveSource()

            merge_blocks = MergeBlocks(registrationName='merge_blocks'+str(section), Input=slice_source)
            merge_source = GetActiveSource()

            ## Rendering the result
            display = Show(merge_source, render_view, 'UnstructuredGridRepresentation')
#            render_view.ResetCamera(True)
#            Render()

#            display = Show(cross_slice, render_view, 'GeometryRepresentation')
#            slice_source = GetActiveSource()
        else:
            openfoam_output.MeshRegions = ['patch/outlet']
            render_view.Update()
            Hide3DWidgets(proxy=transform.Transform)

            slice_source = GetActiveSource()

            merge_blocks = MergeBlocks(registrationName='merge_blocks'+str(section), Input=slice_source)
            merge_source = GetActiveSource()

            display = Show(merge_source, render_view, 'UnstructuredGridRepresentation')

        #render_view.ResetCamera(True)
        #Render()

        ## Taking screenshots
        ### Flow velocity distribution
        u_values = []
        u_ranges = {'X':0, 'Y':1, 'Z':2}

        for u in ['Magnitude', 'X', 'Y', 'Z']:
            ColorBy(display, ('POINTS', 'U', u))
            display.RescaleTransferFunctionToDataRange(True, False)
            if u != 'Magnitude':
                for i,j in enumerate(['_min', '_max']):
                    value = openfoam_output.GetPointDataInformation().GetArray('U').GetRange(u_ranges[u])[i]
                    u_values.append(value)
                    data['s'+str(section+1)+'-U'+u+j].append(value)
            SaveScreenshot(os.path.join(screenshot_path, 's'+str(section+1)+'-U'+u+'.png'),
                           render_view,
                           ImageResolution=[512, 512],
                           OverrideColorPalette='WhiteBackground',
                           TransparentBackground=1)

        data['s'+str(section+1)+'-UMagnitude_min'].append(min(u_values))
        data['s'+str(section+1)+'-UMagnitude_max'].append(max(u_values))

        ### Pressure distribution
        ColorBy(display, ('POINTS', 'p'))
        display.RescaleTransferFunctionToDataRange(True, False)
        data['s'+str(section+1)+'-P_min'].append(openfoam_output.GetPointDataInformation().GetArray('p').GetRange()[0])
        data['s'+str(section+1)+'-P_max'].append(openfoam_output.GetPointDataInformation().GetArray('p').GetRange()[1])
        SaveScreenshot(os.path.join(screenshot_path, 's'+str(section+1)+'-P.png'),
                       render_view,
                       ImageResolution=[512, 512],
                       OverrideColorPalette='WhiteBackground',
                       TransparentBackground=1)

        if section != section_count-1:
            Hide(merge_source, render_view)
            Render()

    ResetSession()
    #UpdatePipeline()

df = pd.DataFrame(data)

df.to_csv(os.path.join(save_path, batch_name+'.csv'), index=False)